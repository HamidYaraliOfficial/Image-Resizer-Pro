import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QRadioButton, QButtonGroup, QProgressBar, QTextEdit, QFrame, QGridLayout,
    QTabWidget, QScrollArea, QFormLayout, QSplitter, QSpacerItem, QSizePolicy,
    QMessageBox, QInputDialog, QLineEdit, QMenuBar, QStatusBar, QListWidget,
    QListWidgetItem, QAbstractItemView, QToolTip, QDialog, QDialogButtonBox,
    QSlider, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTranslator, QLocale, pyqtSignal, QThread, QSettings, QSize,
    QDateTime, QTimer, QUrl, QRect,
    QSequentialAnimationGroup, QParallelAnimationGroup, QEvent, QPoint
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPalette, QColor, QFont, QPainter, QLinearGradient,
    QDesktopServices, QKeySequence, QShortcut, QBrush, QMovie,
    QValidator, QIntValidator, QClipboard, QCursor, QEnterEvent,
    QAction
)
from PIL import Image, ExifTags
import qdarkstyle
import qtawesome as qta
import datetime
import math


# Thread for image resizing
class ResizeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_path, output_path, width, height, keep_aspect, quality, format_type, preserve_meta):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.width = width
        self.height = height
        self.keep_aspect = keep_aspect
        self.quality = quality
        self.format_type = format_type
        self.preserve_meta = preserve_meta

    def run(self):
        try:
            img = Image.open(self.input_path)
            original_width, original_height = img.size

            if self.preserve_meta:
                exif_data = img.info.get('exif')
            else:
                exif_data = None

            if self.keep_aspect:
                ratio = min(self.width / original_width, self.height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                new_width, new_height = self.width, self.height

            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            save_kwargs = {}
            if self.format_type == 'JPEG':
                save_kwargs['quality'] = self.quality
                save_kwargs['optimize'] = True
                if exif_data and self.preserve_meta:
                    save_kwargs['exif'] = exif_data
            elif self.format_type == 'WEBP':
                save_kwargs['quality'] = self.quality
                save_kwargs['method'] = 6
            elif self.format_type == 'PNG':
                save_kwargs['optimize'] = True

            resized.save(self.output_path, **save_kwargs)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


# Batch Processing Dialog
class BatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(parent.tr("Batch Processing"))
        self.setMinimumSize(700, 500)
        self.parent = parent
        self.queue = []

        layout = QVBoxLayout(self)

        # Header
        header = QLabel(parent.tr("Batch Processing"))
        header.setStyleSheet("font-size: 18pt; font-weight: bold; color: #0078D4; padding: 12px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # File list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(parent.tr("Select Multiple Images"))
        add_btn.setIcon(qta.icon('fa5s.images'))
        add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_btn)

        clear_btn = QPushButton(parent.tr("Clear Queue"))
        clear_btn.setIcon(qta.icon('fa5s.trash'))
        clear_btn.clicked.connect(self.clear_queue)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        # Progress
        self.batch_progress = QProgressBar()
        self.batch_progress.setVisible(False)
        layout.addWidget(self.batch_progress)

        # Start button
        self.start_batch_btn = QPushButton(parent.tr("Start Batch"))
        self.start_batch_btn.setIcon(qta.icon('fa5s.play-circle'))
        self.start_batch_btn.clicked.connect(self.start_batch)
        self.start_batch_btn.setStyleSheet(parent.create_action_button("", "", None, "").styleSheet())
        layout.addWidget(self.start_batch_btn)

        # Close
        close_btn = QPushButton(parent.tr("Close"))
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, self.parent.tr("Select Multiple Images"),
            "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.gif)"
        )
        for path in paths:
            if path not in self.queue:
                self.queue.append(path)
                item = QListWidgetItem(os.path.basename(path))
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.list_widget.addItem(item)

    def clear_queue(self):
        self.queue.clear()
        self.list_widget.clear()

    def start_batch(self):
        if not self.queue:
            QMessageBox.warning(self, "Warning", self.parent.tr("Queue is empty!"))
            return

        self.start_batch_btn.setEnabled(False)
        self.batch_progress.setVisible(True)
        self.batch_progress.setMaximum(len(self.queue))
        self.current_index = 0
        self.process_next()

    def process_next(self):
        if self.current_index >= len(self.queue):
            self.batch_progress.setValue(self.batch_progress.maximum())
            QMessageBox.information(self, "Success", self.parent.tr("Batch completed!"))
            self.start_batch_btn.setEnabled(True)
            self.batch_progress.setVisible(False)
            return

        path = self.queue[self.current_index]
        output_folder = self.parent.output_folder or os.path.dirname(path)
        base_name = os.path.splitext(os.path.basename(path))[0]
        ext = self.parent.format_combo.currentText().split()[-1].lower()
        if ext == 'jpeg': ext = 'jpg'
        output_path = os.path.join(output_folder, f"{base_name}_resized.{ext}")

        worker = ResizeWorker(
            path, output_path,
            self.parent.width_spin.value(), self.parent.height_spin.value(),
            self.parent.aspect_check.isChecked(), self.parent.quality_spin.value(),
            self.parent.format_combo.currentText().split()[-1], self.parent.meta_check.isChecked()
        )
        worker.finished.connect(lambda p: self.on_batch_item_done(p, True))
        worker.error.connect(lambda e: self.on_batch_item_done(e, False))
        worker.start()

        self.batch_progress.setValue(self.current_index)
        self.current_index += 1

    def on_batch_item_done(self, result, success):
        if success:
            self.parent.log(f"Batch: {os.path.basename(result)}")
        else:
            self.parent.log(f"Batch Error: {result}")
        self.process_next()


