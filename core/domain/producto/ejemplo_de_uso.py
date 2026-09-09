from domain.producto import (
    Producto,
    ProductoId,
    NombreProducto,
    CategoriaProducto,
    Precio,
    Cantidad,
    StockMinimo
)

# ============ Crear un producto ============
try:
    producto = Producto(
        id=ProductoId("123e4567-e89b-12d3-a456-426614174000"),
        nombre=NombreProducto("Laptop Gamer Pro"),
        categoria=CategoriaProducto.ELECTRONICA,
        precio=Precio(1500.99),
        cantidad_inicial=Cantidad(50),
        stock_minimo=StockMinimo(10)
    )
    
    print(f"✅ Producto registrado: {producto}")
    print(f"📊 ¿En alertas? {producto.esta_en_alertas()}")  # False (50 > 10)
    
    # ============ Vender 5 unidades ============
    producto.reducir_stock(5)
    print(f"📦 Stock después de venta: {producto.cantidad.valor}")  # 45
    
    # ============ Verificar alerta ============
    print(f"📊 ¿En alertas? {producto.esta_en_alertas()}")  # False (45 > 10)
    
    # ============ Vender hasta alerta ============
    producto.reducir_stock(35)  # Queda en 10
    print(f"📦 Stock después de venta: {producto.cantidad.valor}")  # 10
    print(f"🚨 ¿En alertas? {producto.esta_en_alertas()}")  # True
    
except Exception as e:
    print(f"❌ Error: {e}")
