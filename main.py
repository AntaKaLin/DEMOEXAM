from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from main_ui import Ui_MainWindow
from dialog import Ui_Dialog
import pymysql
import sys


class Dialog(QDialog):
    def __init__(self, current_id=None):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # self.ui.lineEdit_3.setValidator(QIntValidator(0, 999999, self))
        # self.ui.lineEdit_6.setValidator(QIntValidator(0, 999999, self))
        # self.ui.lineEdit_4.setValidator(QDoubleValidator(0.0, 999999.99, 2, self))

        self.db = DataBase()
        
        self.setup_combo()
        # self.ui.buttonBox.accepted.connect(self.collect)

        self.current_id = current_id

        if current_id:
            self.load_data_in_lines()
            print('Изменение!')
            self.ui.buttonBox.accepted.connect(self.edit)
        else:
            print('Добавление!')
            self.ui.buttonBox.accepted.connect(self.add)

    def setup_combo(self):
        self.ui.comboBox.addItem('Kari', 2)
        self.ui.comboBox.addItem('Обувь для вас', 3)

        creators = self.db.creators()
        print(creators)
        for e in creators:
            self.ui.comboBox_2.addItem(e['name'], e['id'])
        
        self.ui.comboBox_3.addItem('Женская', 0)
        self.ui.comboBox_3.addItem('Мужская', 1)


    def collect(self):
        new_data = {'id': self.ui.lineEdit.text(), 'name': self.ui.lineEdit_2.text(), 'unit': self.ui.lineEdit_3.text(), 'price': self.ui.doubleSpinBox.value(), 'supplier_id': self.ui.comboBox.currentData(),\
                    'creator_id': self.ui.comboBox_2.currentData(), 'category': self.ui.comboBox_3.currentData(),\
                    'sale': self.ui.spinBox.value(),\
                    'quantity': self.ui.spinBox_2.value(), 'discription': self.ui.textEdit.toPlainText(), 'photo': self.ui.lineEdit_7.text()}
        return new_data

    def load_data_in_lines(self):
        data = self.db.get_one_stuff(self.current_id)
        self.ui.lineEdit.setText(str(data['id']))
        self.ui.lineEdit_2.setText(str(data['name'])) 
        self.ui.lineEdit_3.setText(str(data['unit']))
        self.ui.doubleSpinBox.setValue(data['price'])
        self.ui.comboBox.findData(data['supplier_id'])
        self.ui.comboBox_2.findData(data['creator_id'])
        self.ui.comboBox_3.findData(data['category'])
        self.ui.spinBox.setValue(data['sale'])
        self.ui.spinBox_2.setValue(data['quantity'])
        self.ui.textEdit.setText(data['discription'])
        self.ui.lineEdit_7.setText(str(data['photo']))

    def edit(self):
        new_data = self.collect()
        self.db.edit(new_data, self.current_id)
        print(new_data)

    def add(self):
        new_data = self.collect()
        self.db.add(new_data)
        print(new_data)



