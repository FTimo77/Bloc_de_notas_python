import sqlite3

class Task:
    def __init__(self, id=None, title=None, description=None, completed=False, label_name=None):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.label_name = label_name

    def __repr__(self):
        return f"ID: {self.id}, Título: {self.title}, Descripción: {self.description}, Completado: {self.completed}, Etiqueta: {self.label_name}"

class TaskService:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def add_task(self, task):
        self.cursor.execute("INSERT INTO tasks (title, description, completed, label_name) VALUES (?, ?, ?, ?)",
                            (task.title, task.description, task.completed, task.label_name))
        self.conn.commit()

    def add_label(self, labelname):
        self.cursor.execute("INSERT INTO labels (name) VALUES (?)", (labelname,))
        self.conn.commit()

    def get_all_labels(self):
        self.cursor.execute("SELECT id, name FROM labels")
        return self.cursor.fetchall()

    def get_label_name_by_id(self, label_id):
        self.cursor.execute("SELECT name FROM labels WHERE id = ?", (label_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_tasks(self):
        self.cursor.execute("SELECT id, title, description, completed, label_name FROM tasks")
        tasks = self.cursor.fetchall()
        return [Task(*task) for task in tasks]

    def get_incompleted_tasks(self):
        self.cursor.execute("SELECT id, title, description, completed, label_name FROM tasks WHERE completed = 0")
        tasks = self.cursor.fetchall()
        return [Task(*task) for task in tasks]

    def mark_task_as_completed(self, task_id):
        self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()

    def delete_task(self, task_id):
        try:
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            return True
        except sqlite3.DatabaseError as e:  # Captura errores específicos de SQLite
            print(f"Error al eliminar la tarea con ID {task_id}: {e}")
            return False
        except Exception as e:  # Captura cualquier otro error inesperado
            print(f"Error inesperado: {e}")
            return False

    def update_task(self, task):
        self.cursor.execute("UPDATE tasks SET title = ?, description = ?, completed = ?, label_name = ? WHERE id = ?",
                            (task.title, task.description, task.completed, task.label_name, task.id))
        self.conn.commit()

class App:
    def __init__(self):
        self.task_service = None
        self.conn = None

    def main(self):
        try:
            self.conn = self.get_connection()
            self.task_service = TaskService(self.conn)

            print("------------Bienvenido a su Gestor de Tareas----------------")
            self.mostrar_menu()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if self.conn:
                self.conn.close()

    def get_connection(self):
        return sqlite3.connect('task_manager.db')

    def mostrar_tareas_pendientes(self):
        print("Sus Tareas son:")
        tasks = self.task_service.get_all_tasks()
        for task in tasks:
            print(task)

    def mostrar_menu(self):
        while True:
            print("\n---------------Menú de opciones:-------------\n"
                  "1 - Crear Tareas\n"
                  "2 - Crear Etiquetas\n"
                  "3 - Marcar como completado\n"
                  "4 - Eliminar Tareas\n"
                  "5 - Actualizar Tarea\n"
                  "6 - Mostrar Tareas Completadas\n"
                  "7 - Mostrar Todas las Tareas\n"
                  "0 - Salir")

            user_input = input("Seleccione una opción: ")

            if user_input == '1':
                self.crear_tarea()
            elif user_input == '2':
                self.crear_etiqueta()
            elif user_input == '3':
                self.marcar_tarea_como_completada()
            elif user_input == '4':
                self.eliminar_tarea()
            elif user_input == '5':
                self.actualizar_tarea()
            elif user_input == '6':
                self.mostrar_tareas_completadas()
            elif user_input == '7':
                self.mostrar_todas_las_tareas()
            elif user_input == '0':
                print("Saliendo del gestor de tareas. ¡Adiós!")
                break
            else:
                print("Opción no válida.")

    def crear_tarea(self):
        title = input("--Ingrese el título de la tarea: ")
        description = input("Ingrese la descripción de la tarea: ")

        print("Seleccione una etiqueta de la siguiente lista:")
        labels = self.task_service.get_all_labels()
        for label in labels:
            print(label)

        label_id = int(input("Ingrese el ID de la etiqueta: "))
        label_name = self.task_service.get_label_name_by_id(label_id)

        task = Task(title=title, description=description, label_name=label_name)
        self.task_service.add_task(task)
        print("La tarea ha sido creada exitosamente.")

    def crear_etiqueta(self):
        labelname = input("Ingresa el nombre de la etiqueta que quieres crear: ")
        self.task_service.add_label(labelname)
        print("La etiqueta ha sido creada exitosamente.")

    def marcar_tarea_como_completada(self):
        print("¿Qué tarea deseas marcar como completada?")
        self.mostrar_tareas_pendientes()

        completed = int(input("Ingrese el ID de la tarea: "))
        self.task_service.mark_task_as_completed(completed)
        print("La tarea ha sido marcada como completada.")

    def eliminar_tarea(self):
        print("¿Qué tarea deseas eliminar?")
        self.mostrar_tareas_pendientes()

        deleted = int(input("Ingrese el ID de la tarea: "))
        self.task_service.delete_task(deleted)
        print("La tarea ha sido eliminada.")

    def actualizar_tarea(self):
        print("¿Qué tarea deseas actualizar?")
        self.mostrar_tareas_pendientes()

        id_updated = int(input("Ingrese el ID de la tarea: "))
        title = input("--Ingrese el título de la tarea: ")
        description = input("Ingrese la descripción de la tarea: ")

        task = Task(id=id_updated, title=title, description=description, completed=False, label_name="Education")
        self.task_service.update_task(task)
        print("La tarea ha sido actualizada.")

    def mostrar_tareas_completadas(self):
        completed_tasks = self.task_service.get_incompleted_tasks()

        if not completed_tasks:
            print("No hay tareas incompletas.")
        else:
            print("Tareas incompletas:")
            for task in completed_tasks:
                print(task)

    def mostrar_todas_las_tareas(self):
        self.mostrar_tareas_pendientes()


def crear_tablas():
    conn = sqlite3.connect('task_manager.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS labels (
                        id INTEGER PRIMARY KEY,
                        name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        completed BOOLEAN,
                        label_name TEXT)''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    crear_tablas()
    App().main()
