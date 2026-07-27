"""
AMALIA Web Chat — browser-based interface using Gradio.

Usage:
    python app.py
Then open http://localhost:7860 in your browser.
"""

import ollama
import gradio as gr

MODEL = "amalia"


def chat(message: str, history: list[list[str | None]]) -> str:
    """Send a message to AMALIA and return the response."""
    # Convert Gradio history format to Ollama messages format
    messages: list[dict] = []
    for user_msg, bot_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": message})

    # Stream the response
    full_response = ""
    for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
        full_response += chunk["message"]["content"]
        yield full_response


def main() -> None:
    # Verify model is available before starting
    try:
        ollama.show(MODEL)
    except ollama.ResponseError:
        print(
            f"[ERROR] Model '{MODEL}' not found in Ollama.\n"
            "Run the setup script first:\n\n"
            "  python setup.py\n"
        )
        return

    demo = gr.ChatInterface(
        fn=chat,
        title="AMALIA — Assistente em Português Europeu",
        description=(
            "Converse com a AMALIA, um modelo de linguagem desenvolvido para o "
            "português europeu por um consórcio de universidades portuguesas."
        ),
        examples=[
            "Olá! Quem és tu?",
            "Explica-me o que é a inteligência artificial.",
            "Qual é a capital de Portugal e o que a torna especial?",
            "Escreve um pequeno poema sobre Lisboa.",
        ],
    )

    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
