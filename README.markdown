# Image Resizer Pro

---

## English

### Overview
**Image Resizer Pro** is a **professional-grade desktop application** for **high-quality image resizing**, built with **Python**, **PyQt6**, and **Pillow**. It offers **pixel-perfect control**, **advanced metadata preservation**, **batch processing**, and a **stunning multilingual interface** with **5 beautiful themes**.

Designed for photographers, designers, developers, and anyone who needs **fast, reliable, and visually consistent image scaling** — with full support for **EXIF, IPTC, XMP**, and **high-performance resampling**.

---

### Key Features
- **Ultra-Precise Resizing** using **Pillow + LANCZOS**
- **Aspect Ratio Lock** with real-time sync
- **Multiple Output Formats**:
  - JPEG (with quality control)
  - PNG (lossless)
  - WebP (modern & efficient)
- **Metadata Preservation** (EXIF, IPTC, XMP)
- **Live Preview** with original vs new size
- **Batch Processing** with queue management
- **Multilingual Interface**:
  - English, Persian (فارسی), Chinese (中文), Russian (Русский)
  - Full **RTL support** for Persian
- **5 Elegant Themes**:
  - Light, Dark, System, Red, Blue
- **Smart Settings Persistence**
- **Keyboard Shortcuts** & **Fullscreen Mode**
- **Detailed Execution Logs**
- **Modern UI** with shadows, gradients, and animations

---

### Requirements
- Python 3.8+
- PyQt6
- Pillow (`PIL`)
- qtawesome
- qdarkstyle

---

### Installation
1. Install dependencies:
   ```bash
   pip install PyQt6 Pillow qtawesome qdarkstyle
   ```
2. Save the script as `image_resizer_pro.py`
3. Run:
   ```bash
   python image_resizer_pro.py
   ```

---

### Usage
1. Click **"Browse"** to select an image
2. Choose **output folder** (optional)
3. Set **width/height** and enable **Keep Aspect Ratio**
4. Adjust **quality** and select **format**
5. Click **"Start Resizing"**
6. View **preview**, **logs**, and **statistics**
7. Use **Batch Processing** for multiple files

> Pro Tip: Enable **High Performance Mode** for 100+ MP images.

---

### Project Structure
- `image_resizer_pro.py` – Complete standalone application
- Settings saved in system registry/config
- Output: `*_resized.*` in selected folder

---

### Contributing
Contributions are welcome!  
You can:
- Add HEIC/AVIF support
- Implement drag & drop
- Add watermarking
- Support GPU acceleration
- Add cloud upload

Submit a **Pull Request** with detailed notes.

---

### License
Released under the **MIT License**. Free for personal and commercial use.

---

## فارسی

### نمای کلی
**تغییر اندازه حرفه‌ای تصویر** یک برنامه دسکتاپ **حرفه‌ای و قدرتمند** برای **تغییر اندازه تصاویر با کیفیت بالا** است که با **پایتون**، **PyQt6** و **Pillow** ساخته شده است. این ابزار کنترل **دقیق پیکسلی**، **حفظ متادیتا**، **پردازش دسته‌ای** و رابط کاربری **چندزبانه و زیبا** با **۵ تم خیره‌کننده** ارائه می‌دهد.

مناسب برای عکاسان، طراحان، توسعه‌دهندگان و هر کسی که نیاز به **تغییر اندازه سریع، قابل اعتماد و یکنواخت** دارد — با پشتیبانی کامل از **EXIF، IPTC، XMP** و **الگوریتم‌های پیشرفته**.

---

### ویژگی‌های کلیدی
- **تغییر اندازه فوق‌دقیق** با **LANCZOS**
- **قفل نسبت ابعاد** با همگام‌سازی لحظه‌ای
- **فرمت‌های خروجی متعدد**:
  - JPEG (با کنترل کیفیت)
  - PNG (بدون افت کیفیت)
  - WebP (مدرن و بهینه)
- **حفظ متادیتا** (EXIF، IPTC، XMP)
- **پیش‌نمایش زنده** با مقایسه اندازه
- **پردازش دسته‌ای** با مدیریت صف
- **رابط چندزبانه**:
  - فارسی، انگلیسی، چینی، روسی
  - پشتیبانی کامل از **راست‌به‌چپ**
- **۵ تم زیبا**:
  - روشن، تاریک، سیستم، قرمز، آبی
- **ذخیره هوشمند تنظیمات**
- **میانبرهای کیبورد** و **حالت تمام‌صفحه**
- **لاگ‌های دقیق اجرا**
- **رابط مدرن** با سایه، گرادیان و انیمیشن

---

