"""牛香香品牌 · 统一配置加载器
从 .env 文件读取凭证，杜绝硬编码
"""
import os
from pathlib import Path

def _find_env():
    """向上查找 .env 文件"""
    for p in [Path.cwd(), Path(__file__).resolve().parent.parent]:
        for candidate in [p, p.parent, p.parent.parent]:
            env_path = candidate / ".env"
            if env_path.exists():
                return env_path
    return None

def load_env():
    """加载 .env 到 os.environ"""
    env_path = _find_env()
    if not env_path:
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if key and val and key not in os.environ:
                os.environ[key] = val

# 自动加载
load_env()

# 便捷访问
JHF_USERNAME = os.environ.get("JHF_USERNAME", "")
JHF_PASSWORD = os.environ.get("JHF_PASSWORD", "")
JHF_LOGIN_URL = os.environ.get("JHF_LOGIN_URL", "https://h2025.jihuifan.com/web/index.php?c=user&a=login&")
JHF_BASE_URL = os.environ.get("JHF_BASE_URL", "https://h2025.jihuifan.com")
