from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QImage
from ui.zoomable_view import ZoomableGraphicsView

import json
import os
import numpy as np
from PIL import Image
from core.model_manager import get_current_model_path
from core.model_manager import set_current_model_path
from core.model_manager import list_available_models
from core.analysis import compute_mask_statistics, filter_masks_by_area
from config.settings import MANUAL_NOTES_DIR


class SegmentationWorker(QThread):
    finished = Signal(object, object, object, object, object)
    error = Signal(str)

    def __init__(self, image_path, model_path, min_area):
        super().__init__()
        self.image_path = image_path
        self.model_path = model_path
        self.min_area = min_area

    def run(self):
        try:
            with Image.open(self.image_path) as img:
                image = np.array(img.convert("RGB"))

            from core.segmentor import Segmentor
            from core.visualize import draw_segmentation_overlay

            segmentor = Segmentor(self.model_path)
            masks = segmentor.predict(image)
            filtered_masks = filter_masks_by_area(masks, min_area=self.min_area)
            stats = compute_mask_statistics(filtered_masks)
            overlay = draw_segmentation_overlay(image, filtered_masks)
            self.finished.emit(image, overlay, filtered_masks, stats, self.min_area)
        except Exception as exc:
            self.error.emit(str(exc))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SegStudio - 普通模式")
        self.resize(1050, 760)
        self.setMinimumSize(760, 560)
        self.setStyleSheet(self._get_style())
        self.image_path = None
        self.original_image = None
        self.overlay_image = None
        self.filtered_masks = None
        self.worker = None
        self.last_saved_result_path = None
        self._build_ui()
        self._refresh_summary()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("SegStudio 结果查看")
        title.setObjectName("title")
        subtitle = QLabel("上传图片后即可快速查看去红细胞分割结果，并保存高质量结果图")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        header.addWidget(title)
        header.addStretch(1)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.clicked.connect(self._on_logout)
        self.switch_model_btn = QPushButton("切换模型")
        self.switch_model_btn.clicked.connect(self._on_switch_model)
        header.addWidget(self.switch_model_btn)
        header.addWidget(self.logout_btn)
        outer_layout.addLayout(header)
        outer_layout.addWidget(subtitle)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        comparison_layout = QHBoxLayout()
        comparison_layout.setSpacing(12)

        self.original_group = QGroupBox("原图")
        self.original_group.setObjectName("view_group")
        original_layout = QVBoxLayout()
        self.original_view = ZoomableGraphicsView()
        self.original_view.setMinimumSize(320, 280)
        self.original_view.setStyleSheet("border: 1px solid #334155; background-color: #111827; border-radius: 10px;")
        original_layout.addWidget(self.original_view)
        self.original_group.setLayout(original_layout)

        self.result_group = QGroupBox("分割结果")
        self.result_group.setObjectName("view_group")
        result_layout = QVBoxLayout()
        self.result_view = ZoomableGraphicsView()
        self.result_view.setMinimumSize(320, 280)
        self.result_view.setStyleSheet("border: 1px solid #334155; background-color: #111827; border-radius: 10px;")
        result_layout.addWidget(self.result_view)
        self.result_group.setLayout(result_layout)

        comparison_layout.addWidget(self.original_group, 1)
        comparison_layout.addWidget(self.result_group, 1)

        control_bar = QHBoxLayout()
        select_btn = QPushButton("选择图片")
        select_btn.clicked.connect(self._on_select_image)
        run_btn = QPushButton("开始分割")
        run_btn.clicked.connect(self._on_run_segmentation)
        self.save_btn = QPushButton("保存结果")
        self.save_btn.clicked.connect(self._on_save_result)
        self.save_btn.setEnabled(False)
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._on_reset)
        control_bar.addWidget(select_btn)
        control_bar.addWidget(run_btn)
        control_bar.addWidget(self.save_btn)
        control_bar.addWidget(reset_btn)

        self.status_label = QLabel("准备就绪：选择一张图片后即可开始分割")
        self.status_label.setObjectName("status")
        self.status_label.setWordWrap(True)

        summary_group = QGroupBox("状态与信息")
        summary_group.setObjectName("summary_group")
        summary_layout = QVBoxLayout()
        self.image_info_label = QLabel("当前图片：未选择")
        self.model_info_label = QLabel("当前模型：")
        self.count_label = QLabel("检测细胞数：0")
        self.stats_label = QLabel("统计：无")
        self.stats_label.setWordWrap(True)
        self.stats_label.setObjectName("tip")

        filter_row = QHBoxLayout()
        filter_label = QLabel("最小面积")
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(1, 500)
        self.min_area_spinbox.setValue(3)
        self.min_area_spinbox.setToolTip("过滤掉小于该像素面积的碎片")
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.min_area_spinbox)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("可在这里记录人工修正意见或观察结果")
        self.notes_edit.setMaximumHeight(90)

        note_btn = QPushButton("保存修正说明")
        note_btn.clicked.connect(self._on_save_notes)
        recent_btn = QPushButton("打开上次结果")
        recent_btn.clicked.connect(self._on_open_last_result)

        self.tip_label = QLabel("提示：分割完成后可直接保存结果图，便于后续人工修正和训练")
        self.tip_label.setWordWrap(True)
        self.tip_label.setObjectName("tip")

        summary_layout.addWidget(self.image_info_label)
        summary_layout.addWidget(self.model_info_label)
        summary_layout.addWidget(self.count_label)
        summary_layout.addWidget(self.stats_label)
        summary_layout.addLayout(filter_row)
        summary_layout.addWidget(self.tip_label)
        summary_layout.addWidget(self.notes_edit)
        summary_layout.addWidget(note_btn)
        summary_layout.addWidget(recent_btn)
        summary_group.setLayout(summary_layout)

        content_layout.addLayout(comparison_layout, 3)
        content_layout.addWidget(summary_group, 1)

        outer_layout.addLayout(content_layout)
        outer_layout.addLayout(control_bar)
        outer_layout.addWidget(self.status_label)

        self.setLayout(outer_layout)

    def _refresh_summary(self):
        current_model = get_current_model_path()
        self.model_info_label.setText(f"当前模型：{current_model}")
        self.tip_label.setText(
            f"可用模型：{len(list_available_models())} 个。"
            "可通过切换模型按钮快速切换推理模型。"
        )

    def _array_to_pixmap(self, image):
        image = np.ascontiguousarray(image)
        if image.ndim == 2:
            image = np.repeat(image[..., np.newaxis], 3, axis=2)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    def _on_select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "Images (*.png *.jpg *.jpeg *.tif *.tiff)"
        )
        if path:
            self.image_path = path
            with Image.open(path) as img:
                self.original_image = np.array(img.convert("RGB"))
            self.overlay_image = None
            pixmap = QPixmap(path)
            self.original_view.set_pixmap(pixmap)
            self.result_view.set_pixmap(QPixmap())
            self.image_info_label.setText(f"当前图片：{path}")
            self.count_label.setText("检测细胞数：0")
            self.save_btn.setEnabled(False)
            self.status_label.setText("图片已加载，点击开始分割")

    def _on_run_segmentation(self):
        if self.image_path is None:
            self.status_label.setText("请先选择一张图片")
            return

        self.status_label.setText("正在加载模型并执行分割，请稍候...")
        self.save_btn.setEnabled(False)
        self.worker = SegmentationWorker(
            self.image_path,
            get_current_model_path(),
            self.min_area_spinbox.value()
        )
        self.worker.finished.connect(self._on_segmentation_finished)
        self.worker.error.connect(self._on_segmentation_error)
        self.worker.start()

    def _on_segmentation_finished(self, original_image, overlay, filtered_masks, stats, min_area):
        self.original_image = original_image
        self.overlay_image = overlay
        self.filtered_masks = filtered_masks
        self.original_view.set_pixmap(self._array_to_pixmap(original_image))
        self.result_view.set_pixmap(self._array_to_pixmap(overlay))
        self.count_label.setText(f"检测细胞数：{stats['cell_count']}")
        self.stats_label.setText(
            f"统计：目标数 {stats['cell_count']}，平均面积 {stats['average_area']:.1f}，最大面积 {stats['max_area']}"
        )
        self.status_label.setText(
            f"分割完成，已按最小面积 {min_area} 过滤后显示，共检测到 {stats['cell_count']} 个目标"
        )
        self.save_btn.setEnabled(True)

    def _on_segmentation_error(self, message):
        self.status_label.setText(f"分割失败：{message}")
        QMessageBox.critical(self, "分割失败", message)
        self.save_btn.setEnabled(False)

    def _on_save_result(self):
        if self.overlay_image is None:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存分割结果",
            "segmentation_result.png",
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        if save_path:
            image = Image.fromarray(self.overlay_image)
            image.save(save_path)
            self.last_saved_result_path = save_path
            self.status_label.setText(f"结果已保存到：{save_path}")

    def _on_reset(self):
        self.image_path = None
        self.original_image = None
        self.overlay_image = None
        self.image_info_label.setText("当前图片：未选择")
        self.count_label.setText("检测细胞数：0")
        self.stats_label.setText("统计：无")
        self.save_btn.setEnabled(False)
        self.status_label.setText("已重置，欢迎继续上传新的样本")
        self.original_view.set_pixmap(QPixmap())
        self.result_view.set_pixmap(QPixmap())

    def _on_switch_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models"),
            "模型文件 (*.pth *.pt)"
        )
        if file_path:
            set_current_model_path(file_path)
            self._refresh_summary()
            self.status_label.setText(f"已切换模型：{file_path}")

    def _on_save_notes(self):
        if self.image_path is None:
            self.status_label.setText("请先选择或分割一张图片后再保存说明")
            return

        notes_dir = MANUAL_NOTES_DIR
        os.makedirs(notes_dir, exist_ok=True)
        note_path = os.path.join(notes_dir, f"{os.path.splitext(os.path.basename(self.image_path))[0]}_notes.json")
        payload = {
            "image_path": self.image_path,
            "model_path": get_current_model_path(),
            "min_area": self.min_area_spinbox.value(),
            "notes": self.notes_edit.toPlainText(),
        }
        with open(note_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        self.status_label.setText(f"修正说明已保存到：{note_path}")

    def _on_open_last_result(self):
        if self.last_saved_result_path and os.path.exists(self.last_saved_result_path):
            pixmap = QPixmap(self.last_saved_result_path)
            if not pixmap.isNull():
                self.result_view.set_pixmap(pixmap)
                self.status_label.setText(f"已加载最近保存结果：{self.last_saved_result_path}")
                return
        self.status_label.setText("尚未保存过结果，先执行一次保存即可加载最近结果")

    def _on_logout(self):
        from ui.login_window import LoginWindow
        self.next_window = LoginWindow()
        self.next_window.show()
        self.close()

    def _get_style(self):
        return """
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: "Microsoft YaHei";
            }
            #title {
                font-size: 22px;
                font-weight: bold;
                color: #5eead4;
            }
            #subtitle {
                font-size: 12px;
                color: #94a3b8;
            }
            #status {
                color: #5eead4;
                font-size: 12px;
            }
            #summary_group {
                border: 1px solid #334155;
                border-radius: 10px;
                padding-top: 10px;
            }
            #view_group {
                border: 1px solid #334155;
                border-radius: 10px;
                padding-top: 10px;
            }
            #tip {
                color: #cbd5e1;
                font-size: 12px;
            }
            QPushButton {
                background-color: #14b8a6;
                color: #04131a;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #94a3b8;
            }
        """