### پیش‌نیازها
- پایتون ۳.۸ یا بالاتر
- PyQt6
- Pillow (`PIL`)
- qtawesome
- qdarkstyle

---

### نصب
1. نصب کتابخانه‌ها:
   ```bash
   pip install PyQt6 Pillow qtawesome qdarkstyle
   ```
2. فایل را با نام `image_resizer_pro.py` ذخیره کنید
3. اجرا:
   ```bash
   python image_resizer_pro.py
   ```

---

### نحوه استفاده
1. روی **«جستجو»** کلیک کنید و تصویر را انتخاب کنید
2. **پوشه خروجی** را انتخاب کنید (اختیاری)
3. **عرض/ارتفاع** را تنظیم کنید و **«حفظ نسبت ابعاد»** را فعال کنید
4. **کیفیت** و **فرمت** را انتخاب کنید
5. روی **«شروع تغییر اندازه»** کلیک کنید
6. **پیش‌نمایش**، **لاگ‌ها** و **آمار** را مشاهده کنید
7. برای چند فایل از **«پردازش دسته‌ای»** استفاده کنید

> نکته حرفه‌ای: برای تصاویر بالای ۱۰۰ مگاپیکسل، **حالت عملکرد بالا** را فعال کنید.

---

### ساختار پروژه
- `image_resizer_pro.py` – برنامه کامل و مستقل
- تنظیمات در رجیستری/فایل تنظیمات ذخیره می‌شود
- خروجی: `*_resized.*` در پوشه انتخابی

---

### مشارکت
مشارکت شما ارزشمند است!  
می‌توانید:
- پشتیبانی از HEIC/AVIF اضافه کنید
- کشیدن و رها کردن اضافه کنید
- واترمارک اضافه کنید
- شتاب‌دهی GPU اضافه کنید
- آپلود ابری اضافه کنید

درخواست کشش (Pull Request) با توضیحات کامل ارسال کنید.

---

### مجوز
تحت **مجوز MIT** منتشر شده است. آزاد برای استفاده شخصی و تجاری.

---

## 中文

### 项目概览
**专业图像缩放器** 是一款**专业级桌面应用程序**，用于**高质量图像缩放**，基于 **Python**、**PyQt6** 和 **Pillow** 构建。它提供**像素级精确控制**、**元数据保留**、**批量处理**以及**多语言华丽界面**，支持 **5 种精美主题**。

专为摄影师、设计师、开发者以及需要**快速、可靠、一致缩放**的用户设计 — 完全支持 **EXIF、IPTC、XMP** 和**高性能重采样**。

---

### 核心功能
- **超精准缩放**，采用 **LANCZOS 算法**
- **纵横比锁定**，实时同步
- **多种输出格式**：
  - JPEG（可控质量）
  - PNG（无损）
  - WebP（现代高效）
- **保留元数据**（EXIF、IPTC、XMP）
- **实时预览**，显示原始与新尺寸
- **批量处理**，带队列管理
- **多语言界面**：
  - 中文、英语、波斯语、俄语
  - 完整支持**从右到左 (RTL)**
- **5 种优雅主题**：
  - 亮色、暗色、系统、红色、蓝色
- **智能设置持久化**
- **键盘快捷键** & **全屏模式**
- **详细执行日志**
- **现代化界面**，带阴影、渐变和动画

---

### 系统要求
- Python 3.8+
- PyQt6
- Pillow (`PIL`)
- qtawesome
- qdarkstyle

---

### 安装步骤
1. 安装依赖：
   ```bash
   pip install PyQt6 Pillow qtawesome qdarkstyle
   ```
2. 将脚本保存为 `image_resizer_pro.py`
3. 运行：
   ```bash
   python image_resizer_pro.py
   ```

---

### 使用指南
1. 点击 **“浏览”** 选择图像
2. 选择 **输出文件夹**（可选）
3. 设置 **宽度/高度**，启用 **保持纵横比**
4. 调整 **质量** 并选择 **格式**
5. 点击 **“开始缩放”**
6. 查看 **预览**、**日志** 和 **统计**
7. 使用 **批量处理** 处理多个文件

> 专业提示：对 100+ MP 图像启用 **高性能模式**。

---

### 项目结构
- `image_resizer_pro.py` – 完整独立应用程序
- 设置保存在系统注册表/配置文件
- 输出：`*_resized.*` 在选中文件夹

---

### 贡献代码
我们欢迎贡献！您可以：
- 添加 HEIC/AVIF 支持
- 实现拖放功能
- 添加水印
- 支持 GPU 加速
- 添加云上传

请提交带有详细说明的 **Pull Request**。

---

### 许可证
基于 **MIT 许可证** 发布。个人和商业用途完全免费。