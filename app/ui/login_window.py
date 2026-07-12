from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from config.settings import get_admin_password, is_admin_password_correct

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SegStudio 分割模型训练系统")
        self.setFixedSize(440, 500)
        self.setStyleSheet(self._get_style())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 50, 40, 40)
        layout.setSpacing(14)

        title = QLabel("SegStudio")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        subtitle = QLabel("轻量级去红细胞分割与训练平台")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitle")

        intro = QLabel("支持快速查看分割结果、批量自动标注、模型训练闭环与管理切换")
        intro.setAlignment(Qt.AlignCenter)
        intro.setWordWrap(True)
        intro.setObjectName("intro")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入密码进入管理员模式（留空则进入普通模式）")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_enter_clicked)

        enter_btn = QPushButton("进入系统")
        enter_btn.clicked.connect(self._on_enter_clicked)

        self.hint_label = QLabel("")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setObjectName("hint")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(intro)
        layout.addStretch(1)
        layout.addWidget(self.password_input)
        layout.addWidget(enter_btn)
        layout.addWidget(self.hint_label)
        layout.addStretch(1)

        self.setLayout(layout)

    def _on_enter_clicked(self):
        pwd = self.password_input.text()
        if pwd == "":
            self.hint_label.setText("正在进入普通模式...")
            from ui.main_window import MainWindow
            self.next_window = MainWindow()
            self.next_window.show()
            self.close()
        elif is_admin_password_correct(pwd):
            self.hint_label.setText("密码正确，正在进入管理员模式...")
            from ui.admin_window import AdminWindow
            self.next_window = AdminWindow()
            self.next_window.show()
            self.close()
        else:
            self.hint_label.setText("密码错误，请重新输入")

    def _get_style(self):
        return """
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: "Microsoft YaHei";
            }
            #title {
                font-size: 28px;
                font-weight: bold;
                color: #5eead4;
            }
            #subtitle {
                font-size: 13px;
                color: #cbd5e1;
            }
            #intro {
                font-size: 12px;
                color: #94a3b8;
            }
            #hint {
                font-size: 12px;
                color: #5eead4;
            }
            QLineEdit {
                background-color: #111827;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #5eead4;
            }
            QPushButton {
                background-color: #14b8a6;
                color: #04131a;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """