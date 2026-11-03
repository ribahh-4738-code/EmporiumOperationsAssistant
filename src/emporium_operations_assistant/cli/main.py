"""Interactive CLI chat with the Emporium assistant (Maiara)."""

from __future__ import annotations

import argparse
import sys

from emporium_operations_assistant.assistant.chat import ChatService
from emporium_operations_assistant.config import load_settings


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chat CLI com a Maiara (Emporium Operations Assistant).",
    )
    parser.add_argument(
        "--customer-id",
        type=int,
        default=None,
        help="Vincula a sessão a um customer_id (pedidos recentes no contexto).",
    )
    return parser.parse_args(argv)


def _print_banner(display_name: str, session_customer_id: int | None) -> None:
    print()
    print(f"=== Emporium Operations Assistant — {display_name} ===")
    print("Digite sua mensagem e pressione Enter.")
    print("Comandos: /sair ou /exit — encerrar")
    if session_customer_id is not None:
        print(f"Contexto de pedidos: cliente #{session_customer_id} (sessão CLI)")
    print("Consulta de pedidos na conversa: número do pedido ou e-mail cadastrado.")
    print("Opcional: /cliente <id> ou /cliente (limpar vínculo)")
    print()


def _handle_cliente_command(chat: ChatService, arg: str) -> bool:
    """Return True if handled (do not send to LLM)."""
    parts = arg.split(maxsplit=1)
    if len(parts) == 1:
        chat.session_customer_id = None
        print("Vínculo de cliente da sessão removido.\n")
        return True
    try:
        cid = int(parts[1].strip())
    except ValueError:
        print("Use: /cliente <número> ou /cliente para limpar.\n")
        return True
    if cid <= 0:
        print("customer_id deve ser um inteiro positivo.\n")
        return True
    chat.session_customer_id = cid
    print(f"Contexto de pedidos: cliente #{cid}\n")
    return True


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    settings = load_settings()
    if settings.llm_provider == "gemini" and not settings.gemini_api_key:
        print(
            "GEMINI_API_KEY não configurada. Adicione em .env e tente novamente.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    session_id = args.customer_id if args.customer_id is not None else settings.chat_customer_id

    try:
        chat = ChatService(settings, session_customer_id=session_id)
        display_name = chat.display_name
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    _print_banner(display_name, chat.session_customer_id)

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

        if lowered == "/cliente" or lowered.startswith("/cliente "):
            _handle_cliente_command(chat, user_line)
            continue

        reply = chat.complete_user_message(user_line)
        print(f"\n{display_name}: {reply}\n")


if __name__ == "__main__":
    main()
