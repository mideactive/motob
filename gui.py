from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTabWidget, QWidget, QApplication,
    QMainWindow, QCheckBox
)
from PyQt5.QtCore import pyqtSlot
import hashlib
import database
from admin_gui import AdminWindow  # Import AdminWindow
from user_gui import MainUserWindow

class UserManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Management")

        self.tab_widget = QTabWidget()

        self.create_account_tab = QWidget()
        self.admin_login_tab = QWidget()  # New tab for admin login
        self.user_login_tab = QWidget()   # New tab for user login

        self.tab_widget.addTab(self.create_account_tab, "Create Account")
        self.tab_widget.addTab(self.admin_login_tab, "Admin Login")  # Tab for admin login
        self.tab_widget.addTab(self.user_login_tab, "User Login")    # Tab for user login

        self.setup_create_account_tab()
        self.setup_admin_login_tab()  # Setup admin login tab
        self.setup_user_login_tab()   # Setup user login tab

        self.setCentralWidget(self.tab_widget)
        self.user_window = None
        self.admin_logged_in = False  # Track if admin is logged in
        self.create_account_tab.hide()  # Hide create account tab initially

    def setup_create_account_tab(self):
        layout = QVBoxLayout()

        self.create_username_label = QLabel("Username:")
        self.create_username_input = QLineEdit()

        self.create_password_label = QLabel("Password:")
        self.create_password_input = QLineEdit()
        self.create_password_input.setEchoMode(QLineEdit.Password)

        self.create_admin_checkbox = QCheckBox("Admin")

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.clicked.connect(self.create_account)

        layout.addWidget(self.create_username_label)
        layout.addWidget(self.create_username_input)
        layout.addWidget(self.create_password_label)
        layout.addWidget(self.create_password_input)
        layout.addWidget(self.create_admin_checkbox)
        layout.addWidget(self.create_account_button)

        self.create_account_tab.setLayout(layout)

    # Define the create_account method
    def create_account(self):
        # Check if the users table is empty
        if not database.get_all_users():
            # Allow user registration without admin authentication if the table is empty
            admin_required = False
        else:
            # Admin authentication is required if the table is not empty
            admin_required = True

        if admin_required and not self.admin_logged_in:
            QMessageBox.warning(self, "Warning", "Only admin can create accounts.")
            return

        username = self.create_username_input.text()
        password = self.create_password_input.text()
        is_admin = self.create_admin_checkbox.isChecked()

        if not username or not password:
            QMessageBox.warning(self, "Warning", "Please enter username and password.")
            return

        if database.get_user(username):
            QMessageBox.warning(self, "Warning", "User already exists.")
            return

        # Hash the password before storing it in the database
        hashed_password = hash_password(password)

        database.add_user(username, hashed_password, is_admin)
        QMessageBox.information(self, "Success", "User account created successfully.")

        # Clear input fields after account creation
        self.create_username_input.clear()
        self.create_password_input.clear()
        self.create_admin_checkbox.setChecked(False)

    def setup_admin_login_tab(self):
        layout = QVBoxLayout()

        self.admin_login_username_label = QLabel("Username:")
        self.admin_login_username_input = QLineEdit()

        self.admin_login_password_label = QLabel("Password:")
        self.admin_login_password_input = QLineEdit()
        self.admin_login_password_input.setEchoMode(QLineEdit.Password)

        self.admin_login_button = QPushButton("Login")
        # Connect the login button to the admin_login method
        self.admin_login_button.clicked.connect(self.admin_login)

        layout.addWidget(self.admin_login_username_label)
        layout.addWidget(self.admin_login_username_input)
        layout.addWidget(self.admin_login_password_label)
        layout.addWidget(self.admin_login_password_input)
        layout.addWidget(self.admin_login_button)

        self.admin_login_tab.setLayout(layout)

    def setup_user_login_tab(self):
        layout = QVBoxLayout()

        self.user_login_username_label = QLabel("Username:")
        self.user_login_username_input = QLineEdit()

        self.user_login_password_label = QLabel("Password:")
        self.user_login_password_input = QLineEdit()
        self.user_login_password_input.setEchoMode(QLineEdit.Password)

        self.user_login_button = QPushButton("Login")
        self.user_login_button.clicked.connect(self.user_login)

        layout.addWidget(self.user_login_username_label)
        layout.addWidget(self.user_login_username_input)
        layout.addWidget(self.user_login_password_label)
        layout.addWidget(self.user_login_password_input)
        layout.addWidget(self.user_login_button)

        self.user_login_tab.setLayout(layout)

    def user_login(self):
        username = self.user_login_username_input.text()
        password = self.user_login_password_input.text()

        user = database.get_user(username)

        if not user:
            QMessageBox.warning(self, "Warning", "User does not exist.")
            return

        # Hash the input password for comparison
        hashed_input_password = hash_password(password)

        # Compare hashed passwords
        if user[2] != hashed_input_password:  # Check against hashed password from the database
            QMessageBox.warning(self, "Warning", "Incorrect password.")
            return

        if user[3] == 0 or (user[3] == 1 and self.admin_logged_in):  # Check if the user is a regular user or if admin is logged in
            self.user_window = MainUserWindow(username, self.logout)
            self.user_window.show()
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self.hide()
        else:
            QMessageBox.warning(self, "Warning", "This is not a regular user account.")

        # Clear input fields after successful login
        self.user_login_username_input.clear()
        self.user_login_password_input.clear()

    # Define a slot to handle logout action
    @pyqtSlot()
    def logout(self):
        if self.user_window:
            self.user_window.hide()

        self.tab_widget.setCurrentWidget(self.user_login_tab)

    def admin_login(self):
        username = self.admin_login_username_input.text()
        password = self.admin_login_password_input.text()

        user = database.get_user(username)

        if not user:
            QMessageBox.warning(self, "Warning", "User does not exist.")
            return

        # Hash the input password for comparison
        hashed_input_password = hash_password(password)

        # Compare hashed passwords
        if user[2] != hashed_input_password:  # Check against hashed password from the database
            QMessageBox.warning(self, "Warning", "Incorrect password.")
            return

        if user[3] == 1:  # Check if the user is an admin
            self.admin_logged_in = True  # Set admin logged in
            self.create_account_tab.show()  # Show create account tab
            # Instantiate and show the AdminWindow
            self.admin_window = AdminWindow()
            self.admin_window.show()
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self.hide()
        else:
            QMessageBox.warning(self, "Warning", "This is not an admin account.")

        # Clear input fields after successful login
        self.admin_login_username_input.clear()
        self.admin_login_password_input.clear()

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    app = QApplication(sys.argv)
    user_management_window = UserManagementWindow()
    user_management_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
