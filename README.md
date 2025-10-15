# AI Document Generator (Công cụ Tự động Tạo Tài liệu)

Một công cụ dòng lệnh (CLI) sử dụng Google Gemini API để tự động tạo ra các bài viết, báo cáo chi tiết về các chủ đề ngẫu nhiên và lưu chúng dưới dạng file `.docx`.

## Tính năng

- **Tạo chủ đề ngẫu nhiên:** Tự động sinh ra các chủ đề đa dạng và thú vị.
- **Sinh nội dung chuyên sâu:** Sử dụng mô hình `gemini-1.5-flash` để viết các bài phân tích có cấu trúc (tiêu đề, giới thiệu, thân bài, kết luận) với độ dài 800-1200 từ.
- **Định dạng Markdown:** Nội dung được tạo ban đầu ở định dạng Markdown.
- **Chuyển đổi sang DOCX:** Tự động sử dụng Pandoc để chuyển đổi file Markdown thành `.docx`.
- **Xử lý song song:** Có khả năng tạo nhiều tài liệu cùng lúc để tăng hiệu suất.

## Yêu cầu

- Python 3.x
- [Pandoc](https://pandoc.org/installing.html)
- Một khóa API của Google Gemini.

## Cài đặt & Cấu hình

1. **Clone repository:**
   ```bash
   git clone <URL_CUA_REPO_TREN_GITHUB>
   cd ai-document-generator
   ```

2. **Cài đặt thư viện Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình Pandoc:**
   Dự án này đã bao gồm `pandoc.exe` trong thư mục `pandoc-3.8.2`. Script đã được cấu hình để sử dụng đường dẫn này. Nếu bạn di chuyển thư mục, hãy cập nhật biến `PANDOC_PATH` trong `main.py`.

4. **Cấu hình API Key:**
   - Tạo một file tên là `.env` ở thư mục gốc.
   - Thêm nội dung sau vào file `.env` và thay thế `YOUR_API_KEY_HERE` bằng khóa API của bạn:
     ```
     GEMINI_API_KEY="YOUR_API_KEY_HERE"
     ```

## Sử dụng

Chạy script từ dòng lệnh và cung cấp số lượng file bạn muốn tạo:

```bash
python main.py <so_luong_file>
```

**Ví dụ:** Để tạo 5 tài liệu:

```bash
python main.py 5
```

Các file `.docx` sẽ được tạo và lưu trong thư mục `docs`.
