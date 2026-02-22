# Cerebras PDF Generator 🚀

**Cerebras PDF Generator** là một ứng dụng Web tự động sinh ra hàng loạt các tài liệu học thuật và kiến thức chuyên sâu dưới định dạng PDF chuẩn xác, sử dụng sức mạnh xử lý siêu tốc của **Cerebras Llama-3 70B**. Dự án được xây dựng dựa trên kiến trúc OOP Clean Architecture tối ưu hóa để triển khai linh hoạt (Docker, Hugging Face Spaces, Render, GitHub Pages kết nối Backend).

---

## 🌟 Tính Năng Nổi Bật

- **Sinh Ý Tưởng Ngẫu Nhiên**: Tích hợp Cerebras API để tạo ra các kịch bản, chủ đề giáo dục và khoa học ngẫu nhiên hoàn toàn bằng Tiếng Việt (800-1200 từ).
- **Trình Bày Tự Động (PDF)**: Sử dụng thư viện `ReportLab` và phông chữ tùy chỉnh (`SVN-Arial`) để dàn trang tự động 100% PDF tiếng Việt không bị lỗi font hay bố cục.
- **Xử Lý Hàng Loạt (Batch Processing)**: Khả năng tạo một lúc 5-20 file PDF và đóng gói thành tệp tin `.zip` duy nhất, tiết kiệm thời gian đáng kể.
- **Quyền Riêng Tư Tuyệt Đối**: 
  - API Key chỉ sử dụng tạm thời trên RAM để xử lý, không bao giờ sao lưu hay lưu vết (Logs).
  - Tệp tải xuống (ZIP) được truyền tải trung gian và thiết lập tự hủy qua `tmpfiles.org`.
- **Giao Diện Thanh Lịch**: Thiết kế UI mang cảm hứng macOS tinh gọn, tích hợp đầy đủ Modal Hướng dẫn và Chính sách. 

---

## 🛠️ Trải Nghiệm & Cài Đặt

### 1. Triển Khai Trực Tiếp Lên Hugging Face Spaces (Khuyên Dùng)

Dự án đã được tích hợp sẵn 100% tài nguyên (`Dockerfile` & `requirements.txt`) để máy chủ Hugging Face có thể Build và Chạy ngay lập tức:
1. Tạo một tài khoản Hugging Face, tạo không gian mới (New Space) dạng **Docker Blank**.
2. **Setup Github Actions**: Cấp mã **Hugging Face Access Token** (quyền Write) và đính kèm vào Secrets (`HF_TOKEN`) của GitHub này.
3. Kịch bản `.github/workflows/deploy-hf.yml` sẽ thực thi, kéo bản cập nhật lên Space liên tục mỗi khi có Push.

### 2. Cài Đặt và Chạy Tại Máy Tính (Local)

**Yêu cầu môi trường:** Python 3.9+ 

1. **Clone mã nguồn:**
   ```bash
   git clone https://github.com/htrnguyen/cerebras-pdf-gen.git
   cd cerebras-pdf-gen
   ```
2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Chạy Server Backend:**
   ```bash
   python main.py
   # Hệ thống sẽ khởi chạy tại: http://localhost:8000
   ```

---

## 🏛️ Kiến Trúc Mã Nguồn (Clean OOP Architecture)

Ứng dụng chia làm Backend và Website Tĩnh:
- `main.py`: Entrypoint của ứng dụng. Cung cấp API Router FastAPI cực nhẹ.
- `app/api/endpoints.py`: Xử lý HTTP Request để khởi chạy đa luồng Background Tasks.
- `app/core/workflow.py`: Bộ điều hướng chính (Orchestrator).
- `app/services/...`: Tầng dịch vụ chuyên biệt (Generation, PDF ReportLab, ZIP Storage, Fallback Prompts).
- `app/models/state.py`: Global State - quản lý tiến trình (0-100%).
- `static/`: Frontend tĩnh, giao diện siêu tốc với CSS Tailwind nhúng trực tiếp.

---

## 📜 Giấy Phép & Tuyên Bố Trách Nhiệm

Dự án này là một công cụ giúp tạo nội dung dựa trên AI tạo sinh:
- **Tác giả không chịu trách nhiệm:** Với độ chính xác, bản quyền, hoặc lỗi kiến thức (hallucinations) có trong các File PDF được hệ thống sinh ra. Mọi tác vụ sử dụng dữ liệu phụ thuộc vào quyết định của phía người dùng cuối. 
- Giấy phép Mã Nguồn: **MIT License**. Bạn được tự do phân phối, tùy biến nhưng cần giữ lại bản quyền khai sinh.
