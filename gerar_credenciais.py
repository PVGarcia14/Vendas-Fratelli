import getpass
import hashlib
import secrets

username = input("Nome do utilizador: ").strip()
if not username or any(c in username for c in " .[]"):
    raise SystemExit("Use um nome simples, sem espaços, pontos ou colchetes.")
password = getpass.getpass("Defina a palavra-passe: ")
if len(password) < 12:
    raise SystemExit("Use uma palavra-passe com pelo menos 12 caracteres.")
salt = secrets.token_hex(16)
digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 310_000).hex()
role = input("Perfil (admin/user) [user]: ").strip().lower() or "user"
if role not in ("admin", "user"):
    raise SystemExit("Perfil inválido. Use admin ou user.")
print("\nCopie este bloco para Streamlit Community Cloud → Settings → Secrets:")
print(f"[users.{username}]")
print(f'salt = "{salt}"')
print(f'password_hash = "{digest}"')
print(f'role = "{role}"')
print("\nNunca guarde a palavra-passe ou secrets no GitHub.")
