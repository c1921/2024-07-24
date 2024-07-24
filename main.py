import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, 
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import QTimer, Qt

class Building:
    def __init__(self, name, materials_required, workload, max_workers, unlocked=False):
        self.name = name
        self.materials_required = materials_required  # {'Wood': 10, 'Stone': 5}
        self.workload = workload  # 工作量，以小时计
        self.current_workload = 0  # 当前工作量
        self.unlocked = unlocked
        self.assigned_characters = []  # 分配的角色
        self.max_workers = max_workers  # 最多建造人数

    def unlock(self):
        self.unlocked = True

    def is_unlocked(self):
        return self.unlocked

    def progress_work(self):
        if self.assigned_characters:
            self.current_workload += 0.01 * len(self.assigned_characters)
            return self.current_workload >= self.workload
        return False

    def assign_character(self, character):
        if len(self.assigned_characters) < self.max_workers:
            self.assigned_characters.append(character)
            character.status = "Assigned"

    def unassign_character(self, character):
        if character in self.assigned_characters:
            self.assigned_characters.remove(character)
            character.status = "Idle"

class Item:
    def __init__(self, name, category, quantity=0):
        self.name = name
        self.category = category  # 'Material', 'Food', 'Weapon'
        self.quantity = quantity

class Character:
    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age
        self.status = "Idle"  # 初始状态为空闲

    def update_status(self, current_hour):
        if 21 <= current_hour or current_hour < 5:
            self.status = "Sleeping"
        elif 5 <= current_hour < 7 or 17 <= current_hour < 21:
            self.status = "Leisure"
        elif 7 <= current_hour < 17:
            if self.status != "Assigned":
                self.status = "Idle"
        else:
            self.status = "Idle"

class TimeModule(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_year = 1
        self.current_month = 3
        self.current_day = 1
        self.current_hour = 10
        self.current_minute = 0
        self.is_paused = False

        self.items = {
            'Wood': Item('Wood', 'Material', 100),
            'Stone': Item('Stone', 'Material', 50),
            'Bread': Item('Bread', 'Food', 20),
            'Sword': Item('Sword', 'Weapon', 5)
        }

        self.characters = [
            Character('John', 'Male', 25),
            Character('Alice', 'Female', 22)
        ]

        self.available_buildings = [
            Building('House', {'Wood': 10, 'Stone': 5}, 100, 2),
            Building('Farm', {'Wood': 5, 'Stone': 2}, 50, 1)
        ]

        self.under_construction = []
        self.owned_buildings = []

        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(200)  # 每200毫秒更新一次

        self.update_display()

    def initUI(self):
        self.setWindowTitle('Time Module')

        # 时间显示
        self.label = QLabel(self)

        # 暂停/继续按钮
        self.pause_continue_button = QPushButton('Pause', self)
        self.pause_continue_button.clicked.connect(self.toggle_time)

        # 物品表格
        self.items_table = QTableWidget(self)
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(['Name', 'Quantity'])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 角色表格
        self.characters_table = QTableWidget(self)
        self.characters_table.setColumnCount(4)
        self.characters_table.setHorizontalHeaderLabels(['Name', 'Gender', 'Age', 'Status'])
        self.characters_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.update_characters_table()

        # 建造按钮和建造中的建筑
        self.building_buttons_layout = QVBoxLayout()
        self.update_building_buttons()

        # 建造中的建筑和已拥有的建筑
        self.under_construction_label = QLabel("Under Construction")
        self.owned_buildings_label = QLabel("Owned Buildings")

        self.under_construction_list = QLabel()
        self.owned_buildings_list = QLabel()

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.pause_continue_button)
        self.main_layout.addWidget(self.items_table)
        self.main_layout.addWidget(self.characters_table)
        
        self.building_buttons_container = QFrame()
        self.building_buttons_container.setLayout(self.building_buttons_layout)
        self.main_layout.addWidget(self.building_buttons_container)

        self.main_layout.addWidget(self.under_construction_label)
        self.main_layout.addWidget(self.under_construction_list)
        self.main_layout.addWidget(self.owned_buildings_label)
        self.main_layout.addWidget(self.owned_buildings_list)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.update_items_table()

    def update_display(self):
        self.label.setText(f"{self.current_year}年-{self.current_month:02d}月-{self.current_day:02d}日 {self.current_hour:02d}:{self.current_minute:02d}")
        self.update_items_table()
        self.update_characters_table()
        self.update_under_construction_list()
        self.update_owned_buildings_list()

    def update_items_table(self):
        self.items_table.setRowCount(len(self.items))
        for i, item in enumerate(self.items.values()):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item.quantity)))

    def update_characters_table(self):
        self.characters_table.setRowCount(len(self.characters))
        for i, character in enumerate(self.characters):
            character.update_status(self.current_hour)
            self.characters_table.setItem(i, 0, QTableWidgetItem(character.name))
            self.characters_table.setItem(i, 1, QTableWidgetItem(character.gender))
            self.characters_table.setItem(i, 2, QTableWidgetItem(str(character.age)))
            self.characters_table.setItem(i, 3, QTableWidgetItem(character.status))

    def update_building_buttons(self):
        for i in reversed(range(self.building_buttons_layout.count())): 
            self.building_buttons_layout.itemAt(i).widget().setParent(None)

        for building in self.available_buildings:
            button = QPushButton(f"Build {building.name}", self)
            button.clicked.connect(lambda _, b=building: self.start_building(b))
            self.building_buttons_layout.addWidget(button)

    def update_under_construction_list(self):
        text = "\n".join([f"{b.name} ({b.current_workload:.2f}/{b.workload})" for b in self.under_construction])
        self.under_construction_list.setText(text)

    def update_owned_buildings_list(self):
        text = "\n".join([b.name for b in self.owned_buildings])
        self.owned_buildings_list.setText(text)

    def update_time(self):
        if not self.is_paused:
            self.current_minute += 1
            if self.current_minute >= 60:
                self.current_minute = 0
                self.current_hour += 1
            if self.current_hour >= 24:
                self.current_hour = 0
                self.current_day += 1
            if self.current_day > 30:
                self.current_day = 1
                self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1

            for character in self.characters:
                character.update_status(self.current_hour)

            for building in self.under_construction:
                if building.progress_work():
                    self.under_construction.remove(building)
                    self.owned_buildings.append(building)

            self.auto_assign_characters()

            self.update_display()

    def toggle_time(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_continue_button.setText('Continue')
        else:
            self.pause_continue_button.setText('Pause')

    def start_building(self, building):
        if all(self.items[material].quantity >= quantity for material, quantity in building.materials_required.items()):
            for material, quantity in building.materials_required.items():
                self.items[material].quantity -= quantity
            new_building = Building(building.name, building.materials_required, building.workload, building.max_workers)
            self.under_construction.append(new_building)
            self.update_display()

    def auto_assign_characters(self):
        for building in self.under_construction:
            for character in self.characters:
                if character.status == "Idle" and len(building.assigned_characters) < building.max_workers:
                    building.assign_character(character)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TimeModule()
    ex.show()
    sys.exit(app.exec())
