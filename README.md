# Aliyun Supabase CLI MCP Server

这个项目把阿里云 AnalyticDB Supabase CLI 封装成 MCP 工具，并提供 Docker 化部署文件，适合部署到服务器后由支持 MCP 的客户端通过容器 stdio 调用。

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

## MCP 客户端配置示例

使用 Docker 运行 stdio MCP 服务：

```json
{
  "mcpServers": {
    "aliyun-supabase": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/.env",
        "-v",
        "/absolute/path/to/workspace:/workspace",
        "aliyun-supabase-mcp:latest"
      ]
    }
  }
}
```

服务器部署时，把 `/absolute/path/to/.env` 和 `/absolute/path/to/workspace` 替换成服务器上的绝对路径。

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

```bash
docker compose build
docker compose run --rm aliyun-supabase-mcp
```

MCP 的 stdio 模式需要由 MCP 客户端启动容器并保持标准输入输出连接；不要把它当成普通 HTTP 服务暴露端口。

## 安全建议

- 不要把 `.env` 提交到代码仓库
- 服务器上限制 `.env` 文件权限
- 删除项目、重置密码、设置密钥等高风险操作建议只授予可信客户端使用
- `supabase_cli` 只允许文档中的 Supabase 根命令，避免任意系统命令执行
