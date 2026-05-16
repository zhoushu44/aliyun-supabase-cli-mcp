# Changelog

## 1.0 - 2026-05-17

### Added

- 新增阿里云 AnalyticDB Supabase CLI 的 MCP Server 封装。
- 新增 Dockerfile，镜像内自动安装阿里云 Supabase CLI `1.0.0`。
- 新增 SSE 服务模式，默认监听 `0.0.0.0:8000`。
- 新增 GitHub Actions 自动构建与推送 Docker Hub 镜像。
- 新增 Docker Hub 镜像双标签推送：`1.0` 和 `latest`。
- 新增 `.env.example`，集中管理阿里云凭证、数据库密码和 MCP 服务端口。
- 新增 `.dockerignore`，保持排除 `.env`，避免密钥进入镜像构建上下文。

### Changed

- 数据库相关 MCP 工具的 `password` 参数改为可选，默认读取 `SUPABASE_DB_PASSWORD`。
- GitHub Actions 只在 `main` 分支 push 时触发构建与推送。
- 镜像推送统一由 GitHub Actions 完成，本地无需执行 `docker push`。

### Security

- MCP 执行入口仅允许阿里云 Supabase CLI 文档中的根命令，避免任意系统命令执行。
- 命令输出会对常见敏感环境变量进行脱敏。
