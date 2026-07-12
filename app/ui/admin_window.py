import os
import glob

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtCore import QTimer
from config.settings import MODEL_PATH, DEFAULT_OUTPUT_MODEL_PATH, AUTO_LABELED_DIR
from core.model_manager import get_current_model_path
from core.model_manager import list_available_models

class AutoLabelWorker(QThread):
    progress_updated = Signal(int, int, str, int)
    finished_all = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, image_folder, output_folder):
        super().__init__()
        self.image_folder = image_folder
        self.output_folder = output_folder

    def run(self):
        try:
            from core.auto_label import auto_label_folder

            def on_progress(current, total, filename, cell_count):
                self.progress_updated.emit(current, total, filename, cell_count)

            results = auto_label_folder(
                self.image_folder,
                self.output_folder,
                progress_callback=on_progress
            )
            self.finished_all.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AutoLabelTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self._get_style())
        self.image_folder = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("批量自动标注")
        title.setObjectName("title")

        top_bar = QHBoxLayout()
        select_btn = QPushButton("选择图片文件夹")
        select_btn.clicked.connect(self._on_select_folder)
        self.folder_label = QLabel("尚未选择文件夹")
        self.folder_label.setObjectName("folder_label")
        top_bar.addWidget(select_btn)
        top_bar.addWidget(self.folder_label)
        top_bar.addStretch(1)

        self.start_btn = QPushButton("开始自动标注")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")

        self.result_list = QListWidget()

        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.result_list)

        self.setLayout(layout)

    def _on_select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择存放图片的文件夹")
        if folder:
            self.image_folder = folder
            self.folder_label.setText(folder)
            self.start_btn.setEnabled(True)

    def _on_start_clicked(self):
        if self.image_folder is None:
            return

        self.result_list.clear()
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.status_label.setText("正在准备...")

        output_folder = AUTO_LABELED_DIR

        self.worker = AutoLabelWorker(self.image_folder, output_folder)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.finished_all.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_progress_updated(self, current, total, filename, cell_count):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"正在处理 {current}/{total}: {filename}")
        self.result_list.addItem(f"{filename} -> 检测到 {cell_count} 个细胞")

    def _on_finished(self, results):
        self.status_label.setText(f"全部完成，共处理 {len(results)} 张图片")
        self.start_btn.setEnabled(True)

    def _on_error(self, error_message):
        self.status_label.setText(f"出错了: {error_message}")
        self.start_btn.setEnabled(True)

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
            #folder_label {
                color: #8a93a3;
                font-size: 12px;
            }
            #status_label {
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
            QPushButton:disabled {
                background-color: #2c3440;
                color: #6b7280;
            }
            QListWidget {
                background-color: #1e242e;
                border: 1px solid #2c3440;
                border-radius: 6px;
            }
            QProgressBar {
                background-color: #1e242e;
                border: 1px solid #2c3440;
                border-radius: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4fd1c5;
            }
        """

class TrainWorker(QThread):
    finished_ok = Signal(str, list, int)
    error_occurred = Signal(str)

    def __init__(self, data_folder, base_model_path, output_model_path, n_epochs):
        super().__init__()
        self.data_folder = data_folder
        self.base_model_path = base_model_path
        self.output_model_path = output_model_path
        self.n_epochs = n_epochs

    def run(self):
        try:
            from core.train_model import retrain_model
            new_model_path, train_losses, image_count = retrain_model(
                self.data_folder,
                self.base_model_path,
                self.output_model_path,
                n_epochs=self.n_epochs
            )
            self.finished_ok.emit(new_model_path, train_losses, image_count)
        except Exception as e:
            self.error_occurred.emit(str(e))

class TrainingPlaceholderTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self._get_style())
        self.data_folder = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("闭环训练：用修正后的数据继续训练模型")
        title.setObjectName("title")

        top_bar = QHBoxLayout()
        select_btn = QPushButton("选择已修正标注的文件夹")
        select_btn.clicked.connect(self._on_select_folder)
        self.folder_label = QLabel("尚未选择文件夹")
        self.folder_label.setObjectName("folder_label")
        top_bar.addWidget(select_btn)
        top_bar.addWidget(self.folder_label)
        top_bar.addStretch(1)

        self.start_btn = QPushButton("开始训练")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setEnabled(False)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")

        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        self.setLayout(layout)

    def _on_select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择存放已修正图片+json的文件夹")
        if folder:
            self.data_folder = folder
            self.folder_label.setText(folder)
            self.start_btn.setEnabled(True)

    def _on_start_clicked(self):
        if self.data_folder is None:
            return

        self.start_btn.setEnabled(False)
        self.status_label.setText("正在训练，请稍候（这个过程可能需要几分钟）...")

        output_path = DEFAULT_OUTPUT_MODEL_PATH

        self.worker = TrainWorker(
            self.data_folder,
            MODEL_PATH,
            output_path,
            n_epochs=100
        )
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, new_model_path, train_losses, image_count):
        final_loss = train_losses[-1] if len(train_losses) > 0 else "未知"
        self.status_label.setText(
            f"训练完成！用了{image_count}张图片，新模型已保存到:\n{new_model_path}\n最终loss: {final_loss}"
        )
        self.start_btn.setEnabled(True)

    def _on_error(self, error_message):
        self.status_label.setText(f"训练出错: {error_message}")
        self.start_btn.setEnabled(True)

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
            #folder_label {
                color: #8a93a3;
                font-size: 12px;
            }
            #status_label {
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
            QPushButton:disabled {
                background-color: #2c3440;
                color: #6b7280;
            }
        """

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SegStudio - 管理员训练控制台")
        self.resize(1120, 760)
        self.setMinimumSize(800, 550)
        self.setStyleSheet(self._get_shell_style())
        self.next_window = None
        self._tabs_loaded = False
        self._build_ui()
        self._refresh_overview()
        QTimer.singleShot(0, self._load_tabs)

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 10, 16, 10)
        title = QLabel("SegStudio 管理员模式")
        title.setObjectName("shell_title")
        subtitle = QLabel("任务闭环：自动标注 → 修正数据 → 训练模型 → 切换部署")
        subtitle.setObjectName("shell_subtitle")
        exit_btn = QPushButton("退出登录")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self._on_exit_clicked)
        top_bar.addWidget(title)
        top_bar.addStretch(1)
        top_bar.addWidget(subtitle)
        top_bar.addWidget(exit_btn)

        overview_box = QGroupBox("工作流总览")
        overview_box.setObjectName("overview_box")
        overview_layout = QVBoxLayout()
        self.overview_label = QLabel("")
        self.overview_label.setWordWrap(True)
        self.overview_label.setObjectName("overview_label")
        quick_bar = QHBoxLayout()
        self.auto_btn = QPushButton("进入自动标注")
        self.auto_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        self.train_btn = QPushButton("进入训练")
        self.train_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        self.model_btn = QPushButton("进入模型管理")
        self.model_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        quick_bar.addWidget(self.auto_btn)
        quick_bar.addWidget(self.train_btn)
        quick_bar.addWidget(self.model_btn)
        overview_layout.addWidget(self.overview_label)
        overview_layout.addLayout(quick_bar)
        overview_box.setLayout(overview_layout)

        self.change_password_btn = QPushButton("修改管理员密码")
        self.change_password_btn.setObjectName("change_password_btn")
        self.change_password_btn.clicked.connect(self._on_change_password_clicked)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("admin_tabs")
        loading_widget = QWidget()
        loading_layout = QVBoxLayout()
        loading_label = QLabel("正在初始化管理员工作台，请稍候...")
        loading_label.setObjectName("loading_label")
        loading_layout.addStretch(1)
        loading_layout.addWidget(loading_label, 0, Qt.AlignCenter)
        loading_layout.addStretch(1)
        loading_widget.setLayout(loading_layout)
        self.tabs.addTab(loading_widget, "准备中")

        outer_layout.addLayout(top_bar)
        outer_layout.addWidget(overview_box)
        outer_layout.addWidget(self.change_password_btn, 0, Qt.AlignRight)
        outer_layout.addWidget(self.tabs)

        self.setLayout(outer_layout)

    def _refresh_overview(self):
        auto_labeled_dir = AUTO_LABELED_DIR
        model_files = list_available_models()
        label_files = glob.glob(os.path.join(auto_labeled_dir, "*.json"))
        current_model = get_current_model_path()
        self.overview_label.setText(
            f"已发现自动标注结果：{len(label_files)} 份；可用模型文件：{len(model_files)} 个；当前使用模型：{current_model}"
        )

    def _load_tabs(self):
        if self._tabs_loaded:
            return
        self._tabs_loaded = True
        self.tabs.clear()
        self.tabs.addTab(AutoLabelTab(), "批量自动标注")
        self.tabs.addTab(TrainingPlaceholderTab(), "模型训练")
        from ui.model_management_tab import ModelManagementTab
        self.tabs.addTab(ModelManagementTab(), "模型管理")

    def _on_change_password_clicked(self):
        from ui.change_password_window import ChangePasswordWindow
        dialog = ChangePasswordWindow(self)
        dialog.exec()

    def _on_exit_clicked(self):
        from ui.login_window import LoginWindow
        self.next_window = LoginWindow()
        self.next_window.show()
        self.close()

    def _get_shell_style(self):
        return """
            QWidget {
                background-color: #14181f;
                color: #e6e6e6;
                font-family: "Microsoft YaHei";
            }
            #shell_title {
                font-size: 18px;
                font-weight: bold;
                color: #4fd1c5;
            }
            #shell_subtitle {
                color: #94a3b8;
                font-size: 12px;
            }
            #overview_box {
                border: 1px solid #2c3440;
                border-radius: 10px;
                padding: 10px;
                margin: 10px 16px 0 16px;
            }
            #overview_label {
                color: #cbd5e1;
                font-size: 12px;
            }
            #loading_label {
                color: #94a3b8;
                font-size: 12px;
            }
            #exit_btn {
                background-color: #2c3440;
                color: #e6e6e6;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            #exit_btn:hover {
                background-color: #3a4354;
            }
            #change_password_btn {
                background-color: #334155;
                color: #e6e6e6;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 8px 14px;
                margin: 0 16px 8px 16px;
                max-width: 180px;
            }
            #change_password_btn:hover {
                background-color: #475569;
            }
            QTabWidget::pane {
                border-top: 1px solid #2c3440;
            }
            QTabBar::tab {
                background-color: #1a1f28;
                color: #8a93a3;
                padding: 10px 20px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #14181f;
                color: #4fd1c5;
                border-bottom: 2px solid #4fd1c5;
            }
            QPushButton {
                background-color: #14b8a6;
                color: #04131a;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """