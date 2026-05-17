# 阿里云 Supabase CLI MCP Server

这是一个把 **阿里云 AnalyticDB Supabase CLI** 封装成 **MCP Server** 的项目。配置完成后，可以在 Trae 等支持 MCP 的客户端中直接调用阿里云 Supabase CLI 能力，例如查看项目、查询数据库表、执行 SQL、管理 Edge Functions、Storage、Auth 用户和 Secrets。

## 功能概览

- 支持通过 MCP 调用阿里云 Supabase CLI。
- 支持本地 `stdio` 模式，适合开发和调试。
- 支持 Docker `sse` 模式，适合部署到宝塔、云服务器或公网服务。
- Docker 镜像内自动安装阿里云版本 Supabase CLI `1.0.0`。
- 支持 SQL 查询、创建表、添加字段、插入数据、更新数据、删除数据。
- 支持 Docker Compose 和 Docker Run 两种启动方式。
- 支持 GitHub Actions 自动构建并推送 Docker 镜像。

## 文件说明

| 文件 | 说明 |
|------|------|
| `server.py` | MCP Server 主程序，封装 Supabase CLI 命令 |
| `Dockerfile` | Docker 镜像构建文件，包含 Python、MCP 依赖和阿里云 Supabase CLI |
| `docker-compose.yml` | Docker Compose 部署配置 |
| `.env.example` | 环境变量示例文件 |
| `.dockerignore` | Docker 构建忽略文件，避免 `.env` 等敏感文件进入镜像 |
| `.github/workflows/docker-publish.yml` | GitHub Actions 自动构建和推送 Docker 镜像 |

## 环境变量

复制 `.env.example` 为 `.env`，并填写真实配置：

```bash
cp .env.example .env
```

`.env` 示例：

```env
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_ACCESS_TOKEN=
ALIYUN_REGION_ID=cn-hangzhou
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_CLI_TIMEOUT=120
SUPABASE_CLI_MAX_TIMEOUT=600
MCP_PORT=8000
MCP_TRANSPORT=sse
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `ALIYUN_ACCESS_KEY_ID` | 是 | 阿里云 AccessKey ID |
| `ALIYUN_ACCESS_KEY_SECRET` | 是 | 阿里云 AccessKey Secret |
| `ALIYUN_ACCESS_TOKEN` | 否 | 临时访问令牌，没有可留空 |
| `ALIYUN_REGION_ID` | 是 | 默认地域，例如 `cn-hangzhou` |
| `SUPABASE_DB_PASSWORD` | 建议填写 | 数据库密码，`link`、`db query`、迁移等数据库操作会用到 |
| `SUPABASE_CLI_TIMEOUT` | 否 | 普通 CLI 命令超时时间，默认 `120` 秒 |
| `SUPABASE_CLI_MAX_TIMEOUT` | 否 | 最大超时时间，默认 `600` 秒 |
| `MCP_PORT` | 否 | SSE 服务端口，默认 `8000` |
| `MCP_TRANSPORT` | 否 | MCP 传输方式，本地一般用 `stdio`，Docker 一般用 `sse` |

## 两种使用方式

本项目建议区分 **本地版** 和 **Docker 版**：

| 版本 | 使用场景 | Trae 配置方式 | 是否适合上云 |
|------|----------|---------------|--------------|
| 本地版 | 本机开发、调试 MCP Server | `command` 启动 `server.py` | 不推荐 |
| Docker 版 | 宝塔、云服务器、公网访问 | `url` 连接 `/sse` | 推荐 |

## 本地版使用

本地版适合开发调试。Trae 会直接启动本机的 `server.py`，通过 `stdio` 和 MCP Server 通信。

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 准备 Supabase CLI

本地版需要系统能找到可执行的 `supabase` 命令。可以通过以下方式之一准备：

- 将阿里云版本 Supabase CLI 放到系统 `PATH`。
- 将可执行文件放到项目目录。
- Windows 本地如果没有阿里云 CLI，可以保持 Docker 容器运行，`server.py` 会尝试通过 `docker exec` 调用容器内的阿里云 Supabase CLI。

如果使用 Docker 容器内 CLI，容器名称默认是：

```text
aliyun-supabase-cli-mcp-aliyun-supabase-mcp-1
```

### 3. Trae 本地版配置

把下面配置添加到 Trae 的 MCP 配置中。路径示例：

```text
C:\Users\Administrator\AppData\Roaming\Trae CN\User\mcp.json
```

配置示例：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "e:\\360MoveData\\Users\\Administrator\\Desktop\\aliyun-supabase-cli-mcp",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "ALIYUN_ACCESS_KEY_ID": "your-access-key-id",
        "ALIYUN_ACCESS_KEY_SECRET": "your-access-key-secret",
        "ALIYUN_ACCESS_TOKEN": "",
        "ALIYUN_REGION_ID": "cn-hangzhou",
        "SUPABASE_DB_PASSWORD": "your-db-password",
        "SUPABASE_CLI_TIMEOUT": "120",
        "SUPABASE_CLI_MAX_TIMEOUT": "600"
      }
    }
  }
}
```

配置后刷新 Trae MCP 连接，或重启 Trae。

## Docker 版使用

Docker 版适合正式部署到宝塔、云服务器或局域网服务器。容器启动后会暴露 SSE 地址，Trae 通过 URL 连接。

### 1. 上传项目

把项目上传到服务器目录，例如：

```bash
/www/wwwroot/aliyun-supabase-cli-mcp
```

进入项目目录：

```bash
cd /www/wwwroot/aliyun-supabase-cli-mcp
```

### 2. 创建 `.env`

```bash
cp .env.example .env
```

编辑 `.env`：

```env
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_ACCESS_TOKEN=
ALIYUN_REGION_ID=cn-hangzhou
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_CLI_TIMEOUT=120
SUPABASE_CLI_MAX_TIMEOUT=600
MCP_PORT=8000
MCP_TRANSPORT=sse
```

### 3. Docker Compose 启动

推荐使用 Docker Compose：

```bash
docker compose up -d --build
```

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

### 4. Docker Run 启动

如果不用 Docker Compose，可以手动构建和启动：

```bash
docker build -t aliyun-supabase-mcp:latest .
docker run -d \
  --name aliyun-supabase-mcp \
  --restart unless-stopped \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/workspace:/workspace \
  aliyun-supabase-mcp:latest
```

### 5. 宝塔 Docker 面板一键部署

宝塔面板内置 Docker 管理，可以直接拉取镜像创建容器。以下是详细步骤：

#### 步骤 1：上传项目并构建镜像

先把项目上传到服务器，例如：

```bash
/www/wwwroot/aliyun-supabase-cli-mcp
```

在服务器终端执行：

```bash
cd /www/wwwroot/aliyun-supabase-cli-mcp
docker build -t aliyun-supabase-mcp:latest .
```

等待构建完成（约 1-2 分钟）。

#### 步骤 2：在宝塔 Docker 面板创建容器

打开宝塔面板 → Docker → 容器 → 添加容器：

| 配置项 | 填写内容 | 说明 |
|--------|----------|------|
| **容器名称** | `aliyun-supabase-mcp` | 自定义名称 |
| **镜像** | `aliyun-supabase-mcp:latest` | 选择刚才构建的镜像 |
| **端口映射** | `8000:8000` | 左边是服务器端口，右边是容器端口 |
| **环境变量** | 见下方表格 | 必须全部填写 |
| **挂载目录** | `/www/wwwroot/aliyun-supabase-cli-mcp/workspace:/workspace` | 可选 |
| **自动重启** | 开启 | 推荐 |
| **entrypoint** | 留空 | 正常不需要填 |
| **command** | 留空 | 正常不需要填 |

#### 步骤 3：环境变量配置

在宝塔容器配置的"环境变量"区域，逐条添加：

| 变量名 | 示例值 | 必填 |
|--------|--------|------|
| `ALIYUN_ACCESS_KEY_ID` | `LTAI5t...` | 是 |
| `ALIYUN_ACCESS_KEY_SECRET` | `f9eDSf...` | 是 |
| `ALIYUN_ACCESS_TOKEN` | 留空 | 否 |
| `ALIYUN_REGION_ID` | `cn-hangzhou` | 是 |
| `SUPABASE_DB_PASSWORD` | `Xq+!Dq...` | 建议填 |
| `SUPABASE_CLI_TIMEOUT` | `120` | 否 |
| `SUPABASE_CLI_MAX_TIMEOUT` | `600` | 否 |
| `MCP_PORT` | `8000` | 否 |
| `MCP_TRANSPORT` | `sse` | 否 |

