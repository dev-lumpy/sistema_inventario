# apps/inventario/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    contacto = models.CharField(max_length=150, blank=True)     # persona
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre 


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT,
                                  related_name='productos')
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock_minimo = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Se mostrará alerta cuando el stock llegue a este valor."
    )
    creado = models.DateTimeField(auto_now_add=True)

    activo = models.BooleanField(default=True)

    # ESTADO_ACTIVO = 'activo' Solo es para hacer actualisaciones el codigo
    # ESTADO_PAUSADO = 'pausado'
    # ESTADO_DISCONTINUADO = 'discontinuado'
    #
    # ESTADOS = [
    #     (ESTADO_ACTIVO, 'Activo'),
    #     (ESTADO_PAUSADO, 'Pausado'),
    #     (ESTADO_DISCONTINUADO, 'Discontinuado'),
    # ]
    #
    # estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)

    def __str__(self):
        return self.nombre

    # ---------- Stock calculado desde los movimientos ----------
    @property
    def stock_actual(self):
        agg = self.movimientos.aggregate(
            entradas=Sum('cantidad', filter=Q(tipo='E')),
            salidas=Sum('cantidad', filter=Q(tipo='S')),
        )
        return (agg['entradas'] or 0) - (agg['salidas'] or 0)

    @property
    def en_alerta(self):
        return self.stock_actual <= self.stock_minimo


class MovimientoStock(models.Model):
    TIPO_ENTRADA = 'E'
    TIPO_SALIDA = 'S'
    TIPOS = [
        (TIPO_ENTRADA, 'Entrada'),
        (TIPO_SALIDA, 'Salida'),
    ]

    # ---------- Motivos ----------
    MOTIVO_INICIAL    = 'inicial'
    MOTIVO_COMPRA     = 'compra'
    MOTIVO_VENTA      = 'venta'
    MOTIVO_AJUSTE     = 'ajuste'
    MOTIVO_MERMA      = 'merma'
    MOTIVO_DEVOLUCION = 'devolucion'

    MOTIVOS = [
        (MOTIVO_INICIAL,    'Stock inicial'),
        (MOTIVO_COMPRA,     'Compra a proveedor'),
        (MOTIVO_VENTA,      'Venta'),
        (MOTIVO_AJUSTE,     'Ajuste de inventario'),
        (MOTIVO_MERMA,      'Merma / pérdida'),
        (MOTIVO_DEVOLUCION, 'Devolución'),
    ]

    # ---------- Campos ----------
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='movimientos',
    )
    tipo = models.CharField(max_length=1, choices=TIPOS)
    motivo = models.CharField(
        max_length=20,
        choices=MOTIVOS,
        default=MOTIVO_AJUSTE,
    )
    detalle = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nota opcional: factura, cliente, etc.",
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "La cantidad debe ser al menos 1.")]
    )
    fecha = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos',
        help_text="Solo para entradas por compra a proveedor",
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        signo = '+' if self.tipo == self.TIPO_ENTRADA else '-'
        return f"{self.producto.nombre} {signo}{self.cantidad} ({self.get_motivo_display()})"

    # ---------- Validación de negocio ----------
    def clean(self):
        super().clean()

        # No dejar stock negativo en salidas
        if self.tipo == self.TIPO_SALIDA and self.producto_id:
            stock_antes = self.producto.stock_actual
            if self.cantidad > stock_antes:
                raise ValidationError({
                    'cantidad': (
                        f'No puedes sacar {self.cantidad}. '
                        f'Stock disponible: {stock_antes}.'
                    )
                })

        # Coherencia entre tipo y motivo
        motivos_entrada = {
            self.MOTIVO_INICIAL,
            self.MOTIVO_COMPRA,
            self.MOTIVO_DEVOLUCION,
        }
        motivos_salida = {
            self.MOTIVO_VENTA,
            self.MOTIVO_MERMA,
        }

        if self.tipo == self.TIPO_ENTRADA and self.motivo in motivos_salida:
            raise ValidationError({
                'motivo': f'El motivo "{self.get_motivo_display()}" no es válido para una entrada.'
            })

        if self.tipo == self.TIPO_SALIDA and self.motivo in motivos_entrada:
            raise ValidationError({
                'motivo': f'El motivo "{self.get_motivo_display()}" no es válido para una salida.'
            })

        if self.motivo == self.MOTIVO_COMPRA and not self.proveedor_id:
            raise ValidationError({
                'proveedor': 'Para una compra, indicá el proveedor.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

