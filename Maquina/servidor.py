import socket
import threading
import pickle
import tkinter as tk


class Producto:
    def __init__(self, nombre, precio, cantidad, dona_fopre=False):
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
        self.dona_fopre = dona_fopre
        self.unidades_compradas = 0

    def comprar(self):
        if self.cantidad > 0:
            self.cantidad -= 1
            self.unidades_compradas += 1
            return self.precio
        else:
            raise ValueError(f"El producto {self.nombre} no está disponible.")


class MaquinaExpendedora:
    def __init__(self, productos):
        self.productos = productos
        self.credito = 0
        self.total_compras = 0
        self.total_donacion_fopre = 0

    def agregar_credito(self, monto):
        self.credito += monto
        return f"Se agregó ${monto:.2f} al crédito. Crédito actual: ${self.credito:.2f}"

    def comprar_producto(self, indice):
        try:
            producto = self.productos[indice - 1]
            if self.credito >= producto.precio:
                self.credito -= producto.precio
                self.total_compras += producto.comprar()
                if producto.dona_fopre:
                    self.total_donacion_fopre += producto.precio * 0.06
                return f"Compraste {producto.nombre}. Crédito restante: ${self.credito:.2f}"
            else:
                return f"Crédito insuficiente para comprar {producto.nombre}."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Producto no válido."

    def terminar_compra(self):
        cambio = self.credito
        self.credito = 0
        return f"Gracias por tu compra. Tu cambio es: ${cambio:.2f}"

    def obtener_informacion_productos(self):
        return [(p.nombre, p.precio, p.cantidad) for p in self.productos]


class ServidorMaquinaExpendedora:
    def __init__(self, root, productos):
        self.root = root
        self.root.title("Servidor - Máquina Expendedora")
        self.maquina = MaquinaExpendedora(productos)

        # Configuración del servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 65432))
        self.server_socket.listen()

        # Interfaz gráfica
        self.frame_estado = tk.Frame(root)
        self.frame_estado.pack(pady=10)

        self.label_estado = tk.Label(self.frame_estado, text="Estado del servidor:", font=("Arial", 14))
        self.label_estado.pack()

        self.text_estado = tk.Text(self.frame_estado, width=60, height=15, state='disabled')
        self.text_estado.pack()

        self.btn_iniciar = tk.Button(root, text="Iniciar Servidor", command=self.iniciar_servidor)
        self.btn_iniciar.pack(pady=10)

        self.btn_actualizar = tk.Button(root, text="Actualizar Estado", command=self.actualizar_estado)
        self.btn_actualizar.pack(pady=10)

    def iniciar_servidor(self):
        self.log("Servidor iniciado. Esperando conexiones...")
        threading.Thread(target=self.aceptar_conexiones, daemon=True).start()

    def aceptar_conexiones(self):
        while True:
            conn, addr = self.server_socket.accept()
            self.log(f"Conexión establecida con {addr}")
            threading.Thread(target=self.procesar_cliente, args=(conn,), daemon=True).start()

    def procesar_cliente(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                solicitud = pickle.loads(data)
                comando = solicitud.get("comando")
                respuesta = ""

                if comando == "mostrar_productos":
                    respuesta = self.maquina.obtener_informacion_productos()
                elif comando == "agregar_credito":
                    respuesta = self.maquina.agregar_credito(solicitud.get("monto", 0))
                elif comando == "comprar_producto":
                    respuesta = self.maquina.comprar_producto(solicitud.get("indice", 0))
                elif comando == "terminar_compra":
                    respuesta = self.maquina.terminar_compra()
                else:
                    respuesta = "Comando no reconocido."

                conn.sendall(pickle.dumps(respuesta))
            except Exception as e:
                conn.sendall(pickle.dumps(f"Error: {str(e)}"))
                break
        conn.close()

    def log(self, mensaje):
        self.text_estado.config(state='normal')
        self.text_estado.insert(tk.END, f"{mensaje}\n")
        self.text_estado.config(state='disabled')
        self.text_estado.see(tk.END)

    def actualizar_estado(self):
        self.log("Actualizando estado de la máquina...")
        for i, producto in enumerate(self.maquina.productos, start=1):
            self.log(f"{i}. {producto.nombre} - Precio: ${producto.precio:.2f}, Cantidad: {producto.cantidad}")


# Productos iniciales
productos = [
    Producto("Agua", 1000, 10, dona_fopre=True),
    Producto("Galletas", 1500, 5, dona_fopre=True),
    Producto("Chocolatina", 2000, 8),
    Producto("Coca-Cola", 2500, 6),
]

# Crear ventana del servidor
if __name__ == "__main__":
    root = tk.Tk()
    servidor = ServidorMaquinaExpendedora(root, productos)
    root.mainloop()