class DataBase():
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            database='demo_demo',
            password='',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )

    def creators(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM `creator`                           
            """)
        return cursor.fetchall()    

    def all_stuff(self, search=None):
        with self.conn.cursor() as cursor:
            q = """
            SELECT st.`id`, st.`name`, st.`unit`, st.`price`, s.name as sup_name, c.name as creator_name, st.`category`, st.`sale`, st.`quantity`, st.`discription`, st.`photo` FROM `stuff` as st
                join supplier as s on st.supplier_id = s.id
                join creator as c on st.creator_id = c.id """
            if not search:
                cursor.execute(q)
            else:
                print('есть фильтр')
                cursor.execute(q + f" where st.creator_id = {search}")

        return cursor.fetchall()
    
    def get_one_stuff(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `stuff` WHERE id = %s", (id,))
        return cursor.fetchone()
    
    def edit(self, new_data, old_id):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE `stuff` SET `id` = %s, `name` = %s, `unit` = %s, `price` = %s, `supplier_id` = %s, `creator_id` = %s, `category` = %s, `sale` = %s, `quantity` = %s, `discription` = %s,`photo` = %s WHERE `stuff`.`id` = %s """, (new_data['id'], new_data['name'], new_data['unit'], new_data['price'], new_data['supplier_id'], new_data['creator_id'], new_data['category'], new_data['sale'], new_data['quantity'], new_data['discription'], new_data['photo'], old_id,))
            self.conn.commit()

    def add(self, new_data):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO `stuff` (`id`, `name`, `unit`, `price`, `supplier_id`, `creator_id`, `category`, `sale`, `quantity`, `discription`, `photo`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_data['id'], new_data['name'], new_data['unit'], new_data['price'], new_data['supplier_id'], new_data['creator_id'], new_data['category'], new_data['sale'], new_data['quantity'], new_data['discription'], new_data['photo'],))
        self.conn.commit()

    def delete(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM stuff WHERE `stuff`.`id` = %s", (id,))
            self.conn.commit()

    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = DataBase()
        self.render_table()

        self.ui.add_btn.clicked.connect(self.add)
        self.ui.edit_btn.clicked.connect(self.edit)
        self.ui.delete_btn.clicked.connect(self.delete)
        self.ui.lineEdit_search.textChanged.connect(self.render_table)
        self.ui.comboBox_filter.currentIndexChanged.connect(self.render_table)

        creators = self.db.creators()
        print(creators)
        self.ui.comboBox_filter.addItem('Все производители', 0)
        for e in creators:
            self.ui.comboBox_filter.addItem(e['name'], e['id'])

    def load_data(self, search=None):
        data = self.db.all_stuff(search)
        # print(data[0].keys())
        return data
    
    def get_current_id(self):
        row = self.ui.tableWidget.currentRow()
        if row == -1:
            return None
        current_id = self.ui.tableWidget.item(row, 0).text()
        return current_id

    def add(self):
        dialog = Dialog()
        dialog.exec()
        self.render_table()

    def edit(self):
        id = self.get_current_id()
        if id == None:
            QMessageBox.information(self, 'Внимание!', 'Выберите элемент для редактирования')
            return None
        dialog = Dialog(id)
        dialog.exec()
        self.render_table()

    def delete(self):
        id = self.get_current_id()
        if id == None:
            QMessageBox.information(self, 'Внимание!', 'Выберите элемент для удаления')
            return None
        q = QMessageBox.question(self, 'Подтвердите удаление', f"Вы точно хотите удалить товар с артикулом {id}?", QMessageBox.Yes | QMessageBox.No)
        if q == QMessageBox.Yes:
            self.db.delete(id)
        self.render_table()
        


    def render_table(self):
        combobox_id = self.ui.comboBox_filter.currentData()
        data = self.load_data(combobox_id)

        s = self.ui.lineEdit_search.text().lower()

        # if s != None and len(s.split()) > 0:
        #     data_with_filter = self.load_data(s)

        self.ui.tableWidget.setRowCount(0)

        if not data:
            return

        self.ui.tableWidget.setColumnCount(len(data[0]))
        self.ui.tableWidget.setRowCount(len(data))
        self.ui.tableWidget.setHorizontalHeaderLabels(data[0].keys())


        for row_id, row in enumerate(data):
            for col_id, value in enumerate(row.values()):
                if col_id == 10:
                    pixmap = QPixmap(f'img\{value}').scaled(100, 100, Qt.KeepAspectRatio)
                    label = QLabel()
                    label.setPixmap(pixmap)
                    self.ui.tableWidget.setCellWidget(row_id, col_id, label)
                    continue

                item = QTableWidgetItem(str(value))
                
                if col_id == 7:
                    if int(value) >= 15:
                        item.setBackground(Qt.green)

                if s != None and len(s.split()) > 0 and s in str(value).lower():
                    item.setBackground(QColor(145, 199, 217))

                self.ui.tableWidget.setItem(row_id, col_id, item)

        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    icon = QPixmap('img/1.jpg')
    window.setWindowIcon(icon)


    sys.exit(app.exec())