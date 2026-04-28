from __future__ import annotations
import os
from pathlib import Path

keys = ["HF_TOKEN", "MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "WIKI_PATH"]
print("Environment check")
for key in keys:
    value = os.environ.get(key)
    status = "set" if value else "missing"
    print(f"- {key}: {status}")

wiki = Path(os.environ.get("WIKI_PATH", "wiki")).expanduser()
print(f"- wiki path exists: {wiki.exists()} -> {wiki}")
