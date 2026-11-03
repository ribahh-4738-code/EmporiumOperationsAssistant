"""Static store facts (aligned with data/políticas_da_loja.pdf)."""

from __future__ import annotations


def build_store_context() -> str:
    """Always-on block mirroring PDF sections 1.2 and 2 (see data/políticas_da_loja.pdf)."""
    return (
        "Informações gerais da loja — manual data/políticas_da_loja.pdf "
        "(seções 1.2 Dados da Empresa e 2 Horário de Funcionamento):\n"
        "1.2 Dados da Empresa:\n"
        "- Nome fantasia: Empório da Música (Campo Grande/MS)\n"
        "- Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande – MS, CEP 79202-333\n"
        "- Telefone / WhatsApp: (67) 3341-4444\n"
        "- E-mail: contato@emporiodamusica.com.br\n"
        "2 Horário de Funcionamento (presencial e WhatsApp):\n"
        "- Segunda a sexta-feira: 09:00 às 18:00\n"
        "- Sábado: 09:00 às 13:00\n"
        "- Domingo e feriados: fechado\n"
        "Outras regras (trocas, pagamento, prazos): use os trechos RAG do mesmo PDF."
    )
