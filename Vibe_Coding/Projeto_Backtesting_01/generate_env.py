#!/usr/bin/env python3
"""
Gera o arquivo .env a partir do .env.example com SECRET_KEY aleatória.

Uso:
    python generate_env.py
"""
import secrets
import shutil
from pathlib import Path

ENV_EXAMPLE = Path(".env.example")
ENV_FILE = Path(".env")


def generate_secret_key(length: int = 50) -> str:
    """Gera uma SECRET_KEY criptograficamente segura."""
    return secrets.token_urlsafe(length)


def main() -> None:
    if not ENV_EXAMPLE.exists():
        print("❌ .env.example não encontrado no diretório atual.")
        raise SystemExit(1)

    if ENV_FILE.exists():
        print("⚠️  .env já existe. Abortando para não sobrescrever.")
        print("   Delete-o manualmente se quiser regenerar.")
        raise SystemExit(0)

    shutil.copy(ENV_EXAMPLE, ENV_FILE)

    content = ENV_FILE.read_text()
    secret = generate_secret_key()
    content = content.replace("SECRET_KEY=change-me", f"SECRET_KEY={secret}")
    ENV_FILE.write_text(content)

    print("✅ .env criado com sucesso!")
    print(f"   SECRET_KEY gerada: {secret[:12]}...")
    print("   Preencha as demais variáveis antes de fazer deploy.")


if __name__ == "__main__":
    main()
