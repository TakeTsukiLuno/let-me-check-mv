# Codex / GitHub 上传指引（公开、无音频）

仓库：https://github.com/TakeTsukiLuno/let-me-check-mv（Public）。

仅上传 ①定稿工程/修改记录、②原始美术、⑦ 98镜头总览。
不要上传 ③Suno原曲、④正式母带、⑤正式 MP4、⑥归档 MKV。
旧①含 8.4 MB 的 MP3 Base64 音轨，**禁止上传旧①**；必须使用本次 ①无音频公开工程。

解压顺序：先②原始绘画素材，然后①无音频公开工程并覆盖同名根目录文件，最后将⑦存到 release/LET_ME_CHECK_98镜头审片总览.jpg。

在合并得到的 LET_ME_CHECK_v3.13_FINAL 下执行：
  python tools/verify_archive.py
期望 PASS。确认 HTML 源码内没有 `data:audio/mpeg;base64` 和 `id="built_in_audio"`。

**保留 GitHub 既有历史**：用 `git clone` 获取现有仓库，将需发布的文件拷贝进仓库，然后 `git add` 白名单路径；不要使用 `git init` + `git push --force` 覆盖旧提交。

仅 Git add：README.md, .gitignore, .gitattributes, SHA256SUMS.txt, source/, assets/CG_from_v2_9/, assets/character_reference/, assets/original_CG/, history/, tools/, release/LET_ME_CHECK_98镜头审片总览.jpg。

提交前必须检查 `git diff --cached --name-only`，确认没有 WAV、MP3、FLAC、AAC、MP4、MKV 或它们的 ZIP 包。还须确认 HTML 中无内嵌音频。

发布源文件为可选本地音频驱动的“静音预览程序”；内嵌图片和字体不会被变动。不要把本地音频路径写入仓库。