#### 步骤 4：启动容器

配置完成后点击"提交"，宝塔会自动创建并启动容器。

#### 步骤 5：验证部署成功

在服务器终端执行：

```bash
curl -i http://127.0.0.1:8000/sse
```

正常响应应包含：

```text
HTTP/1.1 200 OK
content-type: text/event-stream; charset=utf-8
```

如果看到以上内容，说明 MCP 服务已正常运行。

#### 步骤 6：Trae 连接

在本地 Trae 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "url": "http://服务器IP:8000/sse"
    }
  }
}
```

刷新 Trae MCP 连接，即可使用。

---

### 宝塔部署常见问题

#### 问题 1：更新容器时报 `no command specified`

**原因**：宝塔在创建新容器时没有继承镜像的 `ENTRYPOINT`

**解决方案**：在容器配置里显式填写：

| 字段 | 值 |
|------|----|
| `entrypoint` | `python` |
| `command` | `/app/server.py` |

#### 问题 2：容器启动后立即退出

**排查步骤**：
1. 查看容器日志（宝塔 Docker 面板 → 容器 → 日志）
2. 确认环境变量是否完整
3. 确认端口 8000 没有被其他服务占用

#### 问题 3：Trae 连接报 `SSE error: Invalid content type`

**原因**：URL 格式不对

**解决方案**：
- 使用完整地址：`http://服务器IP:8000/sse`
- 必须包含 `http://`
- 必须以 `/sse` 结尾
- 不要只写 `服务器IP:8000`

#### 问题 4：服务器防火墙拦截

**解决方案**：
- 在宝塔安全面板开放 8000 端口
- 或在云服务器控制台开放安全组 8000 端口

---

### 部署后就能直接使用吗？

**不是的**，部署后还需要：

1. **验证服务正常**：在服务器上 `curl http://127.0.0.1:8000/sse`
2. **开放端口**：确保服务器防火墙/安全组开放 8000
3. **配置 Trae**：在本地 Trae 添加 `url` 配置
4. **刷新连接**：刷新 Trae MCP 或重启 Trae

---

### 为什么早上部署不行？

可能的原因：

1. **环境变量没填完整**：`ALIYUN_ACCESS_KEY_ID`、`ALIYUN_ACCESS_KEY_SECRET`、`ALIYUN_REGION_ID` 必须填写
2. **端口没开放**：服务器防火墙或安全组没有开放 8000
3. **容器启动失败**：查看容器日志确认错误
4. **Trae 配置错误**：使用了 `command` 方式而不是 `url` 方式
5. **URL 格式错误**：没有写完整地址 `http://服务器IP:8000/sse`
6. **镜像构建失败**：没有先在服务器上执行 `docker build`

## Trae 连接 Docker 版

Docker 容器启动后，Trae 使用 `url` 方式连接服务器：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "url": "http://服务器IP:8000/sse"
    }
  }
}
```

如果使用域名和 HTTPS：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "url": "https://你的域名/sse"
    }
  }
}
```

注意：

- 必须包含 `http://` 或 `https://`。
- 必须以 `/sse` 结尾。
- 不要只写 `服务器IP:8000`。
- 不要把本地版的 `command` 配置用于远程服务器。

## 服务器测试

容器启动后，在服务器执行：

```bash
curl -i http://127.0.0.1:8000/sse
```

正常响应应包含：

```text
HTTP/1.1 200 OK
content-type: text/event-stream; charset=utf-8
```

也可以从本地电脑测试公网地址：

```bash
curl -i http://服务器IP:8000/sse
```

访问根路径 `/` 返回 `404` 是正常的，MCP 服务入口是 `/sse`。

## Nginx 反向代理

如果通过宝塔网站或 Nginx 反向代理访问 MCP，建议同时代理 `/sse` 和 `/messages/`。

