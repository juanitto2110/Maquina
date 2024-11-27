import socket
import pickle
import tkinter as tk
from tkinter import messagebox, simpledialog


def enviar_solicitud(comando, parametros=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65432))
            solicitud = {"comando": comando}
            if parametros:
                solicitud.update(parametros)
            s.sendall(pickle.dumps(solicitud))
            data = s.recv(1024)
            return pickle.loads(data)
    except Exception as e:
        return f"Error al conectar con el servidor: {str(e)}"


class MaquinaExpendedoraCliente:
    def __init__(self, root):
        self.root = root
        self.root.title("Máquina Expendedora")
        self.credito = 0

        # Secciones de la interfaz
        self.frame_productos = tk.Frame(root)
        self.frame_productos.pack(pady=10)

        self.frame_control = tk.Frame(root)
        self.frame_control.pack(pady=10)

        self.label_credito = tk.Label(self.frame_control, text=f"Crédito: ${self.credito:.2f}", font=("Arial", 12))
        self.label_credito.pack()

        self.btn_agregar_credito = tk.Button(self.frame_control, text="Agregar Crédito", command=self.agregar_credito)
        self.btn_agregar_credito.pack(pady=5)

        self.btn_mostrar_productos = tk.Button(self.frame_control, text="Mostrar Productos", command=self.mostrar_productos)
        self.btn_mostrar_productos.pack(pady=5)

        self.btn_comprar_producto = tk.Button(self.frame_control, text="Comprar Producto", command=self.comprar_producto)
        self.btn_comprar_producto.pack(pady=5)

        self.btn_terminar_compra = tk.Button(self.frame_control, text="Terminar Compra", command=self.terminar_compra)
        self.btn_terminar_compra.pack(pady=5)

        self.productos = []

    def mostrar_productos(self):
        respuesta = enviar_solicitud("mostrar_productos")
        if isinstance(respuesta, list):
            self.productos = respuesta
            for widget in self.frame_productos.winfo_children():
                widget.destroy()
            tk.Label(self.frame_productos, text="Productos Disponibles:", font=("Arial", 12)).pack()
            for i, (nombre, precio, cantidad) in enumerate(self.productos, start=1):
                tk.Label(self.frame_productos, text=f"{i}. {nombre} - Precio: ${precio:.2f}, Cantidad: {cantidad}",
                         font=("Arial", 10)).pack()
        else:
            messagebox.showerror("Error", respuesta)

    def agregar_credito(self):
        monto = simpledialog.askfloat("Agregar Crédito", "Ingrese el monto a agregar:")
        if monto and monto > 0:
            respuesta = enviar_solicitud("agregar_credito", {"monto": monto})
            if "Crédito actual" in respuesta:
                self.credito = float(respuesta.split(":")[1].strip().strip("$"))
                self.label_credito.config(text=f"Crédito: ${self.credito:.2f}")
            messagebox.showinfo("Información", respuesta)
        else:
            messagebox.showerror("Error", "Monto inválido.")

    def comprar_producto(self):
        if not self.productos:
            messagebox.showerror("Error", "Primero debe mostrar los productos.")
            return
        indice = simpledialog.askinteger("Comprar Producto", "Ingrese el número del producto a comprar:")
        if indice and 1 <= indice <= len(self.productos):
            respuesta = enviar_solicitud("comprar_producto", {"indice": indice})
            if "Crédito restante" in respuesta:
                self.credito = float(respuesta.split(":")[1].strip().strip("$"))
                self.label_credito.config(text=f"Crédito: ${self.credito:.2f}")
            messagebox.showinfo("Información", respuesta)
            self.mostrar_productos()
        else:
            messagebox.showerror("Error", "Índice inválido.")

    def terminar_compra(self):
        respuesta = enviar_solicitud("terminar_compra")
        if "Tu cambio es" in respuesta:
            self.credito = 0
            self.label_credito.config(text=f"Crédito: ${self.credito:.2f}")
        messagebox.showinfo("Información", respuesta)


# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = MaquinaExpendedoraCliente(root)
    root.mainloop()
