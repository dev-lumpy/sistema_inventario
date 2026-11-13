"""Carga datos DEMO en la base local: 2 administradores, 20 vendedores
repartidos entre ellos y un catálogo de productos por administrador.

Uso:
    python seed_demo.py
    python seed_demo.py --reset
    python seed_demo.py --password "OtraClave123!"

Todos los usuarios creados usan el prefijo de username fijo (admin_norte,
admin_sur, vendedorNN) y los productos quedan asociados a esos administradores,
así que --reset borra únicamente los datos de esta demo.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.inventario.models import (  # noqa: E402
    Categoria,
    MovimientoStock,
    Producto,
    Proveedor,
)
from apps.usuarios.models import (  # noqa: E402
    AdministradorORM,
    VendedorORM,
)

ADMINS = {
    "admin_norte": {
        "nombre": "Admin Norte",
        "email": "admin_norte@demo.com",
        "categorias": ["Lubricantes", "Filtros", "Frenos", "Baterías"],
    },
    "admin_sur": {
        "nombre": "Admin Sur",
        "email": "admin_sur@demo.com",
        "categorias": ["Neumáticos", "Suspensión", "Motor", "Eléctrico"],
    },
}

VENDEDOR_NOMBRES = [
    "Ana García", "Bruno Pérez", "Carla Gómez", "Diego Fernández",
    "Elena Romero", "Federico Díaz", "Gabriela Sosa", "Hugo Martínez",
    "Inés López", "Javier Álvarez", "Karina Torres", "Lucas Ruiz",
    "María Benítez", "Nicolás Acosta", "Olivia Medina", "Pablo Herrera",
    "Rocío Silva", "Santiago Castro", "Valentina Ríos", "Matías Vega",
]

# Cada vendedor pertenece a uno o a ambos administradores.
# 7 solo Norte, 7 solo Sur y 6 a ambos (total 20).
VENDEDORES_POR_ADMIN = (
    [["admin_norte"]] * 7
    + [["admin_sur"]] * 7
    + [["admin_norte", "admin_sur"]] * 6
)

# (nombre, categoria, precio_unitario, stock_minimo, stock_inicial)
CATALOGO = {
    "admin_norte": [
        ("Aceite 20W-50 Mineral 5L (Norte)", "Lubricantes", 18500, 10, 42),
        ("Aceite 10W-40 Sintético 4L (Norte)", "Lubricantes", 32000, 8, 30),
        ("Filtro de Aceite Universal (Norte)", "Filtros", 6500, 15, 60),
        ("Filtro de Aire Deportivo (Norte)", "Filtros", 12000, 10, 24),
        ("Pastillas de Freno Delanteras (Norte)", "Frenos", 24500, 8, 18),
        ("Disco de Freno Ventilado (Norte)", "Frenos", 48000, 4, 12),
        ("Batería 12V 65Ah (Norte)", "Baterías", 95000, 3, 9),
        ("Batería 12V 80Ah (Norte)", "Baterías", 125000, 5, 4),
    ],
    "admin_sur": [
        ("Neumático 185/65 R15 (Sur)", "Neumáticos", 78000, 4, 14),
        ("Neumático 205/55 R16 (Sur)", "Neumáticos", 98000, 4, 10),
        ("Amortiguador Delantero (Sur)", "Suspensión", 42000, 4, 16),
        ("Rótula de Suspensión (Sur)", "Suspensión", 15500, 6, 22),
        ("Bujía de Iridio (Sur)", "Motor", 8900, 20, 35),
        ("Correa de Distribución (Sur)", "Motor", 36000, 5, 8),
        ("Lámpara H4 LED (Sur)", "Eléctrico", 14500, 10, 30),
        ("Fusible 15A pack x10 (Sur)", "Eléctrico", 3200, 15, 12),
    ],
}

PROVEEDORES = [
    ("Demo Repuestos Norte", "Juan Pérez", "381-555-2001", "norte@demo.com"),
    ("Demo Lubricantes Sur", "Carla Gómez", "381-555-2002", "sur@demo.com"),
    ("Demo Accesorios Centro", "Martín Díaz", "381-555-2003", "centro@demo.com"),
]

CANALES = ["whatsapp", "instagram", "facebook", "presencial", "otro"]
ESTADOS = ["activo"] * 17 + ["pendiente", "inactivo", "activo"]


def _crear_o_actualizar_admin(username: str, datos: dict, password_hash: str):
    return AdministradorORM.objects.update_or_create(
        username=username,
        defaults={
            "email": datos["email"],
            "password": password_hash,
            "activo": "activo",
        },
    )[0]


def _crear_o_actualizar_vendedor(username, nombre, indice, password_hash):
    return VendedorORM.objects.update_or_create(
        username=username,
        defaults={
            "email": f"{username}@demo.com",
            "password": password_hash,
            "activo": ESTADOS[indice],
        },
    )[0]


def _registrar_movimiento(producto, tipo, motivo, cantidad, fecha, **extra):
    """Crea el movimiento y le fija una fecha histórica.

    MovimientoStock.fecha usa auto_now_add, así que se actualiza después
    de crear el registro para poder repartir el historial en el tiempo.
    """
    movimiento = MovimientoStock.objects.create(
        producto=producto,
        tipo=tipo,
        motivo=motivo,
        cantidad=cantidad,
        **extra,
    )
    MovimientoStock.objects.filter(pk=movimiento.pk).update(fecha=fecha)
    return movimiento


def _crear_movimientos(producto: Producto, stock_inicial: int, rng: random.Random):
    """Genera un historial completo y cronológico para un producto.

    Incluye stock inicial, compras, ventas por distintos canales, mermas,
    ajustes y devoluciones repartidos en los últimos ~3 meses.
    """
    hoy = timezone.now()
    dias_historial = rng.randint(80, 110)
    inicio = hoy - timedelta(days=dias_historial)

    stock = max(stock_inicial, 40)
    _registrar_movimiento(
        producto,
        MovimientoStock.TIPO_ENTRADA,
        MovimientoStock.MOTIVO_INICIAL,
        stock,
        inicio + timedelta(hours=9),
        detalle="Stock inicial demo",
    )

    proveedores = list(Proveedor.objects.all())

    # Se planifican todos los eventos y luego se ordenan por fecha para que
    # el stock nunca quede negativo.
    eventos = []
    for _ in range(rng.randint(8, 12)):
        eventos.append(("compra", rng.randint(2, dias_historial)))
    for _ in range(rng.randint(20, 32)):
        eventos.append(("venta", rng.randint(1, dias_historial)))
    for _ in range(rng.randint(2, 5)):
        eventos.append(("merma", rng.randint(5, dias_historial)))
    for _ in range(rng.randint(2, 4)):
        eventos.append(("ajuste", rng.randint(5, dias_historial)))
    for _ in range(rng.randint(1, 3)):
        eventos.append(("devolucion", rng.randint(5, dias_historial)))
    eventos.sort(key=lambda evento: (evento[1], rng.random()))

    ventas = 0
    compras = 0

    for tipo_evento, offset in eventos:
        fecha = inicio + timedelta(
            days=offset,
            hours=rng.randint(8, 20),
            minutes=rng.randint(0, 59),
        )

        if tipo_evento == "compra":
            cantidad = rng.randint(5, 25)
            compras += 1
            _registrar_movimiento(
                producto,
                MovimientoStock.TIPO_ENTRADA,
                MovimientoStock.MOTIVO_COMPRA,
                cantidad,
                fecha,
                proveedor=rng.choice(proveedores),
                detalle=f"Factura demo A-{compras:04d}",
            )
            stock += cantidad

        elif tipo_evento == "venta":
            if stock <= 0:
                continue
            cantidad = rng.randint(1, min(4, stock))
            ventas += 1
            _registrar_movimiento(
                producto,
                MovimientoStock.TIPO_SALIDA,
                MovimientoStock.MOTIVO_VENTA,
                cantidad,
                fecha,
                canal_venta=rng.choice(CANALES),
                detalle=f"Venta demo #{ventas:03d}",
            )
            stock -= cantidad

        elif tipo_evento == "merma":
            if stock <= 0:
                continue
            cantidad = rng.randint(1, min(2, stock))
            _registrar_movimiento(
                producto,
                MovimientoStock.TIPO_SALIDA,
                MovimientoStock.MOTIVO_MERMA,
                cantidad,
                fecha,
                detalle="Merma detectada en depósito",
            )
            stock -= cantidad

        elif tipo_evento == "devolucion":
            cantidad = rng.randint(1, 3)
            _registrar_movimiento(
                producto,
                MovimientoStock.TIPO_ENTRADA,
                MovimientoStock.MOTIVO_DEVOLUCION,
                cantidad,
                fecha,
                detalle="Devolución de cliente",
            )
            stock += cantidad

        elif tipo_evento == "ajuste":
            if stock > 0 and rng.random() < 0.5:
                cantidad = rng.randint(1, min(3, stock))
                tipo = MovimientoStock.TIPO_SALIDA
                stock -= cantidad
            else:
                cantidad = rng.randint(1, 3)
                tipo = MovimientoStock.TIPO_ENTRADA
                stock += cantidad
            _registrar_movimiento(
                producto,
                tipo,
                MovimientoStock.MOTIVO_AJUSTE,
                cantidad,
                fecha,
                detalle="Ajuste de inventario demo",
            )

    # Algunos productos quedan en alerta para poder ver ese estado en el panel.
    objetivos_alerta = {
        "Batería 12V 80Ah (Norte)",
        "Fusible 15A pack x10 (Sur)",
    }
    if producto.nombre in objetivos_alerta and stock > producto.stock_minimo:
        cantidad = stock - producto.stock_minimo
        _registrar_movimiento(
            producto,
            MovimientoStock.TIPO_SALIDA,
            MovimientoStock.MOTIVO_VENTA,
            cantidad,
            hoy - timedelta(hours=rng.randint(1, 6)),
            canal_venta="presencial",
            detalle="Venta demo de liquidación",
        )
        stock = producto.stock_minimo

    # El producto también "existe" desde antes del historial.
    Producto.objects.filter(pk=producto.pk).update(
        creado=inicio - timedelta(days=rng.randint(1, 10))
    )


def borrar_demo():
    productos = Producto.objects.filter(
        administrador__username__in=list(ADMINS)
    )
    productos.delete()

    VendedorORM.objects.filter(
        username__in=[f"vendedor{i:02d}" for i in range(1, 21)]
    ).delete()
    AdministradorORM.objects.filter(username__in=list(ADMINS)).delete()
    Proveedor.objects.filter(
        nombre__in=[proveedor[0] for proveedor in PROVEEDORES]
    ).delete()


def cargar_demo(password: str, seed: int):
    rng = random.Random(seed)
    password_hash = make_password(password)

    admins = {
        username: _crear_o_actualizar_admin(username, datos, password_hash)
        for username, datos in ADMINS.items()
    }

    for nombre in {cat for datos in ADMINS.values() for cat in datos["categorias"]}:
        Categoria.objects.get_or_create(nombre=nombre)

    for nombre, contacto, telefono, email in PROVEEDORES:
        Proveedor.objects.get_or_create(
            nombre=nombre,
            defaults={
                "contacto": contacto,
                "telefono": telefono,
                "email": email,
            },
        )

    vendedores = []
    for indice, nombre in enumerate(VENDEDOR_NOMBRES):
        username = f"vendedor{indice + 1:02d}"
        vendedor = _crear_o_actualizar_vendedor(
            username, nombre, indice, password_hash
        )
        vendedor.admins.set([admins[admin] for admin in VENDEDORES_POR_ADMIN[indice]])
        vendedores.append(vendedor)

    total_productos = 0
    for username_admin, datos in ADMINS.items():
        admin = admins[username_admin]
        for nombre, categoria, precio, stock_minimo, stock_inicial in CATALOGO[username_admin]:
            producto, creado = Producto.objects.update_or_create(
                nombre=nombre,
                defaults={
                    "categoria": Categoria.objects.get(nombre=categoria),
                    "precio_unitario": precio,
                    "stock_minimo": stock_minimo,
                    "administrador": admin,
                    "activo": True,
                },
            )
            if creado:
                _crear_movimientos(producto, stock_inicial, rng)
            total_productos += 1

    print("Datos demo cargados correctamente")
    print(f"  Administradores: {len(admins)}")
    print(f"  Vendedores:      {len(vendedores)}")
    print(f"  Productos:       {total_productos}")
    print(f"  Contraseña:      {password}")
    print()
    print("Usuarios disponibles:")
    for username in ADMINS:
        print(f"  admin      -> {username}")
    print("  vendedores -> vendedor01 ... vendedor20")
    print()
    print("Vendedores que pertenecen a ambos admins: vendedor15 ... vendedor20")


def main():
    parser = argparse.ArgumentParser(description="Carga datos demo del taller.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra los datos demo antes de volver a cargarlos.",
    )
    parser.add_argument(
        "--password",
        default="Taller#2026",
        help="Contraseña para todos los usuarios demo (default: Taller#2026).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla para precios/cantidades aleatorias (default: 42).",
    )
    args = parser.parse_args()

    with transaction.atomic():
        if args.reset:
            borrar_demo()
        cargar_demo(args.password, args.seed)


if __name__ == "__main__":
    main()
