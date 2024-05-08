# admin_gui.py
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QWidget, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QCheckBox, QSizePolicy
)
from PyQt5.QtCore import Qt
import database
from motob_app import MotobApp
import re
import hashlib  # Import hashlib for password hashing
import sys

# Define the regular expressions for valid usernames and passwords
USERNAME_PATTERN = r"^[a-zA-Z0-9_-]{3,20}$"
PASSWORD_PATTERN = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-+]).{8,}$"

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Interface")

        self.tab_widget = QTabWidget()
        self.user_management_tab = QWidget()
        self.permission_management_tab = QWidget()
        self.activity_log_tab = QWidget()
        self.motob_app_tab = QWidget()  # Define the motob_app_tab attribute

        self.tab_widget.addTab(self.user_management_tab, "User Management")
        self.tab_widget.addTab(self.permission_management_tab, "Permission Management")
        self.tab_widget.addTab(self.activity_log_tab, "Activity Log")
        self.tab_widget.addTab(self.motob_app_tab, "Motob App")  # Add the tab here

        self.setup_user_management_tab()
        self.setup_permission_management_tab()
        self.setup_activity_log_tab()
        self.setup_motob_app_tab()

        # Add logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)

        # Add the tab widget and logout button to the central widget layout
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.tab_widget)
        central_layout.addWidget(self.logout_button, alignment=Qt.AlignBottom)  # Align logout button to the bottom
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Ensure visibility of the permission_management_tab
        self.tab_widget.setCurrentWidget(self.permission_management_tab)


    def setup_user_management_tab(self):
        layout = QVBoxLayout()

        # Username input field
        self.user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)

        # Password input field
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Create user button
        self.create_user_button = QPushButton("Create User")
        self.create_user_button.clicked.connect(self.create_user)
        layout.addWidget(self.create_user_button)

        self.user_management_tab.setLayout(layout)

    def setup_permission_management_tab(self):
        layout = QVBoxLayout()

        self.user_list_label = QLabel("User List:")
        self.user_list = QListWidget()
        self.refresh_user_list()

        # Add grant and revoke buttons
        self.grant_button = QPushButton("Grant Permission")
        self.grant_button.clicked.connect(self.grant_permission)

        self.revoke_button = QPushButton("Revoke Permission")
        self.revoke_button.clicked.connect(self.revoke_permission)

        # Add buttons to a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.grant_button)
        button_layout.addWidget(self.revoke_button)

        layout.addWidget(self.user_list_label)
        layout.addWidget(self.user_list)
        layout.addLayout(button_layout)  # Add button layout to the main layout

        self.permission_management_tab.setLayout(layout)
        self.permission_management_tab.setVisible(True)  # Set the tab to be visible
        print("permission_management_tab visibility:", self.permission_management_tab.isVisible())

    def setup_motob_app_tab(self):
        layout = QVBoxLayout(self.motob_app_tab)

        label = QLabel("Motob Transactions:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Create an instance of MotobApp and add it to the layout
        self.motob_app = MotobApp()
        layout.addWidget(self.motob_app)

    def setup_activity_log_tab(self):
        # Here, you can set up the activity log tab
        layout = QVBoxLayout()
        self.activity_log_list = QListWidget()
        layout.addWidget(self.activity_log_list)
        self.activity_log_tab.setLayout(layout)

    def refresh_activity_log(self):
        activities = database.get_activity_log()
        self.activity_log_list.clear()
        for activity in activities:
            item = QListWidgetItem(activity)
            self.activity_log_list.addItem(item)

    def create_user(self):
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        # Validate username and password against the defined patterns
        if not re.match(USERNAME_PATTERN, username):
            QMessageBox.warning(self, "Warning", "Invalid username. Username must be 3-20 characters long and can contain only letters, numbers, '_', and '-'.")
            return

        if not re.match(PASSWORD_PATTERN, password):
            QMessageBox.warning(self, "Warning", "Invalid password. Password must be at least 8 characters long and contain at least one digit, one lowercase letter, one uppercase letter, and one special character.")
            return

        if database.get_user(username):
            QMessageBox.warning(self, "Warning", "User already exists.")
            return

        # Hash the password
        hashed_password = hash_password(password)

        # Add user to the database with the hashed password
        try:
            database.add_user(username, hashed_password)
            QMessageBox.information(self, "Success", "User created successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")

        # Clear input fields
        self.user_input.clear()
        self.password_input.clear()

    def refresh_user_list(self):
        users = database.get_all_users_with_permissions()
        print("Users fetched from the database:", users)  # Print out the users fetched from the database
        self.user_list.clear()
        for user in users:
            username, is_admin, has_permissions = user
            item = QListWidgetItem(username)

            # Create a container widget to hold the layout
            container_widget = QWidget()
            main_layout = QVBoxLayout(container_widget)

            # Add username label
            username_label = QLabel(username)
            main_layout.addWidget(username_label)

            # Add checkboxes for edit and delete privileges
            edit_privilege_checkbox = QCheckBox("Edit Privilege")
            delete_privilege_checkbox = QCheckBox("Delete Privilege")

            # Set initial checkbox states based on user's permissions
            edit_privilege_checkbox.setChecked(bool(has_permissions))
            delete_privilege_checkbox.setChecked(bool(has_permissions))

            # Add checkboxes to the layout
            main_layout.addWidget(edit_privilege_checkbox)
            main_layout.addWidget(delete_privilege_checkbox)

            # Set the container widget as the item widget
            item.setSizeHint(container_widget.sizeHint())  # Set the size hint of the item
            self.user_list.addItem(item)
            self.user_list.setItemWidget(item, container_widget)

    def grant_permission(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a user.")
            return

        for item in selected_items:
            username = item.text()
            # Update database with the new permission status
            database.grant_permissions(username)  # Call the grant_permissions function
            QMessageBox.information(self, "Success", f"Permission granted for user: {username}")
        self.refresh_user_list()

    def revoke_permission(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a user.")
            return

        for item in selected_items:
            username = item.text()
            # Update database with the new permission status (revoke permissions)
            database.revoke_permissions(username)  # Call the revoke_permissions function
            QMessageBox.information(self, "Success", f"Permission revoked for user: {username}")
        self.refresh_user_list()

    def logout(self):
        # Hide the AdminWindow
        self.hide()
        # Show the UserManagementWindow
        user_management_window.show()

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
