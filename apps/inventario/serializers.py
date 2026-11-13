# apps/inventario/serializers.py
from django.db import transaction
from rest_framework import serializers
from apps.inventario.models import (
    Categoria,
    Producto,
    Proveedor,
    MovimientoStock,
)
from apps.usuarios.models import AdministradorORM


class CategoriaSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class ProductoSelectSerializer(serializers.ModelSerializer):
    stock_actual = serializers.ReadOnlyField()

    class Meta:
        model  = Producto
        fields = ['id', 'nombre', 'categoria', 'precio_unitario', 'stock_minimo', 'activo', 'stock_actual', 'administrador']
        read_only_fields = ['administrador']



class MovimientoHistorialMovimientoSerializer(serializers.ModelSerializer):
    # Categoría: FK en Producto → la aplanamos al nombre
    categoria = serializers.CharField(source='producto.categoria.nombre', read_only=True)

    # Proveedor: puede ser null → devolvemos "—" en ese caso
    proveedor = serializers.SerializerMethodField()

    # Fecha: la formateamos como ISO para que JS la parsee fácil
    fecha = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)

    # Para saber de que producto se trata en la edicion que acabamos de hacer
    producto = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = MovimientoStock
        fields = ['id', 'categoria', 'cantidad', 'proveedor', 'producto', 'fecha']

    def get_proveedor(self, obj):
        return obj.proveedor.nombre if obj.proveedor_id else '—'


class ProductoSelectNameSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'categoria']



class ProductoCreateSerializer(serializers.ModelSerializer):
    cantidad_inicial = serializers.IntegerField(
        write_only=True,
        min_value=1,
        help_text="Cantidad con la que arranca el producto.",
    )
    administrador = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'categoria',
            'precio_unitario',
            'stock_minimo',
            'cantidad_inicial',
            'administrador',
        ]
        read_only_fields = ['id', 'administrador']

    def _obtener_administrador(self):
        request = self.context.get('request')
        usuario = getattr(request, 'user', None)

        if not usuario or not usuario.is_authenticated:
            raise serializers.ValidationError({
                'administrador': 'Debés iniciar sesión como administrador.',
            })

        try:
            return AdministradorORM.objects.get(pk=usuario.pk)
        except AdministradorORM.DoesNotExist:
            raise serializers.ValidationError({
                'administrador': 'Solo un administrador puede crear productos.',
            })

    @transaction.atomic
    def create(self, validated_data):
        cantidad = validated_data.pop('cantidad_inicial')
        administrador = self._obtener_administrador()

        producto = Producto.objects.create(
            administrador=administrador,
            **validated_data,
        )

        MovimientoStock.objects.create(
            producto=producto,
            tipo=MovimientoStock.TIPO_ENTRADA,
            motivo=MovimientoStock.MOTIVO_INICIAL,
            cantidad=cantidad,
            detalle='Stock inicial',
        )

        return producto


class ProveedorSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre']


class EntradaStockSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True),
        error_messages={
            'required': 'Elegí un producto.',
            'does_not_exist': 'Producto no encontrado.',
            'incorrect_type': 'ID de producto inválido.',
        },
    )
    cantidad = serializers.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Ingresá una cantidad.',
            'min_value': 'La cantidad debe ser mayor a cero.',
            'invalid': 'La cantidad debe ser un número entero.',
        },
    )
    proveedor = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.filter(activo=True),
        error_messages={
            'required': 'Elegí un proveedor.',
            'does_not_exist': 'Proveedor no encontrado.',
            'incorrect_type': 'ID de proveedor inválido.',
        },
    )


class MovimientoHistorialSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='producto.nombre', read_only=True)
    proveedor = serializers.CharField(source='proveedor.nombre', read_only=True, allow_null=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    motivo_display = serializers.CharField(source='get_motivo_display', read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'fecha',
            'producto', 'proveedor',
            'tipo', 'tipo_display',
            'motivo', 'motivo_display',
            'cantidad', 'detalle',
        ]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']
        read_only_fields = ['id']


class SalidaStockSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True),
        error_messages={'required': 'Elegí un producto.', 'does_not_exist': 'Producto no encontrado.'},
    )
    cantidad = serializers.IntegerField(
        min_value=1,
        error_messages={'min_value': 'La cantidad debe ser mayor a cero.'},
    )
    canal_venta = serializers.ChoiceField(
        choices=MovimientoStock.CANALES,
        error_messages={'required': 'Elegí un canal.', 'invalid_choice': 'Canal inválido.'},
    )


class ProductoMasVendidoSerializer(serializers.ModelSerializer):
    cantidad_vendida = serializers.IntegerField(read_only=True)

    class Meta:
        model = Producto
        fields = ["nombre", "cantidad_vendida"]


class ProductoVendidoEnRangoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    cantidad_vendida = serializers.IntegerField()
