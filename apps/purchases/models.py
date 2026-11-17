from django.db import models
from django.utils import timezone


class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="proveedores",
    )
    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "proveedores"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self) -> str:
        return self.nombre


class Compra(models.Model):
    ESTADOS = (
        ("borrador", "Borrador"),
        ("confirmada", "Confirmada"),
        ("anulada", "Anulada"),
    )

    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="compras",
    )
    proveedor = models.ForeignKey(
        Proveedor,
        db_column="proveedor_id",
        on_delete=models.PROTECT,
        related_name="compras",
    )
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    nota = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "compras"
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    def __str__(self) -> str:
        return f"Compra {self.pk}"


class CompraDetalle(models.Model):
    id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(
        Compra,
        db_column="compra_id",
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="compra_detalles",
    )
    producto = models.ForeignKey(
        "catalog.Producto",
        db_column="producto_id",
        on_delete=models.PROTECT,
        related_name="compra_detalles",
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "compra_detalle"
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def __str__(self) -> str:
        return f"{self.compra_id} / {self.producto_id}"
