#!/usr/bin/env python
"""
CLI para gestionar llaves y licencias del Sistema Taller.

Uso:
    python manage_license.py generate-keys
    python manage_license.py embed-key <public_key_file>
    python manage_license.py create --private <private_key_file> --client "Nombre" [--email "x@x.com"] [--days 365] [--machine-id <id>]
    python manage_license.py show-machine-id
"""

import argparse
import sys
from pathlib import Path

from config.license import generate_keys, create_license, get_machine_id

BASE_DIR = Path(__file__).resolve().parent


def cmd_generate_keys():
    priv_path = BASE_DIR / "private_key.pem"
    pub_path = BASE_DIR / "public_key.pem"

    private_pem, public_pem = generate_keys()
    priv_path.write_text(private_pem)
    pub_path.write_text(public_pem)

    print(f"✓ Llave privada:  {priv_path}")
    print(f"✓ Llave pública:  {pub_path}")
    print("¡Guarda la llave privada en un lugar seguro! Sin ella no podrás generar licencias.")


def cmd_embed_key(args):
    pub_path = Path(args.public_key_file)
    if not pub_path.exists():
        print(f"✗ No existe: {pub_path}")
        sys.exit(1)

    pub_pem = pub_path.read_text().strip()
    license_path = BASE_DIR / "config" / "license.py"

    # Escapar el PEM para que sea un string de Python válido
    escaped = pub_pem.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    line = f'PUBLIC_KEY_PEM: str = "{escaped}"\n'

    content = license_path.read_text()
    lines = content.splitlines()
    new_lines = []
    replaced = False
    for line_text in lines:
        if line_text.startswith("PUBLIC_KEY_PEM: str = "):
            new_lines.append(line.rstrip("\n"))
            replaced = True
        else:
            new_lines.append(line_text)
    if not replaced:
        print("✗ No se encontró la línea PUBLIC_KEY_PEM en license.py")
        sys.exit(1)

    license_path.write_text("\n".join(new_lines) + "\n")
    print(f"✓ Llave pública embebida en config/license.py")


def cmd_create(args):
    priv_path = Path(args.private_key_file)
    if not priv_path.exists():
        print(f"✗ No existe: {priv_path}")
        sys.exit(1)

    private_pem = priv_path.read_text()
    lic = create_license(
        private_pem,
        client=args.client,
        email=args.email or "",
        days=args.days,
        machine_id=args.machine_id or "",
    )

    lic_path = BASE_DIR / "license.lic"
    lic_path.write_text(lic)
    print(f"✓ Licencia creada: {lic_path}")
    print(lic)


def cmd_show_machine_id():
    print(get_machine_id())


def main():
    parser = argparse.ArgumentParser(description="Gestión de licencias Sistema Taller")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("generate-keys", help="Genera un par de llaves RSA")

    ek = sub.add_parser("embed-key", help="Embebe la llave pública en el código")
    ek.add_argument("public_key_file", help="Archivo public_key.pem")

    cr = sub.add_parser("create", help="Crea un archivo de licencia firmado")
    cr.add_argument("--private", dest="private_key_file", required=True, help="Archivo de llave privada")
    cr.add_argument("--client", required=True, help="Nombre del cliente")
    cr.add_argument("--email", default="", help="Email del cliente")
    cr.add_argument("--days", type=int, default=365, help="Días de validez (default: 365)")
    cr.add_argument("--machine-id", default="", help="ID de máquina (para amarrar la licencia a un equipo)")

    sub.add_parser("show-machine-id", help="Muestra el ID de esta máquina")

    args = parser.parse_args()

    if args.command == "generate-keys":
        cmd_generate_keys()
    elif args.command == "embed-key":
        cmd_embed_key(args)
    elif args.command == "create":
        cmd_create(args)
    elif args.command == "show-machine-id":
        cmd_show_machine_id()


if __name__ == "__main__":
    main()