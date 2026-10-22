#!/usr/bin/env python3
# LET ME CHECK V2 v3.14.2 local FFmpeg bridge; v3.14.1 renderer baseline plus Scheme B audio-tail fix.
# Serves index.html on loopback and pipes concatenated PNG frames to the user's local FFmpeg.
from __future__ import annotations
import json, os, re, shutil, subprocess, tempfile, threading, time, secrets, webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "exports"
OUT_DIR.mkdir(exist_ok=True)
TOKEN = secrets.token_urlsafe(24)
LOCK = threading.RLock()
JOB = None


def json_bytes(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def ffmpeg_executable(value: str) -> str:
    value = (value or "ffmpeg").strip().strip('"').strip("'")
    candidate = Path(value).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    found = shutil.which(value)
    if found:
        return found
    raise FileNotFoundError(
        f"找不到 FFmpeg：{value}。请在页面中填写 ffmpeg.exe 的完整路径，或把 FFmpeg 加入 PATH。"
    )


def status_snapshot():
    global JOB
    with LOCK:
        if not JOB:
            return {"status": "idle"}
        proc = JOB.get("proc")
        if proc is not None:
            rc = proc.poll()
            if rc is not None and JOB["status"] not in ("cancelled", "error", "done"):
                JOB["returncode"] = rc
                if rc == 0 and JOB["output"].exists() and JOB["output"].stat().st_size > 0:
                    JOB["status"] = "done"
                else:
                    JOB["status"] = "error"
                    JOB["error"] = tail_log(JOB.get("log")) or f"FFmpeg 退出码：{rc}"
                cleanup_temp(JOB)
        return {
            "status": JOB.get("status", "idle"),
            "output": JOB["output"].name if JOB.get("output") else "",
            "path": str(JOB["output"].resolve()) if JOB.get("output") else "",
            "error": JOB.get("error", ""),
            "returncode": JOB.get("returncode"),
        }


def tail_log(path):
    try:
        data = Path(path).read_text(encoding="utf-8", errors="replace")
        return data[-2500:].strip()
    except Exception:
        return ""


def cleanup_temp(job):
    td = job.get("tempdir")
    if td and Path(td).exists():
        shutil.rmtree(td, ignore_errors=True)
        job["tempdir"] = None


class Handler(BaseHTTPRequestHandler):
    server_version = "LMC-Local-FFmpeg/1.0"

    def log_message(self, fmt, *args):
        print("[local-export] " + (fmt % args))

    def send_json(self, status, obj):
        body = json_bytes(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            try:
                page = (BASE / "index.html").read_text(encoding="utf-8")
                page = page.replace("__LMC_LOCAL_TOKEN__", TOKEN)
                body = page.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/status":
            self.send_json(200, status_snapshot())
            return
        if parsed.path == "/favicon.ico":
            self.send_response(204); self.end_headers(); return
        self.send_json(404, {"ok": False, "error": "Not found"})

    def _authorized(self):
        if self.headers.get("X-LMC-Token", "") != TOKEN:
            self.send_json(403, {"ok": False, "error": "本地导出会话无效。请从启动器打开页面，不要直接打开 HTML 文件。"})
            return False
        return True

    def _read_body_to_file(self, path):
        remaining = int(self.headers.get("Content-Length", "0"))
        if remaining <= 0:
            raise ValueError("请求体为空")
        with open(path, "wb") as f:
            while remaining:
                chunk = self.rfile.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ConnectionError("上传数据不完整")
                f.write(chunk)
                remaining -= len(chunk)

    def do_POST(self):
        global JOB
        parsed = urlparse(self.path)
        if not self._authorized():
            return
        if parsed.path == "/api/start":
            qs = parse_qs(parsed.query)
            with LOCK:
                if JOB and JOB.get("proc") is not None and JOB["proc"].poll() is None:
                    self.send_json(409, {"ok": False, "error": "已有导出任务正在运行。请先完成或取消它。"}); return
                try:
                    exe = ffmpeg_executable(qs.get("ffmpeg", ["ffmpeg"])[0])
                    crf = int(qs.get("crf", ["18"])[0]); crf = max(14, min(23, crf))
                    codec = qs.get("codec", ["aac"])[0].lower()
                    if codec not in ("aac", "alac"):
                        codec = "aac"
                    ext = qs.get("audioExt", ["wav"])[0].lower()
                    if not re.fullmatch(r"[a-z0-9]{1,8}", ext): ext = "wav"
                    tempdir = tempfile.mkdtemp(prefix="lmc_v3142_")
                    audio_path = Path(tempdir) / f"source.{ext}"
                    self._read_body_to_file(audio_path)
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output = OUT_DIR / f"LET_ME_CHECK_V2_v3.14.2_1080p30_{stamp}.mp4"
                    log_path = Path(tempdir) / "ffmpeg.log"
                    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
                           "-f", "image2pipe", "-framerate", "30", "-vcodec", "png", "-i", "pipe:0",
                           "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0",
                           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                           "-pix_fmt", "yuv420p", "-r", "30"]
                    if codec == "alac": cmd += ["-c:a", "alac"]
                    else: cmd += ["-c:a", "aac", "-b:a", "320k"]
                    cmd += ["-af", "apad", "-movflags", "+faststart", "-t", "274.866667", str(output)]
                    log = open(log_path, "wb")
                    try:
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log, bufsize=0)
                    finally:
                        log.close()
                    JOB = {"proc": proc, "output": output, "tempdir": tempdir, "log": log_path,
                           "status": "running", "returncode": None, "error": "", "started": time.time(), "command": cmd}
                    self.send_json(200, {"ok": True, "status": "running", "output": output.name})
                except Exception as exc:
                    try:
                        if 'tempdir' in locals(): shutil.rmtree(tempdir, ignore_errors=True)
                    except Exception: pass
                    self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/frames":
            with LOCK:
                if not JOB or JOB.get("status") != "running" or not JOB.get("proc"):
                    self.send_json(409, {"ok": False, "error": "FFmpeg 导出进程未运行。"}); return
                proc = JOB["proc"]
            try:
                remaining = int(self.headers.get("Content-Length", "0"))
                if remaining <= 0: raise ValueError("帧数据为空")
                while remaining:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk: raise ConnectionError("帧数据上传不完整")
                    view = memoryview(chunk)
                    sent = 0
                    while sent < len(view):
                        written = proc.stdin.write(view[sent:])
                        if not written:
                            raise BrokenPipeError("FFmpeg 管道已关闭")
                        sent += written
                    remaining -= len(chunk)
                proc.stdin.flush()
                self.send_json(200, {"ok": True, "frames": self.headers.get("X-Frame-Count", "")})
            except (BrokenPipeError, OSError, Exception) as exc:
                with LOCK:
                    if JOB: JOB["status"] = "error"; JOB["error"] = tail_log(JOB.get("log")) or str(exc)
                self.send_json(500, {"ok": False, "error": "写入 FFmpeg 失败：" + (tail_log(JOB.get("log")) or str(exc))})
            return
        if parsed.path == "/api/finish":
            with LOCK:
                if not JOB or JOB.get("status") != "running":
                    self.send_json(409, {"ok": False, "error": "当前没有可结束的导出任务。"}); return
                try:
                    JOB["proc"].stdin.close()
                    JOB["status"] = "finishing"
                except Exception as exc:
                    JOB["status"] = "error"; JOB["error"] = str(exc)
                    self.send_json(500, {"ok": False, "error": str(exc)}); return
            self.send_json(200, {"ok": True, "status": "finishing"}); return
        if parsed.path == "/api/cancel":
            with LOCK:
                if JOB and JOB.get("proc") and JOB["proc"].poll() is None:
                    try:
                        JOB["proc"].stdin.close()
                    except Exception: pass
                    JOB["proc"].terminate()
                    try: JOB["proc"].wait(timeout=3)
                    except subprocess.TimeoutExpired: JOB["proc"].kill(); JOB["proc"].wait(timeout=3)
                    JOB["status"] = "cancelled"
                    try: JOB["output"].unlink(missing_ok=True)
                    except Exception: pass
                    cleanup_temp(JOB)
            self.send_json(200, {"ok": True, "status": "cancelled"}); return
        self.send_json(404, {"ok": False, "error": "Not found"})


def main():
    httpd = None
    for port in range(8765, 8780):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        raise RuntimeError("本地端口 8765–8779 都被占用，请关闭其他导出器后重试。")
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print("=" * 62)
    print("LET ME CHECK V2 v3.14.2 · 原导演执行版 + 本机逐帧 FFmpeg 输出")
    print("页面：", url)
    print("输出目录：", OUT_DIR.resolve())
    print("请保持此窗口打开。关闭窗口会停止本地服务。")
    print("=" * 62)
    try: webbrowser.open(url)
    except Exception: pass
    try: httpd.serve_forever()
    except KeyboardInterrupt: print("\n已关闭本地导出服务。")
    finally: httpd.server_close()

if __name__ == "__main__":
    main()
