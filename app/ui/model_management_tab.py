import os

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QListWidgetItem

from core.model_manager import get_current_model_path
from core.model_manager import set_current_model_path
from core.model_manager import list_available_models
from config.settings import MODELS_FOLDER

class ModelManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self._get_style())
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("模型管理")
        title.setObjectName("title")

        self.current_label = QLabel("")
        self.current_label.setObjectName("current_label")
        self.current_label.setWordWrap(True)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("summary_label")

        self.model_list = QListWidget()

        btn_bar = QHBoxLayout()
        apply_btn = QPushButton("设为当前使用模型")
        apply_btn.clicked.connect(self._on_apply_clicked)
        browse_btn = QPushButton("浏览选择其他模型文件")
        browse_btn.clicked.connect(self._on_browse_clicked)
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self._refresh_list)
        btn_bar.addWidget(apply_btn)
        btn_bar.addWidget(browse_btn)
        btn_bar.addWidget(refresh_btn)

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("hint_label")

        layout.addWidget(title)
        layout.addWidget(self.current_label)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.model_list)
        layout.addLayout(btn_bar)
        layout.addWidget(self.hint_label)

        self.setLayout(layout)

    def _refresh_list(self):
        self.model_list.clear()
        current_path = get_current_model_path()
        available_models = list_available_models()
        self.current_label.setText(f"当前使用模型：{current_path}")
        self.summary_label.setText(f"已发现可用模型：{len(available_models)} 个")

        for model_path in available_models:
            item = QListWidgetItem(os.path.basename(model_path))
            item.setToolTip(model_path)
            self.model_list.addItem(item)
            if model_path == current_path:
                item.setSelected(True)

    def _on_apply_clicked(self):
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            self.hint_label.setText("请先在列表里选中一个模型")
            return

        selected_path = selected_items[0].toolTip()
        if not selected_path:
            selected_path = selected_items[0].text()

        set_current_model_path(selected_path)
        self.hint_label.setText("切换成功，下次进入普通模式将使用新模型")
        self._refresh_list()

    def _on_browse_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            MODELS_FOLDER,
            "模型文件 (*.pth *.pt)"
        )
        if file_path:
            set_current_model_path(file_path)
            self.hint_label.setText("切换成功，下次进入普通模式将使用新模型")
            self._refresh_list()

    def _get_style(self):
        return """
            QWidget {
                background-color: #14181f;
                color: #e6e6e6;
                font-family: "Microsoft YaHei";
            }
            #title {
                font-size: 20px;
                font-weight: bold;
                color: #4fd1c5;
            }
            #current_label {
                color: #8a93a3;
                font-size: 12px;
            }
            #summary_label {
                color: #94a3b8;
                font-size: 12px;
            }
            #hint_label {
                color: #4fd1c5;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4fd1c5;
                color: #0f1216;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3fb8ad;
            }
            QListWidget {
                background-color: #1e242e;
                border: 1px solid #2c3440;
                border-radius: 6px;
            }
        """