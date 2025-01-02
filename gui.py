import customtkinter
from App import TaskService
from App import Task
import sqlite3

class TaskManagerApp:
    def __init__(self):
        # Configuración de la ventana principal
        self.root = customtkinter.CTk()
        self.root.title("Gestor de Tareas")
        self.root.geometry("800x600")

        # Configuración del diseño
        self.root.columnconfigure(0, weight=1)  # Columna de botones (izquierda)
        self.root.columnconfigure(1, weight=3)  # Columna de notas (derecha)
        self.root.rowconfigure(0, weight=1)     # Relleno superior
        self.root.rowconfigure(1, weight=10)    # Contenido principal

        # Conexión con la base de datos y el servicio de tareas
        self.conn = sqlite3.connect("task_manager.db")
        self.task_service = TaskService(self.conn)

        # Crear la interfaz inicial
        self.crear_menu_izquierdo()
        self.mostrar_tareas()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def crear_menu_izquierdo(self):
        # Frame para los botones del menú
        self.menu_frame = customtkinter.CTkFrame(self.root)
        self.menu_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        # Título del menú
        customtkinter.CTkLabel(self.menu_frame, text="Gestor de Tareas", font=("Arial", 24)).pack(pady=20)

        # Botones del menú
        customtkinter.CTkButton(self.menu_frame, text="Crear Tarea", command=self.abrir_formulario_crear_tarea).pack(fill="x", pady=5)
        customtkinter.CTkButton(self.menu_frame, text="Crear Etiqueta", command=self.abrir_formulario_crear_etiqueta).pack(fill="x", pady=5)
        customtkinter.CTkButton(self.menu_frame, text="Actualizar Tareas", command=self.mostrar_tareas).pack(fill="x", pady=5)
        customtkinter.CTkButton(self.menu_frame, text="Eliminar Tareas", command=self.eliminar_tareas).pack(fill="x", pady=5)
        customtkinter.CTkButton(self.menu_frame, text="Salir", command=self.on_closing).pack(fill="x", pady=5)

    def eliminar_tareas(self):
        # Limpiar el área derecha antes de mostrar las tareas y el formulario
        for widget in self.root.grid_slaves(column=1):
            widget.destroy()

        # Frame para mostrar las tareas
        tareas_frame = customtkinter.CTkFrame(self.root)
        tareas_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        # Mostrar todas las tareas
        tareas = self.task_service.get_all_tasks()

        if tareas:
            # Mostrar cada tarea en un label
            customtkinter.CTkLabel(tareas_frame, text="Tareas disponibles (ID - Título):", font=("Arial", 16)).pack(
                pady=10)
            for idx, tarea in enumerate(tareas):
                tarea_texto = f"{tarea.id} - {tarea.title}"
                customtkinter.CTkLabel(tareas_frame, text=tarea_texto, anchor="w").pack(fill="x", pady=5, padx=10)
        else:
            customtkinter.CTkLabel(tareas_frame, text="No hay tareas creadas.", font=("Arial", 16)).pack(pady=20)
            return

        # Campo para ingresar el ID de la tarea a eliminar
        customtkinter.CTkLabel(tareas_frame, text="Ingresa el ID de la tarea a eliminar:").pack(pady=10, padx=5)
        id_entry = customtkinter.CTkEntry(tareas_frame, placeholder_text="ID de la tarea")
        id_entry.pack(pady=5, padx=5)

        # Función para eliminar la tarea
        def confirmar_eliminacion():
            tarea_id = id_entry.get()
            if tarea_id.isdigit():
                tarea_id = int(tarea_id)
                if self.task_service.delete_task(
                        tarea_id):  # Asegúrate de que `delete_task` devuelva True si se elimina correctamente
                    self.mostrar_tareas()
                else:
                    customtkinter.CTkLabel(tareas_frame, text="Error: No se encontró la tarea con ese ID.",
                                           fg_color="red").pack(pady=5)
            else:
                customtkinter.CTkLabel(tareas_frame, text="Error: Ingresa un ID válido.", fg_color="red").pack(pady=5)

        # Botón para confirmar la eliminación
        customtkinter.CTkButton(tareas_frame, text="Eliminar Tarea", command=confirmar_eliminacion).pack(pady=10)

    def mostrar_tareas(self):
        # Limpiar el área derecha antes de mostrar las tareas
        for widget in self.root.grid_slaves(column=1):
            widget.destroy()

        # Frame para mostrar las tareas
        tareas_frame = customtkinter.CTkFrame(self.root)
        tareas_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        tareas = self.task_service.get_all_tasks()

        if tareas:
            # Mostrar cada tarea en un label
            for idx, tarea in enumerate(tareas):
                customtkinter.CTkLabel(tareas_frame, text=str(tarea), anchor="w").pack(fill="x", pady=5, padx=10)
        else:
            # Mostrar un mensaje si no hay tareas
            customtkinter.CTkLabel(tareas_frame, text="No hay tareas creadas.", font=("Arial", 16)).pack(pady=20)

    def abrir_formulario_crear_tarea(self):
        # Limpiar el área derecha para mostrar el formulario
        for widget in self.root.grid_slaves(column=1):
            widget.destroy()

        # Frame para el formulario de crear tarea
        formulario_frame = customtkinter.CTkFrame(self.root)
        formulario_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        customtkinter.CTkLabel(formulario_frame, text="Título de la tarea:").pack(pady=5, padx=5)
        titulo_entry = customtkinter.CTkEntry(formulario_frame)
        titulo_entry.pack(pady=5, padx=5)

        customtkinter.CTkLabel(formulario_frame, text="Descripción de la tarea:").pack(pady=5, padx=5)
        descripcion_entry = customtkinter.CTkEntry(formulario_frame)
        descripcion_entry.pack(pady=5, padx=5)

        customtkinter.CTkLabel(formulario_frame, text="Etiqueta:").pack(pady=5, padx=5)
        etiqueta_entry = customtkinter.CTkEntry(formulario_frame)
        etiqueta_entry.pack(pady=5, padx=5)

        def guardar_tarea():
            titulo = titulo_entry.get()
            descripcion = descripcion_entry.get()
            etiqueta = etiqueta_entry.get()
            if titulo and descripcion and etiqueta:
                self.task_service.add_task(Task(title=titulo, description=descripcion, label_name=etiqueta))
                self.mostrar_tareas()

        customtkinter.CTkButton(formulario_frame, text="Guardar", command=guardar_tarea).pack(pady=10)
        customtkinter.CTkButton(formulario_frame, text="Cancelar", command=self.mostrar_tareas).pack(pady=5)

    def abrir_formulario_crear_etiqueta(self):
        # Similar al formulario de crear tarea pero para etiquetas
        for widget in self.root.grid_slaves(column=1):
            widget.destroy()

        formulario_frame = customtkinter.CTkFrame(self.root)
        formulario_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        customtkinter.CTkLabel(formulario_frame, text="Nombre de la etiqueta:").pack(pady=5, padx=5)
        nombre_entry = customtkinter.CTkEntry(formulario_frame)
        nombre_entry.pack(pady=5, padx=5)

        def guardar_etiqueta():
            nombre = nombre_entry.get()
            if nombre:
                self.task_service.add_label(nombre)
                self.mostrar_tareas()

        customtkinter.CTkButton(formulario_frame, text="Guardar", command=guardar_etiqueta).pack(pady=10)
        customtkinter.CTkButton(formulario_frame, text="Cancelar", command=self.mostrar_tareas).pack(pady=5)

    def on_closing(self):
        # Cerrar la aplicación y la conexión a la base de datos
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    TaskManagerApp()
