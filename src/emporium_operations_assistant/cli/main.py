"""Interactive CLI chat with the Emporium assistant (Maiara)."""

from __future__ import annotations

import sys

from emporium_operations_assistant.assistant.chat import ChatService
from emporium_operations_assistant.config import load_settings


def _print_banner(display_name: str) -> None:
    print()
    print(f"=== Emporium Operations Assistant — {display_name} ===")
    print("Digite sua mensagem e pressione Enter.")
    print("Comandos: /sair ou /exit — encerrar")
    print()


def main() -> None:
    settings = load_settings()
    if settings.llm_provider == "gemini" and not settings.gemini_api_key:
        print(
            "GEMINI_API_KEY não configurada. Adicione em .env e tente novamente.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        chat = ChatService(settings)
        display_name = chat.display_name
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    _print_banner(display_name)

    while True:
        try:
            user_line = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if not user_line:
            continue
        lowered = user_line.lower()
        if lowered in {"/sair", "/exit", "/quit", "sair", "exit", "quit"}:
            print("Até logo!")
            break

        reply = chat.complete_user_message(user_line)
        print(f"\n{display_name}: {reply}\n")


if __name__ == "__main__":
    main()
