# LET ME CHECK — v3.13 MV 定稿工程

> 状态：**2026-10-21 暂时定稿**，保留导演后续修订空间。由导演确认为暂时定稿；仓库当前为 Public，公开资源的使用与转载请遵守相应授权。

## 成片规格

- 98 镜头、双语字幕、1920×1080、30 fps、8246 帧。
- 发布版：`release/LET_ME_CHECK_v3.13_1080p30_中英字幕.mp4`（H.264/AAC）。
- 归档版：`release/LET_ME_CHECK_v3.13_1080p30_FLAC24bit.mkv`（H.264/FLAC 48 kHz 24 bit）。
- 工程音轨：`assets/audio/MV_MASTER_48k_24bit_-14LUFS.wav`，未先转换为 MP3。
- 曲末：`ONE LAST THING?` 272.621–273.334 秒；S097 272.358–273.334；S098 273.334–274.848。

## 文件夹

- `source/`：**最终可运行 HTML 程序**、可读 JS 副本、98 镜头/歌词/双语字幕 JSON、最终程序原样内嵌的 WebP 素材及索引。HTML 为正式单文件入口（打开即可以预览；其中音轨是旧预览内嵌音乐，成片使用新 WAV）。
- `assets/`：导演原始 CG、半身原始 PNG、较早 CG 原始版本、角色三视图参考，以及 Suno WAV 和正式 MV WAV 母带。
- `history/`：版本沿革、原始逐版执行记录、早期 MP3 母带处理报告、审片抽帧汇总及成片 QA；不是对所有历史对话的逐字存档。
- `release/`：正式视频、无损音轨归档视频、98 镜头总览。
- `tools/`：供后续检查、提取和对齐的辅助脚本。
- `SHA256SUMS.txt`：校验文件（生成时已对最终工程资源作摘要）。

## 程序与音频的区别

最终 HTML 的 `built_in_audio` 仍是分镜预览时内嵌的旧版音轨。**正式导出 MP4/MKV 使用 `assets/audio/MV_MASTER_48k_24bit_-14LUFS.wav`**，不能误以为 HTML 内嵌音频是最终母带。影片截图、工程和声轨采用相同锁版时码，不能将预览 MP3 混用为正式源母带。

## 从工程恢复

1. 在浏览器中打开 `source/LET_ME_CHECK_v3.13_交互工程_含预览音频.html`，可以查看完整分镜、字幕和时间轴。
2. `source/storyboard_98shots_lyrics_subtitles.json` 是已整理的镜头与双语歌词数据；`source/player_runtime.js` 是同一 HTML 中提取的执行脚本，方便检索代码。
3. `source/embedded_assets/` 是从**最终 HTML 原样提取**的显示用图片，原始分辨率 CG 在 `assets/`。
4. 若重制视频，必须以 30 fps 的绝对帧时间 `(frame_index + 0.5)/30` 绘制；使用正式 WAV 合入视频、末端按画面帧长补静音。详情参考 `history/FINAL_QA_REPORT.md`。
5. 现阶段归档了真实的最终 HTML 程序与所有可核实素材；**并不包含此前渲染机器上完整的浏览器/FFmpeg自动化执行环境**，不宣称一键重现原始 MP4 编码比特级一致。

## 音频报告说明

`history/original_logs/音频母带报告_早期MP3处理.md` 记录的是较早 MP3 处理链及 A/B 方案，**不是当前最终 WAV 母带的完整制作报告**；最终采用的 WAV 以实际文件和 `history/FINAL_QA_REPORT.md` 为准。

## GitHub 存储建议

GitHub 普通 Git 文件上限是 100 MiB，最终 MP4/MKV 和母带 WAV 等大文件不适合直接用 Contents API 上传。请使用 **Git LFS** 或 GitHub Release 资产管理二进制，并在普通 Git 中保存代码、记录、哈希和清单。当前仓库为 Public。若不希望母带/CG/源文件公开，请先在 GitHub 仓库设置里调整可见性；此归档不会自动更改仓库设置。

### 推荐 Git LFS

```sh
git lfs install
git lfs track "*.mp4" "*.mkv" "*.wav" "*.zip"
git add .gitattributes
git add source assets history release tools README.md SHA256SUMS.txt
git commit -m "Archive LET ME CHECK MV v3.13 final"
git push origin main
```

GitHub LFS 的账户储存、带宽和大小限制需以实际账号权限为准。