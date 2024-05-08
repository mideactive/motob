import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QTabWidget, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from motob_app import MotobApp

class MainUserWindow(QMainWindow):
    # Define a signal for logout
    logout_signal = pyqtSignal()

    def __init__(self, username, logout_function=None):
        super().__init__()
        self.username = username
        self.logout_function = logout_function
        self.setWindowTitle(f"Welcome, {username}")

        self.setup_ui()

    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.motob_app_tab = QWidget()
        self.tab_widget.addTab(self.motob_app_tab, "Motob App")
        self.setup_motob_app_tab()

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.logout_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setup_motob_app_tab(self):
        layout = QVBoxLayout(self.motob_app_tab)
        label = QLabel("Motob Transactions:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.motob_app = MotobApp()
        layout.addWidget(self.motob_app)

    def logout(self):
        # Emit the logout signal when the logout button is clicked
        if self.logout_function:
            self.logout_function()
        self.logout_signal.emit()


def main():
    app = QApplication(sys.argv)
    user_window = MainUserWindow("test_user")
    user_window.show()
    sys.exit(app.exec_())


def show_user_management_window():
    from gui import UserManagementWindow
    user_management_window = UserManagementWindow()
    user_management_window.show()

if __name__ == "__main__":
    main()
