import random


class PromptService:
    @staticmethod
    def get_fallback_topics() -> list[str]:
        return [
            "Sinh học tiến hóa",
            "Vật lý tự nhiên",
            "Lịch sử dân tộc",
            "Hóa học ứng dụng",
            "Địa lý kinh tế",
            "Văn học dân gian",
        ]

    @staticmethod
    def construct_single_prompt(chosen_area: str, random_seed: int = None) -> str:
        if random_seed is None:
            random_seed = random.randint(1, 1000000)

        return f"""
        (Seed: {random_seed} - Chủ đề: {chosen_area})
        
        Viết một bài trình bày hoặc bài giảng chi tiết bằng Tiếng Việt (khoảng 800-1200 từ, tương đương 1 đến 1.5 trang A4) về một khái niệm/sự kiện cụ thể trong lĩnh vực '{chosen_area}'. 
        YÊU CẦU QUAN TRỌNG NHẤT:
        1. Nội dung phải hoàn toàn chính xác, khoa học, dựa trên kiến thức chuẩn sách giáo khoa (SGK) hoặc kiến thức phổ thông đã được công nhận. KHÔNG ĐƯỢC BỊA ĐẶT (no hallucination).
        2. Phân tích sâu sắc, chi tiết, mở rộng các khía cạnh liên quan để đảm bảo bài viết đủ độ dài và chất lượng cao. Không viết hời hợt hoặc lập dàn ý lướt qua.
        3. Không lặp lại nội dung chung chung, hãy đi vào một góc nhìn hoặc khái niệm ngẫu nhiên sâu sắc.
        
        Chỉ trả về MỘT đối tượng JSON duy nhất.

        JSON bao gồm 3 keys:
        1.  "full_topic": Tên tiêu đề dài đầy đủ của bài viết (Tiếng Việt).
        2.  "short_topic": Tên rút gọn (5-10 chữ) để làm tên file.
        3.  "content": Nội dung bài viết bằng Tiếng Việt. Định dạng bằng Markdown cơ bản (# cho Tiêu đề chính, ## cho Luận điểm phụ) và các đoạn văn dài, chi tiết.
        LƯU Ý KỸ THUẬT: Đảm bảo chuỗi JSON hợp lệ 100%. Tất cả khóa (keys) phải được bọc trong dấu ngoặc kép. Tuyệt đối không để lại dấu phẩy thừa (trailing commas) ở cuối mảng hoặc object.
        """

    @staticmethod
    def get_system_role() -> str:
        return "Bạn là một chuyên gia giáo dục thông thái. Bạn luôn tạo ra các nội dung bài giảng chính xác, chuẩn mực sách giáo khoa và KHÔNG bịa đặt. Bạn PHẢI trả về duy nhất 1 đối tượng JSON hợp lệ, KHÔNG kèm text nào khác, KHÔNG có trailing commas."
