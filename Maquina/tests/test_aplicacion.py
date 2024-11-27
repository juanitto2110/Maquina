from flask import Flask, jsonify, request

app = Flask(__name__)

# Estado inicial del servidor
productos = [
    {"id": 1, "nombre": "Agua", "precio": 1000, "cantidad": 10, "dona_fopre": True},
    {"id": 2, "nombre": "Galletas", "precio": 1500, "cantidad": 5, "dona_fopre": True},
    {"id": 3, "nombre": "Chocolatina", "precio": 2000, "cantidad": 8, "dona_fopre": False},
    {"id": 4, "nombre": "Coca-Cola", "precio": 2500, "cantidad": 6, "dona_fopre": False},
]

# Ruta para obtener la lista de productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    return jsonify(productos)

# Ruta para comprar un producto
@app.route('/comprar/<int:producto_id>', methods=['POST'])
def comprar_producto(producto_id):
    for producto in productos:
        if producto["id"] == producto_id:
            if producto["cantidad"] > 0:
                producto["cantidad"] -= 1
                return jsonify({"mensaje": f"Producto {producto['nombre']} comprado exitosamente."})
            else:
                return jsonify({"error": f"Producto {producto['nombre']} no disponible."}), 400
    return jsonify({"error": "Producto no encontrado."}), 404

if __name__ == "__main__":
    app.run(debug=True)
