import sys
import subprocess
import getpass
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QListWidget)
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt

def execute_command(command):
    """Execute a command using subprocess and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

class TerminalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = getpass.getuser()
        self.command_history = []
        self.logs = []  # Stores logs in the format (datetime, command, response, user)
        self.themes = [
            {"background": "#2E3440", "text": "#ECEFF4", "input_bg": "#3B4252", "input_text": "#ECEFF4"},  # Dark theme
            {"background": "#FFFFFF", "text": "#000000", "input_bg": "#E0E0E0", "input_text": "#000000"},  # Light theme
            {"background": "#1B1B1B", "text": "#E0E0E0", "input_bg": "#333333", "input_text": "#E0E0E0"},  # Black theme
            {"background": "#002B36", "text": "#839496", "input_bg": "#073642", "input_text": "#839496"},  # Solarized dark
            {"background": "#FDF6E3", "text": "#657B83", "input_bg": "#EEE8D5", "input_text": "#657B83"},  # Solarized light
            {"background": "#FAFAFA", "text": "#383838", "input_bg": "#E5E5E5", "input_text": "#383838"},  # Light gray theme
            {"background": "#F0F0F0", "text": "#2C2C2C", "input_bg": "#D9D9D9", "input_text": "#2C2C2C"}   # Cool light theme
        ]

        self.current_theme_index = 0
        self.init_ui()

    def init_ui(self):
        # Set up main layout
        self.setWindowTitle("Custom Terminal")

        self.main_layout = QVBoxLayout()

        # Top buttons
        self.button_layout = QHBoxLayout()

        self.history_button = QPushButton("History")
        self.export_button = QPushButton("Export Logs")
        self.theme_button = QPushButton("Change Theme")

        self.button_layout.addWidget(self.history_button)
        self.button_layout.addWidget(self.export_button)
        self.button_layout.addWidget(self.theme_button)
        self.main_layout.addLayout(self.button_layout)

        # Central text area for displaying commands and responses
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Menlo", 14))

        # Input field for commands
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Menlo", 14))
        self.command_input.setPlaceholderText("Enter your command...")
        self.command_input.returnPressed.connect(self.run_command)

        self.main_layout.addWidget(self.text_display)
        self.main_layout.addWidget(self.command_input)

        # Set layout
        self.setLayout(self.main_layout)
        self.resize(800, 600)

        # Connect buttons
        self.history_button.clicked.connect(self.show_history)
        self.export_button.clicked.connect(self.export_logs)
        self.theme_button.clicked.connect(self.change_theme)

        # Apply theme initially
        self.apply_theme()

        # Display welcome message
        self.text_display.append(f"Hello {self.current_user} - $")

    def apply_theme(self):
        """Apply the current theme to the application."""
        theme = self.themes[self.current_theme_index]
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")

        self.text_display.setStyleSheet(
            f"border: none; background-color: {theme['background']}; color: {theme['text']}; font-family: 'Menlo'; font-size: 16px;"
        )
        self.command_input.setStyleSheet(
            f"border: none; background-color: {theme['input_bg']}; color: {theme['input_text']}; font-family: 'Menlo'; font-size: 16px; padding: 10px;"
        )

        button_style = self.button_style(theme)
        self.history_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        self.theme_button.setStyleSheet(button_style)

        # Update all existing text in the text_display to match the theme's text color
        text_cursor = self.text_display.textCursor()
        text_cursor.select(QTextCursor.Document)
        text_format = text_cursor.charFormat()
        text_format.setForeground(QColor(theme['text']))
        text_cursor.setCharFormat(text_format)

    def adjust_color_brightness(self, color, factor):
        """Adjust the brightness of a given color."""
        color = QColor(color)
        r = min(max(int(color.red() * factor), 0), 255)
        g = min(max(int(color.green() * factor), 0), 255)
        b = min(max(int(color.blue() * factor), 0), 255)
        return f"rgb({r}, {g}, {b})"

    def button_style(self, theme):
        """Return the style for buttons with hover and click effects based on the current theme."""
        return f"""
        QPushButton {{
            background-color: {theme['input_bg']};
            color: {theme['input_text']};
            font-family: 'Menlo';
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.adjust_color_brightness(theme['input_bg'], 1.2)};
        }}
        QPushButton:pressed {{
            background-color: {self.adjust_color_brightness(theme['input_bg'], 0.8)};
        }}
        """

    def run_command(self):
        """Execute the command entered by the user and display the result."""
        command = self.command_input.text()
        if command.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.text_display.setTextColor(QColor(self.themes[self.current_theme_index]['text']))
            self.text_display.setFontWeight(QFont.Bold)
            self.text_display.append(f"{self.current_user} - $ {command}")
            self.text_display.setFontWeight(QFont.Normal)

            result = execute_command(command)

            if "error" in result.lower() or "not found" in result.lower():
                self.text_display.setTextColor(QColor("#BF616A"))  # Error text color
            else:
                self.text_display.setTextColor(QColor(self.themes[self.current_theme_index]['text']))

            self.text_display.append(result)
            self.text_display.append("")  # Add a blank line for separation
            self.text_display.moveCursor(QTextCursor.End)

            # Save to history and logs
            self.command_history.append(command)
            self.logs.append((timestamp, command, result, self.current_user))

        # Clear the input field
        self.command_input.clear()

    def show_history(self):
        """Show command history in a persistent list widget."""
        self.history_dialog = QListWidget()
        theme = self.themes[self.current_theme_index]
        self.history_dialog.setStyleSheet(
            f"background-color: {theme['background']}; color: {theme['text']}; font-family: 'Menlo'; font-size: 14px;"
        )
        self.history_dialog.addItems(self.command_history)
        self.history_dialog.setWindowTitle("Command History")
        self.history_dialog.resize(400, 300)
        self.history_dialog.show()

    def export_logs(self):
        """Export logs to a file."""
        log_file_path = "terminal_logs.txt"
        with open(log_file_path, "w") as f:
            for log in self.logs:
                f.write(f"[{log[0]}] {log[3]} - $ {log[1]}\n{log[2]}\n\n")
        self.text_display.setTextColor(QColor("#88C0D0"))
        self.text_display.append(f"Logs exported to {log_file_path}")
        self.text_display.append("")

    def change_theme(self):
        """Cycle through available themes."""
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        self.apply_theme()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = TerminalApp()
    terminal.show()
    sys.exit(app.exec_())
