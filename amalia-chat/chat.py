"""
AMALIA CLI Chat — interact with the AMALIA Portuguese LLM via Ollama.

Usage:
    python chat.py
"""

import sys
import ollama

MODEL = "amalia"


def stream_response(messages: list[dict]) -> str:
    """Stream the model response and return the full text."""
    full_response = ""
    print("\nAMALIA: ", end="", flush=True)

    for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        full_response += token

    print()  # newline after response
    return full_response


def main() -> None:
    print("=" * 50)
    print("  AMALIA — Assistente em Português Europeu")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 50)
    print()

    # Check the model is available
    try:
        ollama.show(MODEL)
    except ollama.ResponseError:
        print(
            f"[ERROR] Model '{MODEL}' not found in Ollama.\n"
            "Run the setup script first:\n\n"
            "  python setup.py\n"
        )
        sys.exit(1)

    messages: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nUntil next time! / Até a próxima!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "sair"}:
            print("Até a próxima!")
            break

        messages.append({"role": "user", "content": user_input})
        response = stream_response(messages)
        messages.append({"role": "assistant", "content": response})
        print()


if __name__ == "__main__":
    main()
