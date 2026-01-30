#!/usr/bin/env python3
"""
Generate secure keys for Docker Data ETL Platform

This script generates all required security keys for the .env file:
- Airflow Fernet Key (for encrypting sensitive data)
- Airflow Webserver Secret Key (for Flask session encryption)
- JupyterLab Token (for notebook access)

Usage:
    python scripts/generate_keys.py

The script will output the keys in .env format that you can copy-paste.
Does not require external packages - uses Python built-in modules only.
"""

import secrets
import base64


def generate_fernet_key():
    """Generate a Fernet-compatible key (32 bytes base64 encoded)"""
    # Fernet requires a 32-byte key, base64 encoded
    key_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key_bytes).decode()


def generate_secret_key():
    """Generate a secret key for Flask session"""
    return secrets.token_urlsafe(32)


def generate_jupyter_token():
    """Generate a token for JupyterLab"""
    return secrets.token_hex(32)


if __name__ == "__main__":
    print("=" * 70)
    print("Docker Data ETL Platform - Security Keys Generator")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: Keep these keys secret and secure!")
    print("⚠️  Add them to your .env file and never commit them to git!")
    print()
    print("-" * 70)

    # Generate all keys
    fernet_key = generate_fernet_key()
    secret_key = generate_secret_key()
    jupyter_token = generate_jupyter_token()

    # Output in .env format
    print("\n# Copy the following lines to your .env file:\n")
    print("# Airflow Security Keys")
    print(f"AIRFLOW_FERNET_KEY={fernet_key}")
    print(f"AIRFLOW_SECRET_KEY={secret_key}")
    print()
    print("# JupyterLab Token (optional - if not set, auto-generated)")
    print(f"JUPYTER_TOKEN={jupyter_token}")
    print()
    print("-" * 70)
    print()
    print("✅ Keys generated successfully!")
    print()
    print("Next steps:")
    print("1. Copy the keys above to your .env file")
    print("2. Set AIRFLOW_ADMIN_USERNAME and AIRFLOW_ADMIN_PASSWORD in .env")
    print("   Example: AIRFLOW_ADMIN_USERNAME=admin")
    print("   Example: AIRFLOW_ADMIN_PASSWORD=your_secure_password")
    print("3. Start the services with: docker-compose up -d")
    print()
