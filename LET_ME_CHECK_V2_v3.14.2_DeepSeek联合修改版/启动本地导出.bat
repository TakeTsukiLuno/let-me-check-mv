@echo off
rem LET ME CHECK v3.14.2 launcher - CRLF, persistent diagnostic console
if /i not "%~1"=="--run" (
  start "LET ME CHECK v3.14.2 - Local FFmpeg" "%ComSpec%" /k ""%~f0" --run"
  exit /b
)
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title LET ME CHECK v3.14.2 - Local FFmpeg Export
set "LOG=%~dp0启动诊断日志.txt"
echo LET ME CHECK v3.14.2 launcher started > "%LOG%"
echo Folder: %CD% >> "%LOG%"
echo ============================================================
echo LET ME CHECK V2 v3.14.2 - 本机 FFmpeg 逐帧导出
echo 工作目录：%CD%
echo 诊断日志：%LOG%
echo ============================================================
echo 正在检查 Python 3...
where py >> "%LOG%" 2>&1
where py >nul 2>&1
if not errorlevel 1 goto use_py
where python >> "%LOG%" 2>&1
where python >nul 2>&1
if not errorlevel 1 goto use_python
echo [错误] 找不到 Python 3。 >> "%LOG%"
echo [错误] 找不到可用的 Python 3。
echo 请安装 Python 3，并在安装时勾选 Add Python to PATH。
goto finish

:use_py
echo 使用 Python Launcher：py -3
echo Using py -3 >> "%LOG%"
py -3 --version
echo Version check exit code: %ERRORLEVEL% >> "%LOG%"
py -3 --version
if errorlevel 1 goto try_python
echo 正在启动服务；请保持此窗口打开。
echo Running server with py -3 >> "%LOG%"
py -3 -u "LET_ME_CHECK_V2_v3.14.2_render_local_ffmpeg.py"
set "RC=%ERRORLEVEL%"
goto finished_server

:try_python
where python >nul 2>&1
if errorlevel 1 goto no_python
goto use_python

:use_python
echo 使用 Python：python
echo Using python >> "%LOG%"
python --version
if errorlevel 1 goto no_python
echo 正在启动服务；请保持此窗口打开。
echo Running server with python >> "%LOG%"
python -u "LET_ME_CHECK_V2_v3.14.2_render_local_ffmpeg.py"
set "RC=%ERRORLEVEL%"
goto finished_server

:no_python
echo [错误] Python 3 无法运行。 >> "%LOG%"
echo [错误] Python 3 无法运行。请查看诊断日志：%LOG%
goto finish

:finished_server
echo Server exit code: %RC% >> "%LOG%"
echo.
echo ============================================================
echo 本地服务已退出，退出代码：%RC%
echo 诊断日志：%LOG%
echo 若有 Traceback，请截图并发送给龙娘。
echo ============================================================

:finish
echo.
echo 此窗口会保持打开。按任意键关闭。
pause >nul
endlocal