# Main Application Window
class ImageResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translators = {}
        self.current_lang = 'en'
        self.input_path = None
        self.output_folder = None
        self.original_ratio = 1.0
        self.settings = QSettings("ImageResizerPro", "Settings")
        self.worker = None
        self.batch_dialog = None

        # Initialize
        self.init_translations()
        self.init_ui()
        self.load_settings()  # Must come after init_ui() because it uses self.theme_group
        self.apply_theme()
        self.setup_shortcuts()

    def init_translations(self):
        # English
        self.translators['en'] = {}

        # Persian
        self.translators['fa'] = {
            "Image Resizer Pro": "تغییر اندازه حرفه‌ای تصویر",
            "Select Image": "انتخاب تصویر",
            "Output Folder": "پوشه خروجی",
            "Browse": "جستجو",
            "Width": "عرض",
            "Height": "ارتفاع",
            "Keep Aspect Ratio": "حفظ نسبت ابعاد",
            "Quality (1-100)": "کیفیت (۱-۱۰۰)",
            "Start Resizing": "شروع تغییر اندازه",
            "Theme": "تم",
            "Language": "زبان",
            "Light": "روشن",
            "Dark": "تیره",
            "System": "سیستم",
            "Red": "قرمز",
            "Blue": "آبی",
            "English": "English",
            "Persian": "فارسی",
            "Chinese": "中文",
            "Russian": "Русский",
            "Processing...": "در حال پردازش...",
            "Success! Saved to:": "موفقیت! ذخیره شد در:",
            "Error:": "خطا:",
            "Select input image first!": "ابتدا تصویر ورودی را انتخاب کنید!",
            "Preview": "پیش‌نمایش",
            "Original Size:": "اندازه اصلی:",
            "New Size:": "اندازه جدید:",
            "About": "درباره",
            "Help": "راهنما",
            "Settings": "تنظیمات",
            "Logs": "لاگ‌ها",
            "Reset": "بازنشانی",
            "Advanced": "پیشرفته",
            "Format": "فرمت",
            "JPEG": "JPEG",
            "PNG": "PNG",
            "WEBP": "WEBP",
            "Preserve Metadata": "حفظ متادیتا",
            "High Performance Mode": "حالت عملکرد بالا",
            "Open Output Folder": "باز کردن پوشه خروجی",
            "Copy to Clipboard": "کپی در کلیپ‌بورد",
            "Save As...": "ذخیره با نام...",
            "Exit": "خروج",
            "File": "فایل",
            "Edit": "ویرایش",
            "View": "نمایش",
            "Tools": "ابزارها",
            "No file selected": "فایلی انتخاب نشده",
            "Same as input": "همانند ورودی",
            "Preview will appear here": "پیش‌نمایش اینجا نمایش داده می‌شود",
            "Loading...": "در حال بارگذاری...",
            "Version": "نسخه",
            "Professional image resizing tool with multilingual support.": "ابزار حرفه‌ای تغییر اندازه تصویر با پشتیبانی چندزبانه.",
            "All rights reserved.": "تمامی حقوق محفوظ است.",
            "Open image in default viewer": "باز کردن تصویر در نمایشگر پیش‌فرض",
            "Reset all settings": "بازنشانی تمام تنظیمات",
            "Auto": "خودکار",
            "Percentage": "درصد",
            "Scale by percentage": "تغییر اندازه بر اساس درصد",
            "Batch Processing": "پردازش دسته‌ای",
            "Select Multiple Images": "انتخاب چندین تصویر",
            "Queue": "صف",
            "Clear Queue": "پاک کردن صف",
            "Start Batch": "شروع پردازش دسته‌ای",
            "Processing {0} of {1}": "در حال پردازش {0} از {1}",
            "Batch completed!": "پردازش دسته‌ای کامل شد!",
            "Queue is empty!": "صف خالی است!",
            "Ready": "آماده",
            "Input": "ورودی",
            "Output": "خروجی",
            "Quality": "کیفیت",
            "Close": "بستن",
            "Warning": "هشدار",
        }

        # Chinese
        self.translators['zh'] = {
            "Image Resizer Pro": "专业图像缩放器",
            "Select Image": "选择图像",
            "Output Folder": "输出文件夹",
            "Browse": "浏览",
            "Width": "宽度",
            "Height": "高度",
            "Keep Aspect Ratio": "保持纵横比",
            "Quality (1-100)": "质量 (1-100)",
            "Start Resizing": "开始缩放",
            "Theme": "主题",
            "Language": "语言",
            "Light": "亮色",
            "Dark": "暗色",
            "System": "系统",
            "Red": "红色",
            "Blue": "蓝色",
            "English": "English",
            "Persian": "فارسی",
            "Chinese": "中文",
            "Russian": "Русский",
            "Processing...": "处理中...",
            "Success! Saved to:": "成功！已保存至：",
            "Error:": "错误：",
            "Select input image first!": "请先选择输入图像！",
            "Preview": "预览",
            "Original Size:": "原始尺寸：",
            "New Size:": "新尺寸：",
            "About": "关于",
            "Help": "帮助",
            "Settings": "设置",
            "Logs": "日志",
            "Reset": "重置",
            "Advanced": "高级",
            "Format": "格式",
            "JPEG": "JPEG",
            "PNG": "PNG",
            "WEBP": "WEBP",
            "Preserve Metadata": "保留元数据",
            "High Performance Mode": "高性能模式",
            "Open Output Folder": "打开输出文件夹",
            "Copy to Clipboard": "复制到剪贴板",
            "Save As...": "另存为...",
            "Exit": "退出",
            "File": "文件",
            "Edit": "编辑",
            "View": "查看",
            "Tools": "工具",
            "No file selected": "未选择文件",
            "Same as input": "与输入相同",
            "Preview will appear here": "预览将显示在这里",
            "Loading...": "加载中...",
            "Version": "版本",
            "Professional image resizing tool with multilingual support.": "专业图像缩放工具，支持多语言。",
            "All rights reserved.": "版权所有。",
            "Open image in default viewer": "在默认查看器中打开图像",
            "Reset all settings": "重置所有设置",
            "Auto": "自动",
            "Percentage": "百分比",
            "Scale by percentage": "按百分比缩放",
            "Batch Processing": "批量处理",
            "Select Multiple Images": "选择多个图像",
            "Queue": "队列",
            "Clear Queue": "清除队列",
            "Start Batch": "开始批量处理",
            "Processing {0} of {1}": "正在处理 {0}/{1}",
            "Batch completed!": "批量处理完成！",
            "Queue is empty!": "队列为空！",
            "Ready": "就绪",
            "Input": "输入",
            "Output": "输出",
            "Quality": "质量",
            "Close": "关闭",
            "Warning": "警告",
        }

        # Russian
        self.translators['ru'] = {
            "Image Resizer Pro": "Профессиональный ресайзер изображений",
            "Select Image": "Выбрать изображение",
            "Output Folder": "Папка вывода",
            "Browse": "Обзор",
            "Width": "Ширина",
            "Height": "Высота",
            "Keep Aspect Ratio": "Сохранить пропорции",
            "Quality (1-100)": "Качество (1-100)",
            "Start Resizing": "Начать изменение размера",
            "Theme": "Тема",
            "Language": "Язык",
            "Light": "Светлая",
            "Dark": "Тёмная",
            "System": "Системная",
            "Red": "Красная",
            "Blue": "Синяя",
            "English": "English",
            "Persian": "فارسی",
            "Chinese": "中文",
            "Russian": "Русский",
            "Processing...": "Обработка...",
            "Success! Saved to:": "Успех! Сохранено в:",
            "Error:": "Ошибка:",
            "Select input image first!": "Сначала выберите входное изображение!",
            "Preview": "Предпросмотр",
            "Original Size:": "Исходный размер:",
            "New Size:": "Новый размер:",
            "About": "О программе",
            "Help": "Помощь",
            "Settings": "Настройки",
            "Logs": "Логи",
            "Reset": "Сброс",
            "Advanced": "Расширенные",
            "Format": "Формат",
            "JPEG": "JPEG",
            "PNG": "PNG",
            "WEBP": "WEBP",
            "Preserve Metadata": "Сохранить метаданные",
            "High Performance Mode": "Режим высокой производительности",
            "Open Output Folder": "Открыть папку вывода",
            "Copy to Clipboard": "Копировать в буфер",
            "Save As...": "Сохранить как...",
            "Exit": "Выход",
            "File": "Файл",
            "Edit": "Правка",
            "View": "Вид",
            "Tools": "Инструменты",
            "No file selected": "Файл не выбран",
            "Same as input": "Как входной",
            "Preview will appear here": "Предпросмотр появится здесь",
            "Loading...": "Загрузка...",
            "Version": "Версия",
            "Professional image resizing tool with multilingual support.": "Профессиональный инструмент изменения размера изображений с поддержкой нескольких языков.",
            "All rights reserved.": "Все права защищены.",
            "Open image in default viewer": "Открыть изображение в просмотрщике по умолчанию",
            "Reset all settings": "Сбросить все настройки",
            "Auto": "Авто",
            "Percentage": "Процент",
            "Scale by percentage": "Масштабировать по проценту",
            "Batch Processing": "Пакетная обработка",
            "Select Multiple Images": "Выбрать несколько изображений",
            "Queue": "Очередь",
            "Clear Queue": "Очистить очередь",
            "Start Batch": "Начать пакетную обработку",
            "Processing {0} of {1}": "Обработка {0} из {1}",
            "Batch completed!": "Пакетная обработка завершена!",
            "Queue is empty!": "Очередь пуста!",
            "Ready": "Готово",
            "Input": "Вход",
            "Output": "Выход",
            "Quality": "Качество",
            "Close": "Закрыть",
            "Warning": "Предупреждение",
        }

    def tr(self, text):
        if self.current_lang == 'en':
            return text
        return self.translators.get(self.current_lang, {}).get(text, text)

    def init_ui(self):
        self.setWindowTitle(self.tr("Image Resizer Pro"))
        self.setWindowIcon(qta.icon('fa5s.images', color='#0078D4'))
        self.resize(1300, 850)
        self.setMinimumSize(1100, 700)

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(self.tr("Ready"))

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(28)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left Panel
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setMinimumWidth(420)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)

        # Header
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0078D4, stop:1 #106EBE); border-radius: 16px; padding: 16px;")
        header_layout = QHBoxLayout(self.header_frame)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.images', color='white').pixmap(56, 56))
        header_layout.addWidget(icon_label)

        self.title_label = QLabel(self.tr("Image Resizer Pro"))
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white;")
        header_layout.addWidget(self.title_label, 1)
        header_layout.addStretch()
        left_layout.addWidget(self.header_frame)

        # Input Group
        input_group = self.create_group(self.tr("Select Image"))
        input_layout = QFormLayout(input_group)
        input_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.input_path_label = QLabel(self.tr("No file selected"))
        self.input_path_label.setWordWrap(True)
        self.input_path_label.setStyleSheet(self.label_style())
        self.input_path_label.setProperty("original_text", self.tr("No file selected"))

        input_btn = self.create_button(self.tr("Browse"), 'fa5s.folder-open', self.select_input)
        input_hbox = QHBoxLayout()
        input_hbox.addWidget(self.input_path_label, 1)
        input_hbox.addWidget(input_btn)
        input_layout.addRow(self.tr("Input") + ":", input_hbox)

        # Output
        self.output_path_label = QLabel(self.tr("Same as input"))
        self.output_path_label.setWordWrap(True)
        self.output_path_label.setStyleSheet(self.label_style())
        self.output_path_label.setProperty("original_text", self.tr("Same as input"))

        output_btn = self.create_button(self.tr("Browse"), 'fa5s.folder', self.select_output)
        output_hbox = QHBoxLayout()
        output_hbox.addWidget(self.output_path_label, 1)
        output_hbox.addWidget(output_btn)
        input_layout.addRow(self.tr("Output Folder") + ":", output_hbox)

        left_layout.addWidget(input_group)

        # Dimensions Group
        dim_group = self.create_group(self.tr("Width") + " × " + self.tr("Height"))
        dim_layout = QGridLayout(dim_group)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20000)
        self.width_spin.setValue(1280)
        self.width_spin.setSuffix(" px")
        self.width_spin.setStyleSheet(self.spin_style())
        self.width_spin.setToolTip(self.tr("Width in pixels"))

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 20000)
        self.height_spin.setValue(720)
        self.height_spin.setSuffix(" px")
        self.height_spin.setStyleSheet(self.spin_style())
        self.height_spin.setToolTip(self.tr("Height in pixels"))

        self.aspect_check = QCheckBox(self.tr("Keep Aspect Ratio"))
        self.aspect_check.setChecked(True)
        self.aspect_check.stateChanged.connect(self.toggle_aspect)
        self.aspect_check.setToolTip(self.tr("Maintain original aspect ratio"))

        dim_layout.addWidget(QLabel(self.tr("Width") + ":"), 0, 0)
        dim_layout.addWidget(self.width_spin, 0, 1)
        dim_layout.addWidget(QLabel(self.tr("Height") + ":"), 1, 0)
        dim_layout.addWidget(self.height_spin, 1, 1)
        dim_layout.addWidget(self.aspect_check, 2, 0, 1, 2)

        left_layout.addWidget(dim_group)

        # Quality & Format
        quality_format = QHBoxLayout()
        quality_group = self.create_group(self.tr("Quality (1-100)"))
        q_layout = QFormLayout(quality_group)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setStyleSheet(self.spin_style())
        self.quality_spin.setToolTip(self.tr("Image quality (higher = better)"))
        q_layout.addRow(self.tr("Quality") + ":", self.quality_spin)
        quality_format.addWidget(quality_group)

        format_group = self.create_group(self.tr("Format"))
        f_layout = QHBoxLayout(format_group)
        self.format_combo = QComboBox()
        self.format_combo.addItems([self.tr("JPEG"), self.tr("PNG"), self.tr("WEBP")])
        self.format_combo.setStyleSheet(self.combo_style())
        self.format_combo.setToolTip(self.tr("Output image format"))
        f_layout.addWidget(self.format_combo)
        quality_format.addWidget(format_group)

        left_layout.addLayout(quality_format)

        # Advanced Options
        adv_group = self.create_group(self.tr("Advanced"))
        adv_layout = QVBoxLayout(adv_group)
        self.meta_check = QCheckBox(self.tr("Preserve Metadata"))
        self.meta_check.setChecked(True)
        self.meta_check.setToolTip(self.tr("Keep EXIF, IPTC, XMP data"))
        self.perf_check = QCheckBox(self.tr("High Performance Mode"))
        self.perf_check.setToolTip(self.tr("Use faster but lower quality resampling"))
        adv_layout.addWidget(self.meta_check)
        adv_layout.addWidget(self.perf_check)
        left_layout.addWidget(adv_group)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(self.progress_style())
        left_layout.addWidget(self.progress)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = self.create_action_button(
            self.tr("Start Resizing"), 'fa5s.magic', self.start_resize,
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0078D4, stop:1 #106EBE); color: white; font-weight: bold;"
        )
        btn_layout.addWidget(self.start_btn)

        self.open_btn = self.create_action_button(
            self.tr("Open Output Folder"), 'fa5s.folder-open', self.open_output_folder,
            "background: #28A745; color: white;"
        )
        self.open_btn.setEnabled(False)
        btn_layout.addWidget(self.open_btn)

        left_layout.addLayout(btn_layout)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #0078D4; font-style: italic; padding: 10px; background: #E3F2FD; border-radius: 8px;")
        left_layout.addWidget(self.status_label)

        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Right Panel - Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setStyleSheet("QTabBar::tab { height: 40px; padding: 0 20px; font-weight: bold; }")

        # Preview Tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(550, 380)
        self.preview_label.setStyleSheet("background: #F8F9FA; border: 3px dashed #DEE2E6; border-radius: 20px; font-size: 16pt; color: #6C757D;")
        self.preview_label.setText(self.tr("Preview will appear here"))
        preview_layout.addWidget(self.preview_label, 1)

        # Info
        info_frame = QFrame()
        info_layout = QFormLayout(info_frame)
        info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.orig_size_label = QLabel(self.tr("Original Size:") + " -")
        self.new_size_label = QLabel(self.tr("New Size:") + " -")
        info_layout.addRow(self.tr("Original Size:"), self.orig_size_label)
        info_layout.addRow(self.tr("New Size:"), self.new_size_label)
        preview_layout.addWidget(info_frame)

        self.tabs.addTab(preview_tab, qta.icon('fa5s.eye', color='#0078D4'), self.tr("Preview"))

        # Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: Consolas; font-size: 10pt; background: #1E1E1E; color: #D4D4D4; border-radius: 12px;")
        logs_layout.addWidget(self.log_text)
        self.tabs.addTab(logs_tab, qta.icon('fa5s.file-alt', color='#6C757D'), self.tr("Logs"))

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        settings_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Language
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.tr("Language") + ":")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([self.tr("English"), self.tr("Persian"), self.tr("Chinese"), self.tr("Russian")])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo, 1)
        settings_layout.addRow(lang_layout)

        # Theme
        theme_layout = QHBoxLayout()
        theme_label = QLabel(self.tr("Theme") + ":")
        self.theme_group = QButtonGroup()
        themes = [self.tr("Light"), self.tr("Dark"), self.tr("System"), self.tr("Red"), self.tr("Blue")]
        for i, name in enumerate(themes):
            rb = QRadioButton(name)
            rb.setToolTip(f"{name} theme")
            self.theme_group.addButton(rb, i)
        self.theme_group.buttonClicked.connect(self.change_theme)
        theme_hbox = QHBoxLayout()
        for btn in self.theme_group.buttons():
            theme_hbox.addWidget(btn)
        theme_layout.addWidget(theme_label)
        theme_layout.addLayout(theme_hbox)
        settings_layout.addRow(theme_layout)

        self.tabs.addTab(settings_tab, qta.icon('fa5s.cog', color='#6C757D'), self.tr("Settings"))

        # Help Tab
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_browser = QTextEdit()
        help_browser.setHtml(self.get_help_text())
        help_browser.setReadOnly(True)
        help_browser.setStyleSheet("background: #F8F9FA; border: none; border-radius: 12px;")
        help_layout.addWidget(help_browser)
        self.tabs.addTab(help_tab, qta.icon('fa5s.question-circle', color='#17A2B8'), self.tr("Help"))

        splitter.addWidget(left_panel)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        # Menu Bar
        self.create_menus()

        # Add shadow effects
        self.add_shadow(self.header_frame)
        self.add_shadow(input_group)
        self.add_shadow(dim_group)
        self.add_shadow(quality_group)
        self.add_shadow(format_group)
        self.add_shadow(adv_group)

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)

    def create_group(self, title):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #CED4DA;
                border-radius: 16px;
                margin-top: 16px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                top: -12px;
                color: #495057;
                background: white;
                padding: 0 12px;
                font-size: 11pt;
            }
        """)
        return group

    def create_button(self, text, icon_name, callback):
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color='#495057'))
        btn.clicked.connect(callback)
        btn.setStyleSheet(self.button_style())
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def create_action_button(self, text, icon_name, callback, extra_style=""):
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color='white'))
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                {extra_style}
                border-radius: 16px;
                padding: 14px 24px;
                font-weight: bold;
                font-size: 12pt;
                min-height: 40px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
            QPushButton:pressed {{ padding-top: 16px; padding-bottom: 12px; }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def label_style(self):
        return "color: #212529; padding: 10px; background: #E9ECEF; border-radius: 10px; font-family: Segoe UI; font-size: 10pt;"

    def spin_style(self):
        return """
        QSpinBox { 
            padding: 8px; 
            border: 2px solid #CED4DA; 
            border-radius: 10px; 
            font-size: 11pt;
        }
        QSpinBox:focus { border-color: #0078D4; }
        """

    def combo_style(self):
        return """
        QComboBox { 
            padding: 8px; 
            border: 2px solid #CED4DA; 
            border-radius: 10px; 
            font-size: 11pt;
        }
        QComboBox:focus { border-color: #0078D4; }
        """

    def button_style(self):
        return """
            QPushButton {
                background: #F8F9FA;
                border: 2px solid #CED4DA;
                border-radius: 12px;
                padding: 12px;
                font-weight: 600;
                font-size: 11pt;
            }
            QPushButton:hover {
                background: #E9ECEF;
                border-color: #ADB5BD;
            }
            QPushButton:pressed {
                background: #DEE2E6;
            }
        """

    def progress_style(self):
        return """
            QProgressBar {
                border: 2px solid #CED4DA;
                border-radius: 12px;
                text-align: center;
                font-weight: bold;
                font-size: 11pt;
                height: 28px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078D4, stop:1 #17A2B8);
                border-radius: 10px;
            }
        """

    def create_menus(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu(self.tr("File"))
        action = QAction(qta.icon('fa5s.folder-open'), self.tr("Select Image"), self)
        action.triggered.connect(self.select_input)
        action.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(action)

        action = QAction(qta.icon('fa5s.save'), self.tr("Output Folder"), self)
        action.triggered.connect(self.select_output)
        file_menu.addAction(action)

        file_menu.addSeparator()

        action = QAction(qta.icon('fa5s.sign-out-alt'), self.tr("Exit"), self)
        action.triggered.connect(self.close)
        action.setShortcut(QKeySequence("Ctrl+Q"))
        file_menu.addAction(action)

        # Edit Menu
        edit_menu = menubar.addMenu(self.tr("Edit"))
        action = QAction(qta.icon('fa5s.redo'), self.tr("Reset all settings"), self)
        action.triggered.connect(self.reset_settings)
        edit_menu.addAction(action)

        # View Menu
        view_menu = menubar.addMenu(self.tr("View"))
        action = QAction(qta.icon('fa5s.expand'), "Fullscreen", self)
        action.triggered.connect(self.toggle_fullscreen)
        action.setShortcut(QKeySequence("F11"))
        view_menu.addAction(action)

        # Tools Menu
        tools_menu = menubar.addMenu(self.tr("Tools"))
        action = QAction(qta.icon('fa5s.images'), self.tr("Batch Processing"), self)
        action.triggered.connect(self.open_batch_dialog)
        tools_menu.addAction(action)

        # Help Menu
        help_menu = menubar.addMenu(self.tr("Help"))
        action = QAction(qta.icon('fa5s.info-circle'), self.tr("About"), self)
        action.triggered.connect(self.show_about)
        help_menu.addAction(action)

        # Use 'mdi.github' instead of 'fa5s.github'
        try:
            action = QAction(qta.icon('mdi.github'), "GitHub", self)
        except:
            action = QAction("GitHub", self)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com")))
        help_menu.addAction(action)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.start_resize)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_preview)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self.open_batch_dialog)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def refresh_preview(self):
        if hasattr(self, 'input_path') and self.input_path:
            self.load_preview(self.input_path)

    def get_help_text(self):
        return f"""
        <div style='padding: 20px; font-family: Segoe UI;'>
        <h2 style='color: #0078D4;'>{self.tr("Help")}</h2>
        <p><b>1.</b> {self.tr("Select Image")} → {self.tr("Browse")} و تصویر خود را انتخاب کنید.</p>
        <p><b>2.</b> {self.tr("Output Folder")} → محل ذخیره تصویر تغییر اندازه یافته.</p>
        <p><b>3.</b> {self.tr("Width")} و {self.tr("Height")} → ابعاد دلخواه.</p>
        <p><b>4.</b> {self.tr("Keep Aspect Ratio")} → نسبت ابعاد حفظ شود.</p>
        <p><b>5.</b> {self.tr("Start Resizing")} → شروع فرآیند.</p>
        <hr>
        <p><b>{self.tr("Advanced")}:</b></p>
        <ul>
            <li>{self.tr("Preserve Metadata")}: اطلاعات EXIF حفظ شود.</li>
            <li>{self.tr("High Performance Mode")}: برای تصاویر بزرگ.</li>
        </ul>
        <p style='color: #6C757D;'><i>{self.tr("Version")} 3.0.0 - Professional Edition</i></p>
        </div>
        """

    def update_direction(self):
        direction = Qt.LayoutDirection.RightToLeft if self.current_lang in ['fa'] else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)
        QApplication.instance().setLayoutDirection(direction)

    def toggle_aspect(self, state):
        if state == Qt.CheckState.Checked:
            self.width_spin.valueChanged.connect(self.update_height)
            self.height_spin.valueChanged.connect(self.update_width)
            if hasattr(self, 'original_ratio'):
                self.update_height()
        else:
            try:
                self.width_spin.valueChanged.disconnect()
                self.height_spin.valueChanged.disconnect()
            except:
                pass

    def update_height(self):
        if self.aspect_check.isChecked() and hasattr(self, 'original_ratio'):
            w = self.width_spin.value()
            h = max(1, int(w / self.original_ratio))
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(h)
            self.height_spin.blockSignals(False)
            self.update_new_size()

    def update_width(self):
        if self.aspect_check.isChecked() and hasattr(self, 'original_ratio'):
            h = self.height_spin.value()
            w = max(1, int(h * self.original_ratio))
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(w)
            self.width_spin.blockSignals(False)
            self.update_new_size()

    def update_new_size(self):
        self.new_size_label.setText(f"{self.width_spin.value()} × {self.height_spin.value()}")

    def select_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select Image"),
            "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.gif)"
        )
        if path:
            self.input_path = path
            self.input_path_label.setText(os.path.basename(path))
            self.load_preview(path)
            self.log(f"Input: {path}")

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, self.tr("Output Folder"))
        if path:
            self.output_folder = path
            self.output_path_label.setText(path)
            self.log(f"Output: {path}")

    def load_preview(self, path):
        try:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                raise Exception("Invalid image")
            scaled = pixmap.scaled(550, 380, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled)

            img = Image.open(path)
            w, h = img.size
            self.orig_size_label.setText(f"{w} × {h}")
            self.original_ratio = w / h if h > 0 else 1.0
            self.update_new_size()
            self.log(f"Preview: {w}×{h}")
        except Exception as e:
            self.preview_label.setText(self.tr("Loading..."))
            self.log(f"Preview error: {e}")

    def start_resize(self):
        if not self.input_path:
            self.status_label.setText(self.tr("Select input image first!"))
            return

        output_folder = self.output_folder or os.path.dirname(self.input_path)
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        ext_map = {self.tr("JPEG"): "jpg", self.tr("PNG"): "png", self.tr("WEBP"): "webp"}
        ext = ext_map.get(self.format_combo.currentText(), "jpg")
        output_path = os.path.join(output_folder, f"{base_name}_resized.{ext}")

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.start_btn.setEnabled(False)
        self.status_label.setText(self.tr("Processing..."))
        self.statusBar.showMessage(self.tr("Processing..."))

        format_type = self.format_combo.currentText().split()[-1]
        self.worker = ResizeWorker(
            self.input_path, output_path,
            self.width_spin.value(), self.height_spin.value(),
            self.aspect_check.isChecked(), self.quality_spin.value(),
            format_type, self.meta_check.isChecked()
        )
        self.worker.finished.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_success(self, path):
        self.progress.setVisible(False)
        self.start_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.status_label.setText(self.tr("Success! Saved to:") + f" {os.path.basename(path)}")
        self.statusBar.showMessage(self.tr("Success! Saved to:") + f" {os.path.basename(path)}", 6000)
        self.log(f"Success: {path}")

    def on_error(self, msg):
        self.progress.setVisible(False)
        self.start_btn.setEnabled(True)
        self.status_label.setText(self.tr("Error:") + f" {msg}")
        self.statusBar.showMessage(self.tr("Error:") + f" {msg}", 10000)
        self.log(f"Error: {msg}")

    def open_output_folder(self):
        if self.output_folder:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_folder))

    def log(self, msg):
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.log_text.append(f"[{timestamp}] {msg}")

    def change_language(self, index):
        langs = ['en', 'fa', 'zh', 'ru']
        self.current_lang = langs[index]
        self.retranslate_ui()
        self.update_direction()
        self.save_settings()

    def change_theme(self, button):
        themes = ['light', 'dark', 'system', 'red', 'blue']
        theme = themes[self.theme_group.id(button)]
        self.settings.setValue("theme", theme)
        self.apply_theme()

    def apply_theme(self):
        theme = self.settings.value("theme", "system")
        app = QApplication.instance()

        if theme == "dark":
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
        elif theme == "light":
            app.setStyleSheet("")
        elif theme == "red":
            app.setStyleSheet(self.red_theme())
        elif theme == "blue":
            app.setStyleSheet(self.blue_theme())
        else:
            app.setStyleSheet("")

        # Force text color
        forced = "\nQLabel, QPushButton, QComboBox, QSpinBox, QGroupBox, QTextEdit { color: #212529; }"
        if theme == "dark":
            forced = "\nQLabel, QPushButton, QComboBox, QSpinBox, QGroupBox, QTextEdit { color: #E9ECEF; }"
        app.setStyleSheet(app.styleSheet() + forced)

    def red_theme(self):
        return """
        QWidget { background-color: #FFF5F5; }
        QGroupBox { border: 2px solid #FFA0A0; background: #FFEBEE; }
        QGroupBox::title { color: #C21807; }
        QPushButton { background: #FFEBEE; border: 2px solid #FF8A80; color: #B71C1C; }
        QTextEdit { background: #1E1E1E; color: #FFB3B3; }
        """

    def blue_theme(self):
        return """
        QWidget { background-color: #F0F8FF; }
        QGroupBox { border: 2px solid #87CEFA; background: #E3F2FD; }
        QGroupBox::title { color: #1E90FF; }
        QPushButton { background: #E3F2FD; border: 2px solid #64B5F6; color: #1565C0; }
        QTextEdit { background: #1E1E1E; color: #87CEFA; }
        """

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Image Resizer Pro"))
        self.statusBar.showMessage(self.tr("Ready"))

        # Retranslate all widgets
        for widget in self.findChildren((QLabel, QPushButton, QGroupBox, QCheckBox, QRadioButton, QMenu, QTabWidget)):
            if hasattr(widget, "setText") and widget.text():
                original = widget.property("original_text")
                if not original:
                    original = widget.text()
                    widget.setProperty("original_text", original)
                widget.setText(self.tr(original))

        # Update combo boxes
        current_format = self.format_combo.currentText()
        self.format_combo.clear()
        self.format_combo.addItems([self.tr("JPEG"), self.tr("PNG"), self.tr("WEBP")])
        idx = [self.tr("JPEG"), self.tr("PNG"), self.tr("WEBP")].index(current_format) if current_format in [self.tr("JPEG"), self.tr("PNG"), self.tr("WEBP")] else 0
        self.format_combo.setCurrentIndex(idx)

        # Update menus
        self.create_menus()

        # Update help
        self.tabs.widget(3).layout().itemAt(0).widget().setHtml(self.get_help_text())

    def save_settings(self):
        self.settings.setValue("language", self.current_lang)
        self.settings.setValue("width", self.width_spin.value())
        self.settings.setValue("height", self.height_spin.value())
        self.settings.setValue("quality", self.quality_spin.value())
        self.settings.setValue("keep_aspect", self.aspect_check.isChecked())
        self.settings.setValue("preserve_meta", self.meta_check.isChecked())
        self.settings.setValue("format", self.format_combo.currentIndex())
        self.settings.setValue("theme", self.settings.value("theme", "system"))

    def load_settings(self):
        # Language
        lang = self.settings.value("language", "en")
        idx = ['en', 'fa', 'zh', 'ru'].index(lang) if lang in ['en', 'fa', 'zh', 'ru'] else 0
        self.lang_combo.setCurrentIndex(idx)
        self.current_lang = ['en', 'fa', 'zh', 'ru'][idx]

        # Dimensions
        self.width_spin.setValue(int(self.settings.value("width", 1280)))
        self.height_spin.setValue(int(self.settings.value("height", 720)))
        self.quality_spin.setValue(int(self.settings.value("quality", 95)))
        self.aspect_check.setChecked(self.settings.value("keep_aspect", True) in [True, "true"])
        self.meta_check.setChecked(self.settings.value("preserve_meta", True) in [True, "true"])
        self.format_combo.setCurrentIndex(int(self.settings.value("format", 0)))

        # Theme - SAFE CHECK
        theme = self.settings.value("theme", "system")
        theme_idx = ['light', 'dark', 'system', 'red', 'blue'].index(theme) if theme in ['light', 'dark', 'system', 'red', 'blue'] else 2
        if self.theme_group.button(theme_idx):  # Check if button exists
            self.theme_group.button(theme_idx).setChecked(True)

    def reset_settings(self):
        if QMessageBox.question(self, "Reset", "Reset all settings to default?") == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            self.apply_theme()
            QMessageBox.information(self, "Reset", "Settings have been reset.")

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.tr("About"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"""
        <h2 style='color: #0078D4;'>{self.tr('Image Resizer Pro')}</h2>
        <p><b>{self.tr('Version')}</b> 3.0.0</p>
        <p>{self.tr('Professional image resizing tool with multilingual support.')}</p>
        <p>© 2025 {self.tr('All rights reserved.')}</p>
        """)
        msg.exec()

    def open_batch_dialog(self):
        if not self.batch_dialog:
            self.batch_dialog = BatchDialog(self)
        self.batch_dialog.show()
        self.batch_dialog.raise_()
        self.batch_dialog.activateWindow()

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)


# Run Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Image Resizer Pro")
    app.setOrganizationName("ProTools")
    app.setStyle("Fusion")

    window = ImageResizerApp()
    window.show()
    sys.exit(app.exec())