from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

from config.settings import get_admin_password, set_admin_password


class ChangePasswordWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改管理员密码")
        self.resize(420, 320)
        self.setModal(True)
        self.setStyleSheet(self._get_style())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("修改管理员密码")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        hint = QLabel("请先输入当前密码，再设置新的密码并确认。")
        hint.setWordWrap(True)
        hint.setObjectName("hint")

        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("输入当前密码")
        self.current_password_input.setEchoMode(QLineEdit.Password)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("输入新密码")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("再次输入新密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        btn_row = QHBoxLayout()
        confirm_btn = QPushButton("确认修改")
        confirm_btn.clicked.connect(self._on_confirm)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch(1)
        btn_row.addWidget(confirm_btn)
        btn_row.addWidget(cancel_btn)

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.current_password_input)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _on_confirm(self):
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if current_password != get_admin_password():
            QMessageBox.warning(self, "修改失败", "当前密码输入不正确")
            return
        if not new_password:
            QMessageBox.warning(self, "修改失败", "新密码不能为空")
            return
        if new_password != confirm_password:
            QMessageBox.warning(self, "修改失败", "两次输入的新密码不一致")
            return

        set_admin_password(new_password)
        QMessageBox.information(self, "修改成功", "管理员密码已成功更新")
        self.accept()

    def _get_style(self):
        return """
            QWidget {
                background-color: #14181f;
                color: #e6e6e6;
                font-family: "Microsoft YaHei";
            }
            #title {
                font-size: 18px;
                font-weight: bold;
                color: #4fd1c5;
            }
            #hint {
                color: #94a3b8;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1e242e;
                border: 1px solid #2c3440;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #14b8a6;
                color: #04131a;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """
