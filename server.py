import os
import shlex
import subprocess
from typing import Any

from mcp.server.fastmcp import FastMCP


MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

mcp = FastMCP("aliyun-supabase-cli", host=MCP_HOST, port=MCP_PORT)

DEFAULT_TIMEOUT = int(os.getenv("SUPABASE_CLI_TIMEOUT", "120"))
MAX_TIMEOUT = int(os.getenv("SUPABASE_CLI_MAX_TIMEOUT", "600"))
SENSITIVE_ENV_NAMES = {
    "ALIYUN_ACCESS_KEY_ID",
    "ALIYUN_ACCESS_KEY_SECRET",
    "ALIYUN_ACCESS_TOKEN",
    "SUPABASE_DB_PASSWORD",
}
ALLOWED_ROOT_COMMANDS = {
    "projects",
    "infra",
    "link",
    "unlink",
    "db",
    "migration",
    "functions",
    "secrets",
    "auth",
    "storage",
    "gen",
}


def _db_password(password: str | None = None) -> str:
    resolved = password or os.getenv("SUPABASE_DB_PASSWORD")
    if not resolved:
        raise ValueError("需要提供数据库密码：传入 password，或在 .env 中设置 SUPABASE_DB_PASSWORD")
    return resolved


def _redact(value: str | None) -> str | None:
    if value is None:
        return None
    redacted = value
    for name in SENSITIVE_ENV_NAMES:
        secret = os.getenv(name)
        if secret:
            redacted = redacted.replace(secret, f"<{name}>")
    return redacted


def _get_supabase_path() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.name == "nt":
        local_path = os.path.join(script_dir, "supabase.exe")
    else:
        local_path = os.path.join(script_dir, "supabase")
    if os.path.isfile(local_path):
        return local_path
    return "supabase"


SUPABASE_PATH = _get_supabase_path()


def _run_supabase(args: list[str], timeout: int | None = None, cwd: str | None = None) -> dict[str, Any]:
    if not args:
        raise ValueError("args 不能为空")
    if args[0] not in ALLOWED_ROOT_COMMANDS:
        raise ValueError(f"不允许执行 supabase {args[0]}，允许的根命令为：{', '.join(sorted(ALLOWED_ROOT_COMMANDS))}")
    safe_timeout = min(timeout or DEFAULT_TIMEOUT, MAX_TIMEOUT)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_workdir = os.getenv("SUPABASE_WORKDIR") or script_dir
    
    if os.name == "nt" and not os.path.isfile(SUPABASE_PATH):
        container_name = os.getenv("SUPABASE_CONTAINER", "aliyun-supabase-cli-mcp-aliyun-supabase-mcp-1")
        cmd_args = ["docker", "exec", container_name, "supabase"] + args
    else:
        cmd_args = [SUPABASE_PATH] + args
    
    process = subprocess.run(
        cmd_args,
        cwd=cwd or default_workdir,
        text=True,
        capture_output=True,
        timeout=safe_timeout,
        check=False,
    )
    return {
        "command": "supabase " + " ".join(shlex.quote(arg) for arg in args),
        "exit_code": process.returncode,
        "stdout": _redact(process.stdout or ""),
        "stderr": _redact(process.stderr or ""),
    }


@mcp.tool()
def supabase_cli(args: list[str], timeout: int | None = None, cwd: str | None = None) -> dict[str, Any]:
    return _run_supabase(args=args, timeout=timeout, cwd=cwd)


@mcp.tool()
def list_projects() -> dict[str, Any]:
    return _run_supabase(["projects", "list"])


@mcp.tool()
def show_project(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["projects", "show", project_ref])


@mcp.tool()
def get_project_api_keys(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["projects", "api-keys", "--project-ref", project_ref])


