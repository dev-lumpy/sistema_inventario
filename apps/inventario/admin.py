from django.contrib import admin
from django.db.models import Sum, Q
from django.utils.html import format_html
from .models import Categoria, Producto, MovimientoStock


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_productos')
    search_fields = ('nombre',)
    ordering = ('nombre',)

    @admin.display(description='Productos')
    def cantidad_productos(self, obj):
        return obj.productos.count()


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'categoria', 'precio_unitario',
        'stock_actual_display', 'stock_minimo', 'estado_alerta',
    )
    list_filter = ('categoria',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_select_related = ('categoria',)   # evita N+1 en la lista
    readonly_fields = ('creado',)

    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'categoria', 'precio_unitario')
        }),
        ('Stock', {
            'fields': ('stock_minimo',),
            'description': 'El stock actual se calcula a partir de los movimientos.'
        }),
        ('Auditoría', {
            'fields': ('creado',),
            'classes': ('collapse',),
        }),
    )

    # ---------- Mostrar el stock calculado ----------
    @admin.display(description='Stock actual', ordering='_stock')
    def stock_actual_display(self, obj):
        return obj.stock_actual

    # ---------- Semáforo de alerta ----------
    @admin.display(description='Estado')
    def estado_alerta(self, obj):
        if obj.en_alerta:
            return format_html(
                '<span style="color:white;background:#dc3545;'
                'padding:2px 8px;border-radius:4px;">⚠ Alerta</span>'
            )
        return format_html(
            '<span style="color:white;background:#28a745;'
            'padding:2px 8px;border-radius:4px;">✔ OK</span>'
        )

    # ---------- Optimizar: anotar el stock en la lista ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _stock=Sum('movimientos__cantidad')
        )


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = (
        'fecha', 'producto', 'tipo_badge', 'cantidad', 'motivo', 'detalle_corto',
    )
    list_filter = ('tipo', 'motivo', 'fecha', 'producto__categoria')
    search_fields = ('producto__nombre', 'detalle')
    ordering = ('-fecha',)
    list_select_related = ('producto',)
    date_hierarchy = 'fecha'
    autocomplete_fields = ('producto',)
    readonly_fields = ('fecha',)

    fieldsets = (
        (None, {
            'fields': ('producto', 'tipo', 'cantidad', 'motivo', 'detalle')
        }),
        ('Auditoría', {
            'fields': ('fecha',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Tipo', ordering='tipo')
    def tipo_badge(self, obj):
        if obj.tipo == MovimientoStock.TIPO_ENTRADA:
            return format_html(
                '<span style="color:white;background:#0d6efd;'
                'padding:2px 8px;border-radius:4px;">Entrada</span>'
            )
        return format_html(
            '<span style="color:white;background:#fd7e14;'
            'padding:2px 8px;border-radius:4px;">Salida</span>'
        )

    @admin.display(description='Detalle')
    def detalle_corto(self, obj):
        if not obj.detalle:
            return '—'
        return obj.detalle[:50] + ('…' if len(obj.detalle) > 50 else '')
