from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="categorias",
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "categorias"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self) -> str:
        return self.nombre


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="productos",
    )
    categoria = models.ForeignKey(
        Categoria,
        db_column="categoria_id",
        on_delete=models.PROTECT,
        related_name="productos",
    )
    nombre = models.CharField(max_length=200)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return self.nombre


class PrecioProducto(models.Model):
    TIPOS_CLIENTE = (
        ("individual", "Individual"),
        ("productor", "Productor"),
        ("mayoreo", "Mayoreo"),
    )

    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="precios",
    )
    producto = models.ForeignKey(
        Producto,
        db_column="producto_id",
        on_delete=models.CASCADE,
        related_name="precios",
    )
    tipo_cliente = models.CharField(max_length=20, choices=TIPOS_CLIENTE)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, default="BOB")
    vigente_desde = models.DateTimeField(default=timezone.now)
    vigente_hasta = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "precios_producto"
        verbose_name = "Precio de producto"
        verbose_name_plural = "Precios de producto"

    def __str__(self) -> str:
        return f"{self.producto} / {self.tipo_cliente}"


class MovimientoInventario(models.Model):
    MOTIVOS = (
        ("compra", "Compra"),
        ("venta", "Venta"),
        ("devolucion", "Devolución"),
        ("merma", "Merma"),
        ("ajuste_pos", "Ajuste positivo"),
        ("ajuste_neg", "Ajuste negativo"),
    )
    REFERENCIAS = (
        ("venta", "Venta"),
        ("compra", "Compra"),
        ("ajuste", "Ajuste"),
    )

    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="movimientos",
    )
    producto = models.ForeignKey(
        Producto,
        db_column="producto_id",
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    motivo = models.CharField(max_length=30, choices=MOTIVOS)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    fecha = models.DateTimeField(default=timezone.now)
    costo_unitario = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    precio_unitario = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    referencia_tipo = models.CharField(
        max_length=20, choices=REFERENCIAS, null=True, blank=True
    )
    referencia_id = models.IntegerField(null=True, blank=True)
    usuario = models.ForeignKey(
        "accounts.Usuario",
        db_column="usuario_id",
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    nota = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"

    def __str__(self) -> str:
        return f"{self.producto} / {self.motivo} / {self.cantidad}"
