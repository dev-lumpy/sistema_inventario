from django.db import models
from django.utils import timezone


class Venta(models.Model):
    TIPOS_CLIENTE = (
        ("individual", "Individual"),
        ("productor", "Productor"),
        ("mayoreo", "Mayoreo"),
    )
    ESTADOS = (
        ("borrador", "Borrador"),
        ("confirmada", "Confirmada"),
        ("anulada", "Anulada"),
    )
    CANALES = (
        ("whatsapp", "WhatsApp"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("presencial", "Presencial"),
        ("otro", "Otro"),
    )

    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="ventas",
    )
    vendedor = models.ForeignKey(
        "accounts.Vendedor",
        db_column="vendedor_id",
        on_delete=models.PROTECT,
        related_name="ventas",
    )
    cliente_nombre = models.CharField(max_length=150, null=True, blank=True)
    tipo_cliente = models.CharField(max_length=20, choices=TIPOS_CLIENTE)
    canal_venta = models.CharField(
        max_length=20, choices=CANALES, null=True, blank=True
    )
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    nota = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "ventas"
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def __str__(self) -> str:
        return f"Venta {self.pk}"


class VentaDetalle(models.Model):
    id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(
        Venta,
        db_column="venta_id",
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="venta_detalles",
    )
    producto = models.ForeignKey(
        "catalog.Producto",
        db_column="producto_id",
        on_delete=models.PROTECT,
        related_name="venta_detalles",
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "venta_detalle"
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self) -> str:
        return f"{self.venta_id} / {self.producto_id}"
