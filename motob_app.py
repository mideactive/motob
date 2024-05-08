import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QDialog, QDialogButtonBox, QGridLayout, QTextEdit, QFormLayout, QHeaderView, QMenu, QAbstractItemView,
    QDateEdit
)
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator, QValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from database import get_all_debts
import database
import error_logger
from error_logger import log_error
from database import get_product_id
import logging


class MyStream(QtCore.QObject):
    text_written = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text):
        self.text_written.emit(str(text))

    def __del__(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


class MotobApp(QMainWindow):
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    def __init__(self):
        super().__init__()

        # Create an instance variable to hold the reference to the MyStream object
        self.stream = MyStream()

        # Redirect stdout and stderr to the text widget
        sys.stdout = self.stream
        sys.stderr = self.stream
        self.stream.text_written.connect(self.on_text_written)

        self.setWindowTitle("Motob Transactions")
        self.setStyleSheet("background-color: #f0f0f0; color: #333;")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.purchases_tab = QWidget()
        self.sales_tab = QWidget()
        self.view_purchases_tab = QWidget()
        self.view_sales_tab = QWidget()
        self.products_tab = QWidget()
        self.debtors_tab = QWidget()
        self.debt_tab = QWidget()
        self.calculator_tab = QWidget()

        self.tab_widget.addTab(self.purchases_tab, "Add Purchase")
        self.tab_widget.addTab(self.sales_tab, "Add Sale")
        self.tab_widget.addTab(self.view_purchases_tab, "View Purchases")
        self.tab_widget.addTab(self.view_sales_tab, "View Sales")
        self.tab_widget.addTab(self.products_tab, "Manage Products")
        self.tab_widget.addTab(self.debtors_tab, "Manage Debtors")
        self.tab_widget.addTab(self.debt_tab, "Manage Debts")
        self.tab_widget.addTab(self.calculator_tab, "Calculator")

        self.setup_purchases_tab()
        self.setup_sales_tab()
        self.setup_view_purchases_tab()
        self.setup_view_sales_tab()
        self.setup_products_tab()
        self.setup_debtors_tab()
        self.setup_debt_tab()
        self.setup_calculator_tab()

        self.show()

    def on_text_written(self, text):
        # Handle the emitted text here by appending it to a QTextEdit widget
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()


    def setup_debt_tab(self):
        layout = QVBoxLayout(self.debt_tab)

        label = QLabel("Manage Debts:")
        label.setFont(QFont("Arial", 16, weight=QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add Debt Entry Form
        form_layout = QFormLayout()
        self.creditor_label = QLabel("Creditor:")
        self.creditor = QLineEdit()
        form_layout.addRow(self.creditor_label, self.creditor)

        self.date_label = QLabel("Date:")
        self.date = QLineEdit()
        form_layout.addRow(self.date_label, self.date)

        self.goods_purchased_label = QLabel("Goods Purchased:")
        self.goods_purchased = QLineEdit()
        form_layout.addRow(self.goods_purchased_label, self.goods_purchased)

        self.quantity_label = QLabel("Quantity:")
        self.quantity = QLineEdit()
        self.quantity.setValidator(QIntValidator())
        form_layout.addRow(self.quantity_label, self.quantity)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price = QLineEdit()
        self.unit_price.setValidator(QDoubleValidator())
        form_layout.addRow(self.unit_price_label, self.unit_price)

        layout.addLayout(form_layout)

        button_add_debt = QPushButton("Add Debt")
        button_add_debt.clicked.connect(self.add_debt)
        layout.addWidget(button_add_debt)

        # Debt Table
        self.debt_table = QTableWidget()
        self.debt_table.setColumnCount(8)  # Corrected column count
        self.debt_table.setHorizontalHeaderLabels(["ID", "Creditor", "Date", "Goods Purchased", "Quantity", "Unit Price", "Total", "Actions"])
        layout.addWidget(self.debt_table)

        # Load existing debts
        self.load_debts()

    def add_debt(self):
        creditor = self.creditor.text()
        date = self.date.text()
        goods_purchased = self.goods_purchased.text()
        quantity_text = self.quantity.text()
        unit_price_text = self.unit_price.text()

        if not creditor or not date or not goods_purchased or not quantity_text or not unit_price_text:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        try:
            quantity = int(quantity_text)
            unit_price = float(unit_price_text)
            total = quantity * unit_price
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numeric values.")
            return

        if quantity < 0 or unit_price < 0:
            QMessageBox.warning(self, "Warning", "Values cannot be negative.")
            return

        # Add debt to database
        database.add_debt(creditor, date, goods_purchased, quantity, unit_price)
        self.load_debts()  # Reload debts to update the table with the new data

        # Clear input fields after adding debt
        self.creditor.clear()
        self.date.clear()
        self.goods_purchased.clear()
        self.quantity.clear()
        self.unit_price.clear()
        self.total.clear()

    def load_debts(self):
        # Clear existing data
        self.debt_table.setRowCount(0)

        # Fetch all debts from the database
        debts = database.get_all_debts()

        # Populate the table with debts
        for row, debt in enumerate(debts):
            self.debt_table.insertRow(row)
            for col, data in enumerate(debt):
                item = QTableWidgetItem(str(data))
                self.debt_table.setItem(row, col, item)

            # Add edit and delete buttons to each row under the "Actions" column
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, r=row: self.edit_debt(r))
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, r=row: self.delete_debt(r))
            buttons_layout = QHBoxLayout()
            buttons_layout.addWidget(edit_button)
            buttons_layout.addWidget(delete_button)
            cell_widget = QWidget()
            cell_widget.setLayout(buttons_layout)
            self.debt_table.setCellWidget(row, 7, cell_widget)

        self.debt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def edit_debt(self, row):
        debt_id = int(self.debt_table.item(row, 0).text())  # Assuming ID is in the first column
        creditor = self.debt_table.item(row, 1).text()
        date = self.debt_table.item(row, 2).text()
        goods_purchased = self.debt_table.item(row, 3).text()
        quantity = int(self.debt_table.item(row, 4).text())
        unit_price = float(self.debt_table.item(row, 5).text())

        # Open a dialog to edit debt details
        dialog = EditDebtDialog(debt_id, creditor, date, goods_purchased, quantity, unit_price, parent=self)
        if dialog.exec_():
            # If the dialog is accepted (e.g., user clicked OK), reload debts
            self.load_debts()

    def delete_debt(self, row):
        debt_id = int(self.debt_table.item(row, 0).text())  # Assuming ID is in the first column

        # Confirm deletion with a message box
        reply = QMessageBox.question(self, 'Delete Debt', 'Are you sure you want to delete this debt?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # If user confirms deletion, delete the debt from the database
            database.delete_debt(debt_id)
            # Reload debts after deletion
            self.load_debts()

    def setup_calculator_tab(self):  # Function to setup calculator tab
        layout = QVBoxLayout()
        self.calculator_tab.setLayout(layout)

        label = QLabel("Calculator:")
        label.setFont(QFont("Arial", 16, weight=QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add calculator display
        self.display = QLineEdit()
        self.display.setFont(QFont("Arial", 12))
        self.display.setAlignment(Qt.AlignRight)
        layout.addWidget(self.display)

        # Create calculator buttons
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('=', 3, 2), ('+', 3, 3)
        ]

        for btn_text, row, col in buttons:
            btn = QPushButton(btn_text)
            btn.setFont(QFont("Arial", 12))
            btn.clicked.connect(lambda _, text=btn_text: self.on_button_click(text))
            grid_layout.addWidget(btn, row, col)

    def on_button_click(self, text):  # Function to handle calculator button clicks
        if text == '=':
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
        else:
            self.display.setText(self.display.text() + text)

    def setup_purchases_tab(self):
        layout = QVBoxLayout()
        self.purchases_tab.setLayout(layout)

        label = QLabel("Add Purchase:")
        label.setFont(QFont("Arial", 16, weight=QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add widgets for data entry with labels

        self.purchase_date_label = QLabel("Date:")
        self.purchase_date = QLineEdit()
        self.purchase_date.setFont(QFont("Arial", 12))
        layout.addWidget(self.purchase_date_label)
        layout.addWidget(self.purchase_date)

        self.purchase_item_name_label = QLabel("Item Name:")
        self.purchase_item_name = QLineEdit()
        self.purchase_item_name.setFont(QFont("Arial", 12))
        layout.addWidget(self.purchase_item_name_label)
        layout.addWidget(self.purchase_item_name)

        self.purchase_quantity_label = QLabel("Quantity:")
        self.purchase_quantity = QLineEdit()
        self.purchase_quantity.setFont(QFont("Arial", 12))
        self.purchase_quantity.setValidator(QIntValidator())  # Numeric validation
        layout.addWidget(self.purchase_quantity_label)
        layout.addWidget(self.purchase_quantity)

        self.purchase_unit_price_label = QLabel("Unit Price:")
        self.purchase_unit_price = QLineEdit()
        self.purchase_unit_price.setFont(QFont("Arial", 12))
        self.purchase_unit_price.setValidator(QDoubleValidator())  # Numeric validation
        layout.addWidget(self.purchase_unit_price_label)
        layout.addWidget(self.purchase_unit_price)

        # Add Total Price field
        self.purchase_total_price_label = QLabel("Total Price:")
        self.purchase_total_price = QLineEdit()
        self.purchase_total_price.setFont(QFont("Arial", 12))
        self.purchase_total_price.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.purchase_total_price_label)
        layout.addWidget(self.purchase_total_price)

        button = QPushButton("Add Purchase")
        button.setFont(QFont("Arial", 14))
        button.clicked.connect(self.add_purchase)
        layout.addWidget(button)

    def add_purchase(self):
        try:
            date = self.purchase_date.text()
            item_name = self.purchase_item_name.text().strip()  # Remove leading and trailing spaces
            quantity = int(self.purchase_quantity.text())
            unit_price = float(self.purchase_unit_price.text())

            # Validate date format
            date_validator = QRegExpValidator(QRegExp("[0-9]{4}-[0-9]{2}-[0-9]{2}"))  # YYYY-MM-DD format
            if not date_validator.validate(date, 0)[0] == QValidator.Acceptable:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

            if not date or not item_name:
                raise ValueError("Please fill in all fields.")

            # Validate item name format
            item_name_validator = QRegExpValidator(QRegExp("[A-Za-z]+( [A-Za-z]+)*"))
            if not item_name_validator.validate(item_name, 0)[0] == QValidator.Acceptable:
                raise ValueError("Invalid item name format. Please use alphabetic characters and spaces, but not at the beginning or end.")

            # Calculate total price
            total_price = quantity * unit_price
            self.purchase_total_price.setText(str(total_price))  # Update total price field

            # Check for duplicate entry
            if database.purchase_exists(date, item_name, quantity, unit_price):
                raise ValueError("Duplicate entry detected.")

            # Add purchase to database
            database.add_purchase(date, item_name, quantity, unit_price)
            self.load_purchases()  # Reload purchases to update the table with the new data

            # Clear input fields after successful submission
            self.purchase_date.clear()
            self.purchase_item_name.clear()
            self.purchase_quantity.clear()
            self.purchase_unit_price.clear()
            self.purchase_total_price.clear()

        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def load_purchases(self):
        try:
            purchases = database.get_all_purchases()
            self.purchases_table.setRowCount(len(purchases))
            for row, purchase in enumerate(purchases):
                for col, data in enumerate(purchase):
                    item = QTableWidgetItem(str(data))
                    self.purchases_table.setItem(row, col, item)

                # Calculate total price and display it in the "Total Price" column
                quantity = int(purchase[4])
                unit_price = float(purchase[5])
                total_price = quantity * unit_price
                total_item = QTableWidgetItem(str(total_price))
                self.purchases_table.setItem(row, 6, total_item)  # Place total price in the correct column

                # Add edit and delete buttons to each row under the "Actions" column
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda state, row=row: self.edit_purchase(row))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda state, row=row: self.delete_purchase(row))
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(edit_button)
                buttons_layout.addWidget(delete_button)
                cell_widget = QWidget()
                cell_widget.setLayout(buttons_layout)
                self.purchases_table.setCellWidget(row, 6, cell_widget)  # Place buttons in the correct column

        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def edit_purchase(self, row):
        try:
            # Get purchase ID
            purchase_id_item = self.purchases_table.item(row, 0)
            if purchase_id_item is None:
                raise ValueError("Purchase ID is not available.")
            purchase_id = int(purchase_id_item.text())

            # Get data from the table
            date_item = self.purchases_table.item(row, 2)
            if date_item is None:
                raise ValueError("Date is not available.")
            date = date_item.text()

            item_name_item = self.purchases_table.item(row, 1)  # Corrected index for item name
            if item_name_item is None:
                raise ValueError("Item name is not available.")
            item_name = item_name_item.text()

            quantity_item = self.purchases_table.item(row, 3)  # Corrected index for quantity
            if quantity_item is None:
                raise ValueError("Quantity is not available.")
            quantity = round(float(quantity_item.text()))

            unit_price_item = self.purchases_table.item(row, 4)  # Corrected index for unit price
            if unit_price_item is None:
                raise ValueError("Unit price is not available.")
            unit_price = float(unit_price_item.text())

            total_price_item = self.purchases_table.item(row, 5)  # Corrected index for total price
            if total_price_item is None:
                print("Total price item is None at row:", row)  # Debugging statement
                raise ValueError("Total price is not available.")
            total_price = float(total_price_item.text())  # Fetch total price from the table

            # Open a dialog for editing
            dialog = EditPurchaseDialog(date, item_name, quantity, unit_price, total_price)
            if dialog.exec_():
                # Get updated data from the dialog
                updated_date = dialog.date.text()
                updated_item_name = dialog.item_name.text()
                updated_quantity = round(float(dialog.quantity.text()))
                updated_unit_price = float(dialog.unit_price.text())

                # Calculate total price
                updated_total_price = updated_quantity * updated_unit_price

                # Update the database
                database.edit_purchase(purchase_id, updated_date, updated_item_name, updated_quantity, updated_unit_price, updated_total_price)

                # Reload the purchases
                self.load_purchases()

        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def delete_purchase(self, row):
        try:
            # Get purchase ID
            purchase_id = int(self.purchases_table.item(row, 0).text())

            # Confirmation dialog
            reply = QMessageBox.question(self, 'Delete Purchase', 'Are you sure you want to delete this purchase?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Delete the purchase from the database
                database.delete_purchase(purchase_id)

                # Reload the purchases
                self.load_purchases()

        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def setup_view_purchases_tab(self):
        layout = QVBoxLayout()
        self.view_purchases_tab.setLayout(layout)

        label = QLabel("View Purchases:")
        label.setFont(QFont("Arial", 16, weight=QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        try:
            self.purchases_table = QTableWidget()
            self.purchases_table.setColumnCount(7)  # Updated to include "Product ID" and "Total Price" columns
            self.purchases_table.setHorizontalHeaderLabels(["ID","Item Name", "Date", "Quantity", "Unit Price", "Total Price", "Actions"])
            # Updated header labels
            layout.addWidget(self.purchases_table)

            # Print column headers and their indices
            header_labels = [self.purchases_table.horizontalHeaderItem(i).text() for i in range(self.purchases_table.columnCount())]
            print("Column Headers: {}".format(header_labels))

            self.load_purchases()

            # Set column alignment
            header = self.purchases_table.horizontalHeader()
            for col in range(self.purchases_table.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.Stretch)  # Adjust column width to content
                header.setDefaultAlignment(Qt.AlignCenter)  # Align header text to center

        except Exception as e:
            error_logger.log_error(e)

    def setup_sales_tab(self):
        try:
            layout = QVBoxLayout()
            self.sales_tab.setLayout(layout)

            label = QLabel("Add Sale:")
            label.setFont(QFont("Arial", 16, weight=QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            # Add widgets for data entry with labels
            self.sale_date_label = QLabel("Date:")
            self.sale_date = QLineEdit()
            self.sale_date.setFont(QFont("Arial", 12))
            layout.addWidget(self.sale_date_label)
            layout.addWidget(self.sale_date)

            self.sale_item_name_label = QLabel("Item Name:")
            self.sale_item_name = QLineEdit()
            self.sale_item_name.setFont(QFont("Arial", 12))
            layout.addWidget(self.sale_item_name_label)
            layout.addWidget(self.sale_item_name)

            self.sale_customer_name_label = QLabel("Customer Name:")
            self.sale_customer_name = QLineEdit()
            self.sale_customer_name.setFont(QFont("Arial", 12))
            layout.addWidget(self.sale_customer_name_label)
            layout.addWidget(self.sale_customer_name)

            self.sale_quantity_label = QLabel("Quantity:")
            self.sale_quantity = QLineEdit()
            self.sale_quantity.setFont(QFont("Arial", 12))
            self.sale_quantity.setValidator(QIntValidator())
            layout.addWidget(self.sale_quantity_label)
            layout.addWidget(self.sale_quantity)

            self.sale_unit_price_label = QLabel("Unit Price:")
            self.sale_unit_price = QLineEdit()
            self.sale_unit_price.setFont(QFont("Arial", 12))
            self.sale_unit_price.setValidator(QDoubleValidator())
            layout.addWidget(self.sale_unit_price_label)
            layout.addWidget(self.sale_unit_price)

            button = QPushButton("Add Sale")
            button.setFont(QFont("Arial", 14))
            button.clicked.connect(self.add_sale)
            layout.addWidget(button)

        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def add_sale(self):
        try:
            date = self.sale_date.text()
            item_name = self.sale_item_name.text().strip()  # Remove leading and trailing spaces
            customer_name = self.sale_customer_name.text().strip()  # Remove leading and trailing spaces
            quantity = int(self.sale_quantity.text())
            unit_price = float(self.sale_unit_price.text())

            if not date or not item_name or not customer_name:
                raise ValueError("Please fill in all fields.")

            # Validate date format
            date_validator = QRegExpValidator(QRegExp("[0-9]{4}-[0-9]{2}-[0-9]{2}"))  # YYYY-MM-DD format
            if not date_validator.validate(date, 0)[0] == QValidator.Acceptable:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

            # Validate item name format
            item_name_validator = QRegExpValidator(QRegExp("[A-Za-z]+( [A-Za-z]+)*"))  # Allows alphabetic characters and spaces but not at the beginning or end
            if not item_name_validator.validate(item_name, 0)[0] == QValidator.Acceptable:
                raise ValueError("Invalid item name format. Please use alphabetic characters and spaces, but not at the beginning or end.")

            # Calculate total price
            total_price = quantity * unit_price

            database.add_sale(item_name, date, customer_name, quantity, unit_price)
            self.load_sales()

            # Clear input fields after successful submission
            self.sale_date.clear()
            self.sale_item_name.clear()
            self.sale_customer_name.clear()
            self.sale_quantity.clear()
            self.sale_unit_price.clear()

        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def load_sales(self):
        try:
            sales = database.get_all_sales()
            self.sales_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, data in enumerate(sale):
                    item = QTableWidgetItem(str(data))
                    self.sales_table.setItem(row, col, item)

                # Calculate total price and display it in the "Total" column
                quantity = int(sale[4])
                unit_price = float(sale[5])
                total_price = quantity * unit_price
                total_item = QTableWidgetItem(str(total_price))
                self.sales_table.setItem(row, 6, total_item)

                # Add edit and delete buttons to each row under the "Actions" column
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda state, row=row: self.edit_sale(row))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda state, row=row: self.delete_sale(row))
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(edit_button)
                buttons_layout.addWidget(delete_button)
                cell_widget = QWidget()
                cell_widget.setLayout(buttons_layout)
                self.sales_table.setCellWidget(row, 7, cell_widget)
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def edit_sale(self, row):
        try:
            # Get sale ID
            sale_id = int(self.sales_table.item(row, 0).text())

            # Get data from the table
            date = self.sales_table.item(row, 1).text()
            customer_name = self.sales_table.item(row, 2).text().strip()  # Remove leading and trailing spaces
            item_name = self.sales_table.item(row, 3).text().strip()  # Remove leading and trailing spaces
            quantity = round(float(self.sales_table.item(row, 4).text()))
            unit_price = float(self.sales_table.item(row, 5).text())

            # Open a dialog for editing
            dialog = EditSaleDialog(date, customer_name, item_name, quantity, unit_price)
            if dialog.exec_():
                # Get updated data from the dialog
                updated_date = dialog.date.text()
                updated_customer_name = dialog.customer_name.text().strip()  # Remove leading and trailing spaces
                updated_item_name = dialog.item_name.text().strip()  # Remove leading and trailing spaces
                updated_quantity = round(float(dialog.quantity.text()))
                updated_unit_price = float(dialog.unit_price.text())

                if not updated_date or not updated_item_name or not updated_customer_name:
                    raise ValueError("Please fill in all fields.")

                # Validate date format
                date_validator = QRegExpValidator(QRegExp("[0-9]{4}-[0-9]{2}-[0-9]{2}"))  # YYYY-MM-DD format
                if not date_validator.validate(updated_date, 0)[0] == QValidator.Acceptable:
                    raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

                # Validate item name format
                item_name_validator = QRegExpValidator(QRegExp("[A-Za-z]+( [A-Za-z]+)*"))  # Allows alphabetic characters and spaces but not at the beginning or end
                if not item_name_validator.validate(updated_item_name, 0)[0] == QValidator.Acceptable:
                    raise ValueError("Invalid item name format. Please use alphabetic characters and spaces, but not at the beginning or end.")

                # Update the database
                database.edit_sale(sale_id, updated_date, updated_customer_name, updated_item_name, updated_quantity, updated_unit_price)

                # Reload the sales
                self.load_sales()

        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def delete_sale(self, row):
        try:
            # Get sale ID
            sale_id = int(self.sales_table.item(row, 0).text())

            # Confirmation dialog
            reply = QMessageBox.question(self, 'Delete Sale', 'Are you sure you want to delete this sale?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Delete the sale from the database
                database.delete_sale(sale_id)

                # Reload the sales
                self.load_sales()
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def setup_view_sales_tab(self):
        try:
            layout = QVBoxLayout()
            self.view_sales_tab.setLayout(layout)

            label = QLabel("View Sales:")
            label.setFont(QFont("Arial", 16, weight=QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            self.sales_table = QTableWidget()
            self.sales_table.setColumnCount(8)  # Updated to include "Total" column
            self.sales_table.setHorizontalHeaderLabels(["ID", "Item Name", "Date", "Customer Name", "Quantity", "Unit Price", "Total", "Actions"])  # Updated header labels
            layout.addWidget(self.sales_table)

            self.load_sales()

            # Set column alignment
            for col in range(self.sales_table.columnCount()):
                self.sales_table.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def setup_products_tab(self):
        try:
            layout = QVBoxLayout()
            self.products_tab.setLayout(layout)

            label = QLabel("Manage Products:")
            label.setFont(QFont("Arial", 16, weight=QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            self.product_name_label = QLabel("Product Name:")
            self.product_name = QLineEdit()
            self.product_name.setFont(QFont("Arial", 12))
            layout.addWidget(self.product_name_label)
            layout.addWidget(self.product_name)

            self.product_stock_label = QLabel("Stock:")
            self.product_stock = QLineEdit()
            self.product_stock.setFont(QFont("Arial", 12))
            self.product_stock.setValidator(QIntValidator())
            layout.addWidget(self.product_stock_label)
            layout.addWidget(self.product_stock)

            self.product_sold_stock_label = QLabel("Sold Stock:")
            self.product_sold_stock = QLineEdit()
            self.product_sold_stock.setFont(QFont("Arial", 12))
            self.product_sold_stock.setValidator(QIntValidator())
            layout.addWidget(self.product_sold_stock_label)
            layout.addWidget(self.product_sold_stock)

            button_add_product = QPushButton("Add Product")
            button_add_product.setFont(QFont("Arial", 14))
            button_add_product.clicked.connect(self.add_product)
            layout.addWidget(button_add_product)

            self.products_table = QTableWidget()
            self.products_table.setColumnCount(6)
            self.products_table.setHorizontalHeaderLabels(["ID", "Product Name", "Stock", "Sold Stock", "Available Stock", "Actions"])
            layout.addWidget(self.products_table)

            self.load_products()
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def add_product(self):
        try:
            name = self.product_name.text().strip()
            available_stock_text = self.product_stock.text().strip()
            sold_stock_text = self.product_sold_stock.text().strip()

            if not name or not available_stock_text or not sold_stock_text:
                raise ValueError("Please fill in all fields.")

            available_stock = int(float(available_stock_text))
            sold_stock = int(float(sold_stock_text))

            if available_stock < 0 or sold_stock < 0:
                raise ValueError("Stock values cannot be negative.")

            if database.product_exists(name):
                raise ValueError("Product already exists.")

            # Calculate available stock by subtracting sold stock
            available_stock -= sold_stock

            if available_stock < 0:
                raise ValueError("Available stock cannot be negative after deducting sold stock.")

            database.add_product(name, available_stock, sold_stock)
            self.load_products()
        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def load_products(self):
        try:
            products = database.get_all_products()
            self.products_table.setRowCount(len(products))

            if not products:
                print("No products found.")
                return

            for row, product in enumerate(products):
                for col, data in enumerate(product):
                    item = QTableWidgetItem(str(data))
                    self.products_table.setItem(row, col, item)

                # Calculate available stock by subtracting sold stock
                available_stock = product[2] - product[3]
                total_item = QTableWidgetItem(str(available_stock))
                self.products_table.setItem(row, 4, total_item)

                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda state, row=row: self.edit_product(row))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda state, row=row: self.delete_product(row))

                buttons_widget = QWidget()
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(edit_button)
                buttons_layout.addWidget(delete_button)
                buttons_widget.setLayout(buttons_layout)

                self.products_table.setCellWidget(row, 5, buttons_widget)
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def edit_product(self, row):
        try:
            product_id = self.products_table.item(row, 0).text()
            name = self.products_table.item(row, 1).text()
            available_stock = int(float(self.products_table.item(row, 2).text()))
            sold_stock = int(float(self.products_table.item(row, 3).text()))

            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Product")
            layout = QVBoxLayout()

            name_label = QLabel("Product Name:")
            name_input = QLineEdit(name)
            layout.addWidget(name_label)
            layout.addWidget(name_input)

            available_stock_label = QLabel("Stock:")
            available_stock_input = QLineEdit(str(available_stock))
            available_stock_input.setValidator(QIntValidator())
            layout.addWidget(available_stock_label)
            layout.addWidget(available_stock_input)

            sold_stock_label = QLabel("Sold Stock:")
            sold_stock_input = QLineEdit(str(sold_stock))
            sold_stock_input.setValidator(QIntValidator())
            layout.addWidget(sold_stock_label)
            layout.addWidget(sold_stock_input)

            buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            button_box = QDialogButtonBox(buttons)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            dialog.setLayout(layout)

            if dialog.exec_() == QDialog.Accepted:
                new_name = name_input.text()
                new_available_stock = int(available_stock_input.text()) - sold_stock  # Calculate new available stock
                new_sold_stock = int(sold_stock_input.text())
                if new_available_stock < 0:
                    raise ValueError("Available stock cannot be negative after deducting sold stock.")
                database.update_product(product_id, new_name, new_available_stock, new_sold_stock)
                self.load_products()
        except ValueError as e:
            error_logger.log_error(e)
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def delete_product(self, row):
        try:
            product_id = int(self.products_table.item(row, 0).text())
            reply = QMessageBox.question(self, 'Delete Product', 'Are you sure you want to delete this product?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                database.delete_product(product_id)
                self.load_products()
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

    def setup_debtors_tab(self):
        layout = QVBoxLayout()
        self.debtors_tab.setLayout(layout)

        label = QLabel("Manage Debtors:")
        label.setFont(QFont("Arial", 16, weight=QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.debtor_name_label = QLabel("Debtor Name:")
        self.debtor_name = QLineEdit()
        self.debtor_name.setFont(QFont("Arial", 12))
        layout.addWidget(self.debtor_name_label)
        layout.addWidget(self.debtor_name)


        self.item_label = QLabel("Item:")
        self.item = QLineEdit()
        self.item.setFont(QFont("Arial", 12))
        layout.addWidget(self.item_label)
        layout.addWidget(self.item)

        self.date_label = QLabel("Date:")
        #self.date = QLineEdit()
        self.date = QDateEdit()  # Changed to QDateEdit to correctly handle date input
        self.date.setFont(QFont("Arial", 12))
        layout.addWidget(self.date_label)
        layout.addWidget(self.date)

        self.quantity_label = QLabel("Quantity:")
        self.quantity = QLineEdit()
        self.quantity.setFont(QFont("Arial", 12))
        self.quantity.setValidator(QIntValidator())
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price = QLineEdit()
        self.unit_price.setFont(QFont("Arial", 12))
        self.unit_price.setValidator(QDoubleValidator())
        layout.addWidget(self.unit_price_label)
        layout.addWidget(self.unit_price)

        button_add_debtor = QPushButton("Add Debtor")
        button_add_debtor.setFont(QFont("Arial", 14))
        button_add_debtor.clicked.connect(self.add_debtor)
        layout.addWidget(button_add_debtor)

        self.debtors_table = QTableWidget()
        self.debtors_table.setColumnCount(8)
        self.debtors_table.setHorizontalHeaderLabels(["ID", "Debtor Name", "Item", "Date", "Quantity", "Unit Price", "Total", "Actions"])
        layout.addWidget(self.debtors_table)

        self.load_debtors()

    def add_debtor(self):
        name = self.debtor_name.text()
        item = self.item.text()
        #date = self.date.text()
        date = self.date.date().toString(Qt.ISODate)  # Retrieve date correctly using QDateEdit
        quantity_text = self.quantity.text()
        unit_price_text = self.unit_price.text()

        logging.debug("Name: %s", name)
        logging.debug("Item: %s", item)
        logging.debug("Date: %s", date)
        logging.debug("Quantity: %s", quantity_text)
        logging.debug("Unit Price: %s", unit_price_text)

        if not name or not item or not date or not quantity_text or not unit_price_text:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        try:
            quantity = int(quantity_text)
            unit_price = float(unit_price_text)
            total = quantity * unit_price
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numeric values.")
            return

        if quantity < 0 or unit_price < 0:
            QMessageBox.warning(self, "Warning", "Values cannot be negative.")
            return

        try:
            database.add_debtor(name, item, date, quantity, unit_price)
            self.load_debtors()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while adding debtor: {str(e)}")

    def load_debtors(self):
        debtors = database.get_all_debtors()
        self.debtors_table.setRowCount(len(debtors))

        for row, debtor in enumerate(debtors):
            for col, data in enumerate(debtor):
                item = QTableWidgetItem(str(data))
                self.debtors_table.setItem(row, col, item)

            # Add edit and delete buttons to each row under the "Actions" column
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda state, row=row: self.edit_debtor(row))
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda state, row=row: self.delete_debtor(row))
            buttons_layout = QHBoxLayout()
            buttons_layout.addWidget(edit_button)
            buttons_layout.addWidget(delete_button)
            cell_widget = QWidget()
            cell_widget.setLayout(buttons_layout)
            self.debtors_table.setCellWidget(row, 7, cell_widget)

    def edit_debtor(self, row):
        debtor_id = int(self.debtors_table.item(row, 0).text())
        name = self.debtors_table.item(row, 1).text()
        item = self.debtors_table.item(row, 2).text()
        date = self.debtors_table.item(row, 3).text()
        quantity = int(self.debtors_table.item(row, 4).text())
        unit_price = float(self.debtors_table.item(row, 5).text())
        total = float(self.debtors_table.item(row, 6).text())

        dialog = EditDebtorDialog(name, item, date, quantity, unit_price, total)
        if dialog.exec_():
            updated_name = dialog.debtor_name.text()
            updated_date = dialog.date.text()
            updated_item = dialog.item_name.text()
            updated_quantity = int(dialog.quantity.text())
            updated_unit_price = float(dialog.unit_price.text())
            updated_total = updated_quantity * updated_unit_price  # Recalculate total

            try:
                database.update_debtor(debtor_id, updated_name, updated_item, updated_date, updated_quantity, updated_unit_price)
                self.load_debtors()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while updating debtor: {str(e)}")

    def delete_debtor(self, row):
        debtor_id = int(self.debtors_table.item(row, 0).text())
        reply = QMessageBox.question(self, 'Delete Debtor', 'Are you sure you want to delete this debtor?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            database.delete_debtor(debtor_id)
            self.load_debtors()

class EditPurchaseDialog(QDialog):
    def __init__(self, item_name, date, quantity, unit_price, total_price):
        try:
            super().__init__()

            self.setWindowTitle("Edit Purchase")

            layout = QVBoxLayout()
            self.setLayout(layout)

            self.item_name_label = QLabel("Date:")
            self.item_name = QLineEdit(item_name)
            layout.addWidget(self.item_name_label)
            layout.addWidget(self.item_name)

            self.date_label = QLabel("Item Name:")
            self.date = QLineEdit(date)
            layout.addWidget(self.date_label)
            layout.addWidget(self.date)

            self.quantity_label = QLabel("Quantity:")
            self.quantity = QLineEdit(str(quantity))
            layout.addWidget(self.quantity_label)
            layout.addWidget(self.quantity)

            self.unit_price_label = QLabel("Unit Price:")
            self.unit_price = QLineEdit(str(unit_price))
            layout.addWidget(self.unit_price_label)
            layout.addWidget(self.unit_price)

            self.total_price_label = QLabel("Total Price:")
            self.total_price = QLineEdit(str(total_price))
            layout.addWidget(self.total_price_label)
            layout.addWidget(self.total_price)

            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(self.button_box)

            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

class EditSaleDialog(QDialog):
    def __init__(self, item_name, date, customer_name, quantity, unit_price):
        try:
            super().__init__()

            self.setWindowTitle("Edit Sale")

            layout = QVBoxLayout()
            self.setLayout(layout)

            self.item_name_label = QLabel("Item Name:")
            self.item_name = QLineEdit(item_name)
            layout.addWidget(self.item_name_label)
            layout.addWidget(self.item_name)

            self.date_label = QLabel("Date:")
            self.date = QLineEdit(date)
            layout.addWidget(self.date_label)
            layout.addWidget(self.date)

            self.customer_name_label = QLabel("Customer Name:")
            self.customer_name = QLineEdit(customer_name)
            layout.addWidget(self.customer_name_label)
            layout.addWidget(self.customer_name)

            self.quantity_label = QLabel("Quantity:")
            self.quantity = QLineEdit(str(quantity))
            layout.addWidget(self.quantity_label)
            layout.addWidget(self.quantity)

            self.unit_price_label = QLabel("Unit Price:")
            self.unit_price = QLineEdit(str(unit_price))
            layout.addWidget(self.unit_price_label)
            layout.addWidget(self.unit_price)

            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(self.button_box)

            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
        except Exception as e:
            error_logger.log_error(e)
            QMessageBox.critical(self, "Error", str(e))

class EditDebtorDialog(QDialog):
    def __init__(self, name, item, date, quantity, unit_price, total):
        super().__init__()
        self.setWindowTitle("Edit Debtor")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.debtor_name_label = QLabel("Debtor Name:")
        self.debtor_name = QLineEdit(name)
        layout.addWidget(self.debtor_name_label)
        layout.addWidget(self.debtor_name)

        self.item_name_label = QLabel("Item Name:")
        self.item_name = QLineEdit(item)
        layout.addWidget(self.item_name_label)
        layout.addWidget(self.item_name)

        self.date_label = QLabel("Date:")
        self.date = QLineEdit(date)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date)

        self.quantity_label = QLabel("Quantity:")
        self.quantity = QLineEdit(str(quantity))
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price = QLineEdit(str(unit_price))
        layout.addWidget(self.unit_price_label)
        layout.addWidget(self.unit_price)

        self.total_label = QLabel("Total:")
        self.total = QLineEdit(str(total))
        self.total.setReadOnly(True)  # Make total field read-only
        layout.addWidget(self.total_label)
        layout.addWidget(self.total)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

class EditDebtDialog(QDialog):
    def __init__(self, debt_id, creditor, date, goods_purchased, quantity, unit_price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Debt")
        self.debt_id = debt_id

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.creditor_label = QLabel("Creditor:")
        self.creditor = QLineEdit(creditor)
        layout.addWidget(self.creditor_label)
        layout.addWidget(self.creditor)

        self.date_label = QLabel("Date:")
        self.date = QLineEdit(date)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date)

        self.goods_purchased_label = QLabel("Goods Purchased:")
        self.goods_purchased = QLineEdit(goods_purchased)
        layout.addWidget(self.goods_purchased_label)
        layout.addWidget(self.goods_purchased)

        self.quantity_label = QLabel("Quantity:")
        self.quantity = QLineEdit(str(quantity))
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price = QLineEdit(str(unit_price))
        layout.addWidget(self.unit_price_label)
        layout.addWidget(self.unit_price)

        self.total_label = QLabel("Total:")
        self.total = QLineEdit()  # Total field will be disabled for editing
        self.total.setEnabled(False)
        layout.addWidget(self.total_label)
        layout.addWidget(self.total)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def save(self):
        try:
            # Get updated debt information from the dialog fields
            creditor = self.creditor.text()
            date = self.date.text()
            goods_purchased = self.goods_purchased.text()
            quantity = int(self.quantity.text())
            unit_price = float(self.unit_price.text())

            # Calculate total
            total = quantity * unit_price

            # Update the debt in the database
            database.update_debt(self.debt_id, creditor, date, goods_purchased, quantity, unit_price, total)

            # Close the dialog
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numeric values for Quantity and Unit Price.")


def main():
    app = QApplication(sys.argv)
    window = MotobApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