```nginx
location /sse {
    proxy_pass http://127.0.0.1:8000/sse;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 3600;
}

location /messages/ {
    proxy_pass http://127.0.0.1:8000/messages/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 3600;
}
```

Trae 连接域名时使用：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "url": "https://你的域名/sse"
    }
  }
}
```

## 常用 MCP 工具

| 工具 | 说明 |
|------|------|
| `list_projects` | 查看 Supabase 项目列表 |
| `show_project` | 查看项目详情 |
| `get_project_api_keys` | 查看项目 API Keys |
| `list_regions` | 查看可用地域 |
| `list_tables` | 查看数据库表 |
| `list_columns` | 查看表字段 |
| `db_query` | 执行 SQL |
| `list_auth_users` | 查看 Auth 用户 |
| `list_storage_buckets` | 查看 Storage Buckets |
| `list_functions` | 查看 Edge Functions |
| `list_secrets` | 查看 Secrets |
| `supabase_cli` | 直接执行允许范围内的 Supabase CLI 命令 |

## SQL 使用示例

查询数据：

```json
{
  "sql": "SELECT * FROM public.user_profiles LIMIT 10",
  "linked": true
}
```

创建表：

```json
{
  "sql": "CREATE TABLE IF NOT EXISTS public.test_table (id SERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT NOW())",
  "linked": true
}
```

添加字段：

```json
{
  "sql": "ALTER TABLE public.test_table ADD COLUMN IF NOT EXISTS description TEXT",
  "linked": true
}
```

插入数据：

```json
{
  "sql": "INSERT INTO public.test_table (name, description) VALUES ('test_item', 'This is a test')",
  "linked": true
}
```

删除测试表：

```json
{
  "sql": "DROP TABLE IF EXISTS public.test_table",
  "linked": true
}
```

## GitHub Actions 自动构建 Docker 镜像

仓库提供 `.github/workflows/docker-publish.yml`。推送到 `main` 或 `master` 分支时，会自动构建 Docker 镜像并推送到 Docker Hub。

需要在 GitHub Secrets 配置：

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`

推送后的镜像标签：

```text
DOCKER_HUB_USERNAME/aliyun-supabase-mcp:latest
DOCKER_HUB_USERNAME/aliyun-supabase-mcp:1.1
```

服务器可以直接拉取镜像：

```bash
docker pull DOCKER_HUB_USERNAME/aliyun-supabase-mcp:1.1
```

## 常见问题

### Trae 报 `SSE error: Invalid content type`

常见原因是 URL 写错。请确认：

- 使用完整地址：`http://服务器IP:8000/sse`
- 地址包含 `http://` 或 `https://`
- 地址以 `/sse` 结尾
- 如果经过 Nginx，确认没有把 SSE 响应改成 HTML 或 JSON

### 访问 `/` 返回 404

正常现象。这个服务不是网页站点，没有首页路由。MCP 入口是：

```text
http://服务器IP:8000/sse
```

### 宝塔更新容器时报 `no command specified`

说明宝塔没有继承镜像默认启动命令。可以填写：

```text
entrypoint = python
command = /app/server.py
```

### SQL 能不能创建表、添加字段、插入数据

可以。只要项目已经 link 或 SQL 命令携带正确连接参数，就可以通过 `db_query` 执行：

- `CREATE TABLE`
- `ALTER TABLE ADD COLUMN`
- `INSERT`
- `SELECT`
- `UPDATE`
- `DELETE`
- `DROP TABLE`

### 服务器防火墙需要开放什么端口

如果直接用 IP 访问，需要开放 `8000` 端口。如果使用 Nginx 反代并配置 HTTPS，只需要开放 `80` 和 `443`。

### `.env` 能不能提交到 Git

不能。`.env` 包含阿里云 AccessKey 和数据库密码，必须保留在本地或服务器，不要提交到仓库。

## 安全建议

- 不要把 `ALIYUN_ACCESS_KEY_SECRET`、`SUPABASE_DB_PASSWORD`、API Key 截图发到公开场景。
- 如果密钥已经暴露，建议立即在阿里云控制台轮换 AccessKey。
- 生产环境建议通过 Nginx + HTTPS 暴露 MCP 服务。
- 如果 MCP 服务对公网开放，建议限制访问来源 IP 或增加网关鉴权。
