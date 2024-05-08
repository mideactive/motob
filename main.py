import sys
from PyQt5.QtWidgets import QApplication
import error_logger
from database import initialize_database, get_user
import database
from admin_gui import AdminWindow
from gui import UserManagementWindow

def initialize_application():
    # Initialize error logging
    error_logger.init_error_log()

    # Initialize the database
    initialize_database()

def main():
    try:
        initialize_application()

        app = QApplication(sys.argv)
        user_management_window = UserManagementWindow()  # Create UserManagementWindow instance first
        admin_window = AdminWindow()  # Don't pass any argument
        user_management_window.admin_window = admin_window  # Set AdminWindow instance in UserManagementWindow
        user_management_window.show()
        sys.exit(app.exec_())

    except Exception as e:
        error_logger.log_error(e)

if __name__ == "__main__":
    main()
