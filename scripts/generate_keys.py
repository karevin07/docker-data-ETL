#!/usr/bin/env python3
"""
生成 Airflow 所需的安全金鑰

使用方式:
    python scripts/generate_keys.py
    
不需要安裝額外套件，僅使用 Python 內建模組。
"""

import secrets
import base64


def generate_fernet_key():
    """生成 Fernet 相容的金鑰 (32 bytes base64 編碼)"""
    # Fernet 需要 32 bytes 的金鑰，base64 編碼後
    key_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key_bytes).decode()


def generate_secret_key():
    """生成 Flask session secret key"""
    return secrets.token_urlsafe(32)


if __name__ == "__main__":
    print("=" * 60)
    print("Airflow Security Keys Generator")
    print("=" * 60)
    print()
    
    fernet_key = generate_fernet_key()
    secret_key = generate_secret_key()
    
    print("🔐 Fernet Key (用於資料庫加密):")
    print(f"   {fernet_key}")
    print()
    
    print("🔑 Secret Key (用於 Web Session):")
    print(f"   {secret_key}")
    print()
    
    print("=" * 60)
    print("請將以上金鑰加入 .env 檔案:")
    print("=" * 60)
    print()
    print(f"AIRFLOW_FERNET_KEY={fernet_key}")
    print(f"AIRFLOW_SECRET_KEY={secret_key}")
    print()
    print("💡 提示: 可以直接執行以下指令將金鑰加入 .env:")
    print()
    print("  python scripts/generate_keys.py >> .env")
    print()
