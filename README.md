# Aliyun Supabase CLI MCP Server

这个项目把阿里云 AnalyticDB Supabase CLI 封装成 MCP 工具，并提供 Docker 化部署与 GitHub Actions 自动构建推送配置，适合部署到服务器后通过 SSE 方式访问。

<https://help.aliyun.com/zh/analyticdb/analyticdb-for-postgresql/supabase-cli-usage-guide?spm=a2c4g.11186623.help-menu-92664.d_2_1_7.21524d4eb5uEls&scm=20140722.H_3029803._.OR_help-T_cn~zh-V_1>

## 功能范围

- 项目管理：列表、详情、API Key、创建、删除、IP 白名单、重置数据库密码
- 基础设施：区域、VPC、交换机查询
- 项目链接：link、unlink
- 数据库：表、列、索引、扩展、SQL 查询、pull、push、dump
- 迁移：列表、up、新建迁移
- Edge Functions：列表、部署、调用
- Secrets：列表、设置、删除
- Auth：用户列表、详情、创建
- Storage：Bucket 列表、创建、删除
- 代码生成：数据库类型生成
- 通用入口：`supabase_cli` 可执行文档中的其他允许根命令

## 本地构建

```bash
docker compose build
```

## 环境变量

复制示例配置并填写自己的凭证：

```bash
cp .env.example .env
```

必填项：

- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`

可选项：

- `ALIYUN_ACCESS_TOKEN`：格式为 `AccessKeyId|AccessKeySecret`
- `ALIYUN_REGION_ID`：默认 `cn-hangzhou`
- `SUPABASE_DB_PASSWORD`：默认数据库密码，部分命令仍建议显式传参
- `SUPABASE_CLI_TIMEOUT`：单次命令默认超时时间
- `SUPABASE_CLI_MAX_TIMEOUT`：单次命令最大超时时间
- `MCP_PORT`：服务端口，默认 `8000`
- `MCP_TRANSPORT`：默认 `sse`

## MCP 客户端配置示例

服务默认监听 `0.0.0.0:8000`，Docker Compose 会映射到宿主机同端口。

```bash
docker compose up -d
```

远程 MCP 地址：

```text
http://服务器IP:8000/sse
```

如果你的客户端需要 JSON 配置，可以使用类似配置：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "url": "http://服务器IP:8000/sse"
    }
  }
}
```

## GitHub Actions 自动推送

已提供 `.github/workflows/docker-publish.yml`，push 到 `main` 分支会自动构建同一个 Docker 镜像，并推送到 Docker Hub。镜像推送只由 GitHub Actions 完成，本地不需要执行任何 `docker push`。

仓库 Secrets 需要配置：

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`

推送后的镜像名：

```text
DOCKER_HUB_USERNAME/aliyun-supabase-mcp:latest
DOCKER_HUB_USERNAME/aliyun-supabase-mcp:1.0
```

`latest` 和 `1.0` 指向同一次 GitHub Actions 构建产物。

## 常用工具调用示例

通用 CLI：

```json
{
  "args": ["projects", "list"]
}
```

查询表：

```json
{
  "project_ref": "sbp-xxxxxxx"
}
```

执行 SQL：

```json
{
  "sql": "SELECT * FROM public.inventory LIMIT 10",
  "linked": true
}
```

## 服务器部署

从 Docker Hub 拉取 GitHub Actions 推送的镜像：

```bash
docker pull DOCKER_HUB_USERNAME/aliyun-supabase-mcp:1.0
```

运行服务：

```bash
docker run -d \
  --name aliyun-supabase-mcp \
  --restart unless-stopped \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/workspace:/workspace \
  DOCKER_HUB_USERNAME/aliyun-supabase-mcp:1.0
```

如果需要在服务器上自行构建，也可以使用：

```bash
docker compose build
docker compose up -d
```

服务监听地址为 `0.0.0.0`，默认端口 `8000`。

## 安全建议

- 不要把 `.env` 提交到代码仓库
- `.dockerignore` 已排除 `.env`，避免真实密钥进入 Docker 构建上下文
- 服务器上限制 `.env` 文件权限
- 删除项目、重置密码、设置密钥等高风险操作建议只授予可信客户端使用
- `supabase_cli` 只允许文档中的 Supabase 根命令，避免任意系统命令执行
