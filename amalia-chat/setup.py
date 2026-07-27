"""
Setup script — downloads AMALIA GGUF from HuggingFace and imports it into Ollama.

Run once before using chat.py or app.py:
    python setup.py
"""

import subprocess
import sys
from pathlib import Path

GGUF_URL = (
    "https://huggingface.co/duarteocarmo/AMALIA-9B-0626-DPO-GGUF/resolve/main/"
    "AMALIA-9B-0626-DPO-Q4_K_M.gguf"
)
GGUF_FILE = Path("AMALIA-9B-0626-DPO-Q4_K_M.gguf")
MODELFILE = Path("Modelfile")
MODEL_NAME = "amalia"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def main() -> None:
    # 1. Check Ollama is installed
    result = run(["ollama", "--version"], check=False)
    if result.returncode != 0:
        print(
            "\n[ERROR] Ollama is not installed or not in PATH.\n"
            "Download it from https://ollama.com and try again.\n"
        )
        sys.exit(1)

    # 2. Download the GGUF model if not already present
    if GGUF_FILE.exists():
        print(f"\n[OK] {GGUF_FILE} already downloaded, skipping download.\n")
    else:
        print(f"\nDownloading AMALIA Q4_K_M GGUF (~5.2 GB)...")
        try:
            run(["curl", "-L", "-o", str(GGUF_FILE), GGUF_URL])
        except FileNotFoundError:
            # Fall back to Python urllib if curl isn't available
            import urllib.request
            print("curl not found, using Python urllib...")
            urllib.request.urlretrieve(GGUF_URL, GGUF_FILE)

    # 3. Rewrite Modelfile to use the local file path
    local_modelfile = MODELFILE.read_text(encoding="utf-8")
    if "FROM duarteocarmo" in local_modelfile:
        local_modelfile = local_modelfile.replace(
            "FROM duarteocarmo/AMALIA-9B-0626-DPO-GGUF:Q4_K_M",
            f"FROM ./{GGUF_FILE}",
        )
        MODELFILE.write_text(local_modelfile, encoding="utf-8")
        print(f"\n[OK] Updated Modelfile to use local GGUF file.\n")

    # 4. Build the Ollama model
    print(f"\nCreating Ollama model '{MODEL_NAME}'...")
    run(["ollama", "create", MODEL_NAME, "-f", str(MODELFILE)])

    print(f"\n[DONE] Model '{MODEL_NAME}' is ready.\n")
    print("Start chatting:")
    print("  Terminal:  python chat.py")
    print("  Browser:   python app.py  →  http://localhost:7860\n")


if __name__ == "__main__":
    main()
