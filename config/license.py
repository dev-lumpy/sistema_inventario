"""
Sistema de licencias para Sistema Taller.

Usa RSA (PKCS1v15 + SHA256) para firmar archivos de licencia.
La llave pública va embebida en el código; la privada solo la tiene el autor.

Uso desde CLI:
    python manage_license.py generate-keys
    python manage_license.py create --client "Cliente" --email "x@x.com" --days 365
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.backends import default_backend

# ─── Ruta base ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Llave pública embebida (se genera con generate-keys) ────────────────────
# Se reemplaza al ejecutar `python manage_license.py embed-key`
PUBLIC_KEY_PEM: str = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuKDdtjKl41ckhdOnut9n\nTO29fMyA23zylmxMOrZF4wFWWhw/hBbAb9IGI0/gOqlGkvCMhc1jsXj5IN/hlMHQ\nZdJwJ59EHS4ZnnP0DGn81l2P7L8X0GwZj5Cai6+qPJ3O1BP/4h8EGHmSfeq1xM4K\nPVuR2QK0S2xlZgVbEZ3rHjeWJ4CYnNDnNDv6RTs1LVLAJ7eQzz7dDg2FgIZ40kmY\nDPR9KM1LGr+uEBMvbeFXr+hS5nIP+D0c5mSPgPxlWeYjjPOswqRQiMg2fv35wkjF\nEf1EFSuhXe4dCtnWD7sJtRp4YjxbQuhDtsUf/r9o1ix/5ukiiUwE9nxWvOAZnRia\nbQIDAQAB\n-----END PUBLIC KEY-----"

# ─── Archivo de licencia ─────────────────────────────────────────────────────
LICENSE_FILE = BASE_DIR / "license.lic"


def _load_public_key() -> RSAPublicKey | None:
    if not PUBLIC_KEY_PEM:
        return None
    return serialization.load_pem_public_key(PUBLIC_KEY_PEM.encode(), backend=default_backend())  # type: ignore


def get_machine_id() -> str:
    """Devuelve un identificador único de la máquina (/etc/machine-id + hostname)."""
    import hashlib
    machine_id_file = "/etc/machine-id"
    try:
        mid = Path(machine_id_file).read_text().strip()
    except Exception:
        mid = "unknown"
    hostname = os.uname().nodename
    raw = f"{mid}-{hostname}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def verify_license() -> dict | None:
    """Verifica el archivo license.lic y devuelve los datos si es válido."""
    if not LICENSE_FILE.exists():
        return None

    public_key = _load_public_key()
    if public_key is None:
        # No hay llave pública configurada → modo desarrollo
        return {"client": "development", "status": "dev"}

    try:
        data = json.loads(LICENSE_FILE.read_text())
        signature = bytes.fromhex(data.pop("signature"))
        payload = json.dumps(data, separators=(",", ":")).encode()

        public_key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA256())

        expires = datetime.fromisoformat(data["expires"])
        if expires < datetime.now(timezone.utc):
            return None  # Expirada

        # Verificar que la máquina coincida con la licencia
        machine_id = get_machine_id()
        if data.get("machine_id") and data["machine_id"] != machine_id:
            return None  # Licencia emitida para otra máquina

        return data
    except Exception:
        return None


def generate_keys() -> tuple[str, str]:
    """Genera un par de llaves RSA y devuelve (privada_pem, pública_pem)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def create_license(
    private_key_pem: str,
    client: str,
    email: str = "",
    days: int = 365,
    machine_id: str = "",
    extra: dict | None = None,
) -> str:
    """Crea un archivo de licencia firmado y devuelve su contenido JSON.

    machine_id: ID de la máquina (get_machine_id()) para amarrar la licencia
                a un equipo específico. Si se omite, la licencia funciona en
                cualquier máquina.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None, backend=default_backend()
    )
    issued = datetime.now(timezone.utc)
    expires = issued + timedelta(days=days)
    payload = {
        "client": client,
        "email": email,
        "issued": issued.isoformat(),
        "expires": expires.isoformat(),
        **(extra or {}),
    }
    if machine_id:
        payload["machine_id"] = machine_id
    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    signature = private_key.sign(payload_json, padding.PKCS1v15(), hashes.SHA256())  # type: ignore
    payload["signature"] = signature.hex()
    return json.dumps(payload, indent=2)