@mcp.tool()
def create_project(name: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    return _run_supabase(["projects", "create", name, *(extra_args or [])], timeout=600)


@mcp.tool()
def delete_project(project_ref: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    return _run_supabase(["projects", "delete", project_ref, *(extra_args or [])], timeout=300)


@mcp.tool()
def update_ip_whitelist(project_ref: str, ip_list: str) -> dict[str, Any]:
    return _run_supabase(["projects", "ip-whitelist", project_ref, "--ip-list", ip_list])


@mcp.tool()
def reset_db_password(project_ref: str, password: str) -> dict[str, Any]:
    return _run_supabase(["projects", "reset-password", project_ref, "--password", password])


@mcp.tool()
def list_regions() -> dict[str, Any]:
    return _run_supabase(["infra", "regions"])


@mcp.tool()
def list_vpcs(region: str) -> dict[str, Any]:
    return _run_supabase(["infra", "vpcs", "--region", region])


@mcp.tool()
def list_vswitches(region: str, vpc_id: str, zone_id: str) -> dict[str, Any]:
    return _run_supabase(["infra", "vswitches", "--region", region, "--vpc-id", vpc_id, "--zone-id", zone_id])


@mcp.tool()
def link_project(project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["link", "--project-ref", project_ref, "--password", _db_password(password)])


@mcp.tool()
def unlink_project() -> dict[str, Any]:
    return _run_supabase(["unlink"])


@mcp.tool()
def list_tables(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["db", "tables", "list", "--project-ref", project_ref])


@mcp.tool()
def list_columns(project_ref: str, table: str) -> dict[str, Any]:
    return _run_supabase(["db", "columns", "list", "--project-ref", project_ref, "--table", table])


@mcp.tool()
def list_indexes(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["db", "indexes", "list", "--project-ref", project_ref])


@mcp.tool()
def list_extensions(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["db", "extensions", "list", "--project-ref", project_ref])


@mcp.tool()
def db_query(sql: str, project_ref: str | None = None, linked: bool = False) -> dict[str, Any]:
    args = ["db", "query", sql]
    if linked:
        args.append("--linked")
    if project_ref:
        args.extend(["--project-ref", project_ref])
    return _run_supabase(args)


@mcp.tool()
def db_pull(project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["db", "pull", "--project-ref", project_ref, "--password", _db_password(password)], timeout=300)


@mcp.tool()
def db_push(project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["db", "push", "--project-ref", project_ref, "--password", _db_password(password)], timeout=300)


@mcp.tool()
def db_dump(project_ref: str, password: str | None = None, file: str = "schema.sql") -> dict[str, Any]:
    return _run_supabase(["db", "dump", "--project-ref", project_ref, "--password", _db_password(password), "--file", file], timeout=300)


@mcp.tool()
def list_migrations(project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["migration", "list", "--project-ref", project_ref, "--password", _db_password(password)])


@mcp.tool()
def migration_up(project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["migration", "up", "--project-ref", project_ref, "--password", _db_password(password)], timeout=300)


@mcp.tool()
def new_migration(name: str) -> dict[str, Any]:
    return _run_supabase(["migration", "new", name])


@mcp.tool()
def list_functions(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["functions", "list", "--project-ref", project_ref])


@mcp.tool()
def deploy_function(slug: str, project_ref: str) -> dict[str, Any]:
    return _run_supabase(["functions", "deploy", slug, "--project-ref", project_ref], timeout=300)


@mcp.tool()
def invoke_function(slug: str, data: str | None = None, project_ref: str | None = None) -> dict[str, Any]:
    args = ["functions", "invoke", slug]
    if data:
        args.extend(["--data", data])
    if project_ref:
        args.extend(["--project-ref", project_ref])
    return _run_supabase(args)


@mcp.tool()
def list_secrets(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["secrets", "list", "--project-ref", project_ref])


@mcp.tool()
def set_secret(project_ref: str, name: str, value: str) -> dict[str, Any]:
    return _run_supabase(["secrets", "set", f"{name}={value}", "--project-ref", project_ref])


@mcp.tool()
def unset_secret(project_ref: str, name: str) -> dict[str, Any]:
    return _run_supabase(["secrets", "unset", name, "--project-ref", project_ref])


@mcp.tool()
def list_auth_users(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["auth", "users", "list", "--project-ref", project_ref])


@mcp.tool()
def get_auth_user(project_ref: str, user_id: str) -> dict[str, Any]:
    return _run_supabase(["auth", "users", "get", user_id, "--project-ref", project_ref])


@mcp.tool()
def create_auth_user(project_ref: str, email: str | None = None, phone: str | None = None, password: str | None = None, email_confirm: bool = False, phone_confirm: bool = False) -> dict[str, Any]:
    args = ["auth", "users", "create", "--project-ref", project_ref]
    if email:
        args.extend(["--email", email])
    if phone:
        args.extend(["--phone", phone])
    if password:
        args.extend(["--password", password])
    if email_confirm:
        args.append("--email-confirm")
    if phone_confirm:
        args.append("--phone-confirm")
    return _run_supabase(args)


@mcp.tool()
def list_storage_buckets(project_ref: str) -> dict[str, Any]:
    return _run_supabase(["storage", "buckets", "list", "--project-ref", project_ref])


@mcp.tool()
def create_storage_bucket(project_ref: str, name: str) -> dict[str, Any]:
    return _run_supabase(["storage", "buckets", "create", name, "--project-ref", project_ref])


@mcp.tool()
def delete_storage_bucket(project_ref: str, name: str) -> dict[str, Any]:
    return _run_supabase(["storage", "buckets", "delete", name, "--project-ref", project_ref])


@mcp.tool()
def generate_types(language: str, project_ref: str, password: str | None = None) -> dict[str, Any]:
    return _run_supabase(["gen", "types", language, "--project-ref", project_ref, "--password", _db_password(password)], timeout=300)


if __name__ == "__main__":
    mcp.run(transport=os.getenv("MCP_TRANSPORT", "sse"))
