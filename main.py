#libreria para crear las ventanas
import tkinter as tk
#llama herramientas de deseño para botones y tablas 
from tkinter import ttk, messagebox, simpledialog
#llama la base de datos creada en el otro documento
from database import FarmaciaDB
#llama los estilos creados en el otro documento
import styles

class FarmaciaComunalApp:
    def __init__(self, root):
        self.db = FarmaciaDB()
        self.root = root
        self.root.title("Sistema Farmacia Comunal")
        self.root.geometry("1150x600")
        self.root.configure(bg=styles.COLOR_FONDO)

        # Configuración de estilos ttk
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        
        style.configure("Treeview", 
                        background=styles.COLOR_SECUNDARIO,
                        foreground=styles.COLOR_TEXTO,
                        rowheight=30,
                        fieldbackground=styles.COLOR_SECUNDARIO,
                        font=styles.FUENTE_NORMAL,
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=styles.COLOR_PRIMARIO, 
                        foreground="white", 
                        font=styles.FUENTE_NEGRITA,
                        padding=5)
        style.map("Treeview.Heading", background=[('active', styles.COLOR_PRIMARIO)])
        style.map("Treeview", background=[("selected", styles.COLOR_ACCION)])

        # Credenciales trabajadores
        self.users = {
            "bodega": 
            {
                "usuario": "juan", 
                "contraseña": "1234"
            },
            "entrega": 
            {
                "usuario": "carlos", 
                "contraseña": "4567"
            }
        }
        #llama la funcion que dibuja los botones y la tabla
        self.create_widgets()
        #actualiza la tabla con los datos de los medicamentos de la base de datos
        self.actualizar_tabla()

    def login(self, tipo_acceso):
        # validador de usuario y contraseña
        user = simpledialog.askstring("Ingrese el Usuario", f"Usuario para {tipo_acceso}:", parent=self.root)
        password = simpledialog.askstring("Ingrese la Contraseña", f"Contraseña para {tipo_acceso}:", show='*', parent=self.root)
        
        credenciales = self.users[tipo_acceso]
        if user == credenciales["usuario"] and password == credenciales["contraseña"]:
            return True
        else:
            messagebox.showerror("Error al ingresar", "Usuario o contraseña incorrectos")
            return False

    def create_widgets(self):
        # SECCIÓN DE BODEGA

        # Módulo de la bodega (como esta costruido todo el campo de la grilla bodega)
        frame_ingreso = tk.LabelFrame(self.root, text="Ingreso de medicamentos a la bodega", bg=styles.COLOR_FONDO, font=styles.STYLE_CONFIG["font_title"])
        frame_ingreso.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_ingreso, text="Nombre:", font=styles.FUENTE_NEGRITA, bg=styles.COLOR_FONDO).grid(row=0, column=0, padx=5)
        self.ent_nombre = tk.Entry(frame_ingreso)
        self.ent_nombre.grid(row=0, column=1, padx=5)

        tk.Label(frame_ingreso, text="Cantidad:", font=styles.FUENTE_NEGRITA, bg=styles.COLOR_FONDO).grid(row=0, column=2, padx=5)
        self.ent_cantidad = tk.Entry(frame_ingreso)
        self.ent_cantidad.grid(row=0, column=3, padx=5)

        tk.Label(frame_ingreso, text="Vencimiento:", font=styles.FUENTE_NEGRITA, bg=styles.COLOR_FONDO).grid(row=0, column=4, padx=5)
        self.ent_fecha = tk.Entry(frame_ingreso)
        self.ent_fecha.grid(row=0, column=5, padx=5)

        tk.Label(frame_ingreso, text="Laboratorio:", font=styles.FUENTE_NEGRITA, bg=styles.COLOR_FONDO).grid(row=0, column=6, padx=5)
        self.ent_marca = tk.Entry(frame_ingreso)
        self.ent_marca.grid(row=0, column=7, padx=5)

        btn_guardar = tk.Button(frame_ingreso, text="Ingreso a Bodega", command=self.guardar_datos, bg=styles.COLOR_ACCION, fg="white", font=styles.FUENTE_NEGRITA, relief="flat", cursor="hand2", padx=10, pady=2)
        btn_guardar.grid(row=0, column=8, padx=10, pady=10)

        # grilla que muestra toda la información de los medicamentos ingresados en la tabla
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Stock", "Vencimiento","Marca"), show="headings")
        # titulos de los encabezados
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Medicamento")
        self.tree.heading("Stock", text="Unidades Disponibles")
        self.tree.heading("Vencimiento", text="fecha de vencimiento")
        self.tree.heading("Marca", text="Laboratorio")
        # centra el contenido de la grilla que muestra toda la información de los medicamentos ingresados en la tabla
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=200, anchor="center")
        self.tree.column("Stock", width=150, anchor="center")
        self.tree.column("Vencimiento", width=150, anchor="center")
        self.tree.column("Marca", width=150, anchor="center")

        # define el tamaño de la grilla (se estira a lo ancho y largo de la pantalla)
        self.tree.pack(fill="both", expand=True, padx=20)

        # SECCIÓN DE ENTREGA

        # Módulo de entrega (como esta costruido todo el campo de la grilla entrega)
        frame_entrega = tk.LabelFrame(self.root, text="Entrega de medicamentos al publico", bg=styles.COLOR_FONDO, font=styles.STYLE_CONFIG["font_title"])
        frame_entrega.pack(fill="x", padx=20, pady=10)
        # boton de entrega
        btn_entregar = tk.Button(frame_entrega, text="Entrega de medicamentos", command=self.procesar_entrega, bg=styles.COLOR_PRIMARIO, fg="white", font=styles.FUENTE_NEGRITA, relief="flat", cursor="hand2", padx=15, pady=8)
        btn_entregar.pack(side="left", padx=20, pady=15)
        # boton de alerta de medicamentos
        btn_alertas = tk.Button(frame_entrega, text="Verificación de medicamentos", command=self.mostrar_alertas, bg=styles.COLOR_ALERTA, fg="white", font=styles.FUENTE_NEGRITA, relief="flat", cursor="hand2", padx=15, pady=8)
        btn_alertas.pack(side="right", padx=20, pady=15)

    def guardar_datos(self):
        # validar acceso de bodega de medicamentos
        if not self.login("bodega"):
            return

        if self.ent_nombre.get() and self.ent_cantidad.get():
            self.db.registrar_medicamento(self.ent_nombre.get(), int(self.ent_cantidad.get()), self.ent_fecha.get(), self.ent_marca.get())
            messagebox.showinfo("Éxito", "Medicamento registrado en bodega")
            self.actualizar_tabla()
            # Limpiar campos tras guardar
            self.ent_nombre.delete(0, tk.END)
            self.ent_cantidad.delete(0, tk.END)
            self.ent_fecha.delete(0, tk.END)
            self.ent_marca.delete(0, tk.END)
        else:
            messagebox.showwarning("Campos incompletos", "Porfavor llenar todos los campos")

    def actualizar_tabla(self):
        # consulta y borra los registros de la tabla viejos
        for item in self.tree.get_children():
            self.tree.delete(item)
        # inserta los nuevos registros en la tabla
        for fila in self.db.obtener_todo():
            self.tree.insert("", "end", values=fila)

    def procesar_entrega(self):
        # revisa si el usuario esta seleccionando un medicamento
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Porfavor seleccione un medicamento de la lista")
            return
        
        # solicita credencial de usuario para entregar
        if not self.login("entrega de medicamentos"):
            return
         # selecciona el medicamento por el ID y le resta de a 1 unidad
        item_id = self.tree.item(selected)['values'][0]
        exito, nuevo_stock = self.db.entregar_medicamento(item_id, 1)
        
        if exito:
            messagebox.showinfo("Entrega", "Medicamento entregado con exito" + "\n" + f"Quedan {nuevo_stock} unidades en inventario.")
            self.actualizar_tabla()
        else:
            messagebox.showerror("No hay unidades suficiente")

    def mostrar_alertas(self):
        alertas = self.db.alertas_criticas()
        if not alertas:
            messagebox.showinfo("Reporte", "No hay medicamentos por vencer o agotarse.")
            return
        
        mensaje = "PRODUCTOS CON POCO STOCK O POR VENCER:\n\n"
        for a in alertas:
            mensaje += f"* Medicamento:{a[0]} {a[1]} unidades (Vence: {a[2]})\n"
        messagebox.showwarning("Alerta de Inventario", mensaje)

if __name__ == "__main__":
    root = tk.Tk()
    app = FarmaciaComunalApp(root)
    root.mainloop()