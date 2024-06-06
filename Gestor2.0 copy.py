import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QFileDialog, QMessageBox, QWidget, QFormLayout, QDialog
from PyQt6.QtCore import Qt
import os
from pathlib import Path
from datetime import datetime

class Task:
    def __init__(self, category, task_id, description, due_date, priority, status):
        self.category = category
        self.task_id = task_id
        self.description = description
        self.due_date = datetime.strptime(due_date, '%Y/%m/%d')
        self.priority = priority
        self.status = status
"""
Comportamiento modal:
Un diálogo modal bloquea la interacción con la ventana principal hasta que se cierra el diálogo, lo que es útil para asegurarse de que el usuario complete la tarea (como introducir datos) antes de continuar con otras partes de la aplicación.
Gestión de botones estándar:
QDialog proporciona métodos y señales estándar para manejar los botones de aceptación (OK, Aceptar, etc.) y cancelación (Cancelar, Close, etc.), facilitando la implementación de estas acciones.
Control del flujo de la aplicación:
Los diálogos permiten pausar el flujo de la aplicación hasta que el usuario complete una acción específica. Esto es esencial para formularios de entrada de datos, como en el caso de TaskDialog.
Facilidad de uso:
PyQt proporciona varios métodos y propiedades integradas en QDialog que simplifican la creación y gestión de diálogos, incluyendo la captura de la respuesta del usuario (Accepted o Rejected).
"""
class TaskDialog(QDialog):
    def __init__(self, parent, categories):
        super().__init__(parent)
        self.categories = categories
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Add Task")
        layout = QFormLayout(self)

        self.task_input = QLineEdit(self)
        self.due_date_input = QLineEdit(self)
        self.priority_input = QLineEdit(self)
        self.status_input = QLineEdit(self)
        self.category_combo = QComboBox(self)
        for category in self.categories:
            self.category_combo.addItem(category)

        layout.addRow("Description:", self.task_input)
        layout.addRow("Due Date:", self.due_date_input)
        layout.addRow("Priority:", self.priority_input)
        layout.addRow("Status:", self.status_input)
        layout.addRow("Category:", self.category_combo)

        add_btn = QPushButton("Add Task", self)
        add_btn.clicked.connect(self.accept)
        layout.addRow(add_btn)

        self.setLayout(layout)

    def get_task_data(self):
        return {
            "description": self.task_input.text(),
            "due_date": self.due_date_input.text(),
            "priority": self.priority_input.text(),
            "status": self.status_input.text(),
            "category": self.category_combo.currentText()
        }

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setGeometry(100, 100, 800, 600)
        
        self.categories = []
        self.tasks = []
        
        self.initUI()
        self.load_tasks_from_file(r'C:\Users\carlo\OneDrive\Documentos\GitHub\POO2024\Tercer Parcial\Tareas.txt')
        
    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Category Input Layout
        input_layout = QHBoxLayout()
        self.category_combo = QComboBox(self)
        self.category_combo.currentIndexChanged.connect(self.filter_tasks_by_category)
        
        add_category_btn = QPushButton("Add Category", self)
        add_category_btn.clicked.connect(self.add_category)
        
        add_task_btn = QPushButton("Add Task", self)
        add_task_btn.clicked.connect(self.open_task_dialog)
        
        input_layout.addWidget(QLabel("Category:"))
        input_layout.addWidget(self.category_combo)
        input_layout.addWidget(add_category_btn)
        input_layout.addWidget(add_task_btn)
        
        # Task List Layout
        self.task_list = QListWidget(self)
        
        # Save Button
        save_btn = QPushButton("Save as CSV", self)
        save_btn.clicked.connect(self.save_tasks)
        
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.task_list)
        main_layout.addWidget(save_btn)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
      
        
    def add_task(self):
        task_description = self.task_input.text().strip()
        if task_description:
            category_name = self.category_combo.currentText()
            task_id = len(self.tasks) + 1
            due_date = "2024/12/31"  # Default due date (modify as needed)
            priority = "Medium"  # Default priority (modify as needed)
            status = "Pending"  # Default status (modify as needed)
            task = Task(category_name, task_id, task_description, due_date, priority, status)
            self.tasks.append(task)
            self.filter_tasks_by_category()  # Refresh the task list to show the new task
            self.task_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Task description cannot be empty!")
    
    def add_category(self):
          # ok: Un valor booleano que indica si el usuario hizo clic en "OK" o en "Cancelar". Si el usuario hace clic en "OK", ok será True. Si el usuario hace clic en "Cancelar" o cierra el cuadro de diálogo, ok será False.
        category_name, ok = QInputDialog.getText(self, "Add Category", "Enter category name:")
        if ok and category_name:
            if category_name not in self.categories:
                self.categories.append(category_name)
                self.update_category_combo()
                self.category_combo.setCurrentText(category_name)
                self.open_task_dialog()
            else:
                QMessageBox.warning(self, "Category Error", "Category already exists!")

    def open_task_dialog(self):
        dialog = TaskDialog(self, self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
            task_id = len(self.tasks) + 1
            task = Task(
                category=task_data["category"],
                task_id=task_id,
                description=task_data["description"],
                due_date=task_data["due_date"],
                priority=task_data["priority"],
                status=task_data["status"]
            )
            self.tasks.append(task)
            self.filter_tasks_by_category()  # Refresh the task list to show the new task
    
    def update_category_combo(self):
        self.category_combo.clear()
        for category in self.categories:
            self.category_combo.addItem(category)
    
    def save_tasks(self):
         # _: Una variable de descarte que se usa para ignorar el segundo valor que devuelve getSaveFileName, que es un filtro seleccionado. No se necesita en este caso, por lo que se ignora.
        # es una opción común en los diálogos de archivos que permite al usuario ver y seleccionar todos los tipos de archivos en el directorio, no solo aquellos que coinciden con el filtro específico (en este caso, archivos CSV).
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Task List", "tareas export", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            with open(file_path, mode='w', newline='') as archivo:
                archivo.write("categoria,id,descripcion,fecha_vencimiento,prioridad,estado\n")  # Escribir encabezados
                for task in self.tasks:
                    archivo.write(f"{task.category},{task.task_id},{task.description},{task.due_date},{task.priority},{task.status}\n")
            QMessageBox.information(self, "Success", "Tasks saved successfully!")

    def load_tasks_from_file(self, file_path):
        file_path = Path(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                headers = file.readline().strip().split('|')
                for line in file:
                    fields = line.strip().split('|')
                    task_data = {}
                    for i in range(len(headers)):
                        task_data[headers[i]] = fields[i]
                    
                    task = Task(
                        category=task_data['categoria'],
                        task_id=task_data['id'],
                        description=task_data['descripcion'],
                        due_date=task_data['fecha_vencimiento'],
                        priority=task_data['prioridad'],
                        status=task_data['estado']
                    )
                    self.tasks.append(task)
                    if task_data['categoria'] not in self.categories:
                        self.categories.append(task_data['categoria'])
                self.update_category_combo()
                self.filter_tasks_by_category()
        else:
            QMessageBox.warning(self, "File Error", "The file does not exist or cannot be opened!")
    
    def filter_tasks_by_category(self):
        selected_category = self.category_combo.currentText()
        self.task_list.clear()
        for task in self.tasks:
            if task.category == selected_category:
                self.task_list.addItem(f"ID: {task.task_id}, Description: {task.description}, Due Date: {task.due_date.strftime('%Y/%m/%d')}, Priority: {task.priority}, Status: {task.status}, Category: {task.category}")

if __name__ == "__main__":
    app = QApplication([])
    window = TaskManager()
    window.show()
    app.exec()
