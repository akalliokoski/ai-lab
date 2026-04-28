from __future__ import annotations
import os
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
env_file = repo_root / ".env"
if env_file.exists():
    for raw in env_file.read_text().splitlines():
        if not raw or raw.lstrip().startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

keys = ["HF_TOKEN", "MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "WIKI_PATH"]
print("Environment check")
for key in keys:
    value = os.environ.get(key)
    status = "set" if value else "missing"
    print(f"- {key}: {status}")

wiki = Path(os.environ.get("WIKI_PATH", repo_root / "wiki")).expanduser()
print(f"- wiki path exists: {wiki.exists()} -> {wiki}")
print(f"- loaded repo .env: {env_file.exists()} -> {env_file}")
