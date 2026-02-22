class UIController {
    constructor() {
        this.btnInc = document.getElementById("btn-inc");
        this.btnDec = document.getElementById("btn-dec");
        this.countDisplay = document.getElementById("file-count-display");
        this.presetBtns = document.querySelectorAll(".grid > button");
        this.btnGenerate = document.getElementById("btn-generate");
        this.inputApiKey = document.querySelector('input[type="password"]');
        this.errorMsg = document.getElementById("error-msg");

        this.progressContainer = document.getElementById("progress-container");
        this.progressBar = document.getElementById("progress-bar");
        this.progressText = document.getElementById("progress-text");
        this.statusText = document.getElementById("status-text");
        this.logText = document.getElementById("log-text");
        this.pingIndicator = document.getElementById("ping-indicator");
        this.downloadContainer = document.getElementById("download-link-container");
        this.downloadLink = document.getElementById("download-link");

        this.fileCount = 10;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.btnInc.onclick = () => this.updateCount(this.fileCount + 1);
        this.btnDec.onclick = () => this.updateCount(this.fileCount - 1);
        this.presetBtns.forEach(
            (btn) => (btn.onclick = () => this.updateCount(parseInt(btn.innerText))),
        );

        const toggleBtn = document.querySelector(".relative.group > button");
        if(toggleBtn) {
            toggleBtn.onclick = (e) => this.toggleApiKeyVisibility(e);
        }
    }

    updateCount(val) {
        this.fileCount = Math.max(1, Math.min(20, val));
        this.countDisplay.innerText = this.fileCount;
        this.presetBtns.forEach((btn) => {
            if (parseInt(btn.innerText) === this.fileCount) {
                btn.className = "h-9 rounded-lg bg-slate-200 text-slate-900 font-semibold text-sm shadow-inner shadow-slate-300 border border-slate-300";
            } else {
                btn.className = "h-9 rounded-lg bg-white border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-300 active:bg-slate-50 text-slate-600 font-medium text-sm transition-all hover:bg-slate-50";
            }
        });
    }

    toggleApiKeyVisibility(e) {
        const type = this.inputApiKey.type === "password" ? "text" : "password";
        this.inputApiKey.type = type;
        e.currentTarget.innerHTML = `<span class="material-symbols-outlined text-[18px]">${type === "password" ? "visibility_off" : "visibility"}</span>`;
    }

    getApiKey() {
        return this.inputApiKey.value.trim();
    }

    showError(msg) {
        let localizedMsg = msg;
        if (msg === "Please enter your Cerebras API Key") {
            localizedMsg = "Vui lòng nhập API Key hợp lệ của Cerebras";
        }
        this.errorMsg.innerText = localizedMsg;
        this.errorMsg.classList.remove("hidden");
    }

    hideError() {
        this.errorMsg.classList.add("hidden");
    }

    setGeneratingState() {
        this.hideError();
        this.downloadContainer.classList.add("hidden");
        this.btnGenerate.disabled = true;
        this.btnGenerate.classList.add("opacity-50", "cursor-not-allowed");

        this.progressContainer.classList.remove("hidden");
        this.progressBar.style.width = "0%";
        this.progressText.innerText = "0%";
        this.statusText.innerText = "Đang khởi tạo...";
        this.pingIndicator.classList.add("animate-ping");
        this.logText.innerText = "Đang kết nối tới Cerebras API...";
    }

    updateProgress(percentage, completedFiles, targetFiles, latestMessage) {
        this.progressBar.style.width = `${percentage}%`;
        this.progressText.innerText = `${percentage}%`;
        this.statusText.innerText = `Đang tạo (${completedFiles}/${targetFiles})...`;
        if (latestMessage) {
            this.logText.innerText = latestMessage;
        }
    }

    setCompletedState(data, onResetCallback) {
        this.pingIndicator.classList.remove("animate-ping");
        this.statusText.innerText = "Hoàn tất!";
        this.logText.innerText = `Đã xong. ${data.completed} thành công, ${data.failed} thất bại.`;

        if (data.download_url) {
            this.downloadLink.href = data.download_url;
            this.downloadContainer.classList.remove("hidden");

            this.downloadLink.onclick = async () => {
                try {
                    await fetch("/api/reset", { method: "POST" });
                } catch (e) { }
                setTimeout(() => {
                    this.downloadContainer.classList.add("hidden");
                    this.progressContainer.classList.add("hidden");
                    this.statusText.innerText = "";
                    this.logText.innerText = "";
                    this.progressBar.style.width = "0%";
                    this.progressText.innerText = "0%";
                }, 1000);
            };
        }
        setTimeout(() => this.resetGenerateButton(), 5000);
    }

    resetGenerateButton() {
        this.btnGenerate.disabled = false;
        this.btnGenerate.classList.remove("opacity-50", "cursor-not-allowed");
    }

    showModal(type) {
        const modal = document.getElementById('legal-modal');
        const content = document.getElementById('legal-modal-content');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');
        
        const texts = {
            'terms': {
                title: 'Điều Khoản Sử Dụng (Terms)',
                html: '<p>Tất cả nội dung được biên soạn bởi ứng dụng này đều do Trí tuệ Nhân tạo (Cerebras Llama-3 70B) tự động tổng hợp dựa trên kiến thức chung.</p><p>Hệ thống chỉ đóng vai trò tự động hóa. <b>Chúng tôi hoàn toàn không chịu trách nhiệm pháp lý</b> về tính chính xác của thông tin, các rủi ro bản quyền hay bất kỳ sai sót thực tế (hallucinations) nào có thể xuất hiện trong nội dung văn bản. Việc sử dụng, phát hành hoặc thương mại hóa các tài liệu này là rủi ro và trách nhiệm hoàn toàn thuộc về phía người dùng.</p>'
            },
            'privacy': {
                title: 'Chính Sách Bảo Mật (Privacy)',
                html: '<p>Tôn trọng tối đa quyền riêng tư: Ứng dụng Không yêu cầu người dùng đăng nhập và Không lưu trữ bất cứ tài nguyên hoặc lịch sử tạo PDF nào trên môi trường máy chủ lâu dài.</p><p>Tất cả tài liệu nén (ZIP) sau khi được tải lên máy chủ trung gian `Tmpfiles.org` sẽ tuân theo thiết lập tự hủy của nền tảng đó. <b>Cerebras API Key</b> của bạn chỉ được hệ thống dùng tạm và sẽ bị xóa ngay lập tức khỏi bộ nhớ (RAM) sau khi tiến trình hoàn tất. Chúng tôi không thu thập Log API Key.</p>'
            },
            'support': {
                title: 'Hỗ Trợ (Support)',
                html: '<p>Nếu hệ thống báo lỗi trong quá trình chạy (Error during generation) hoặc bị kẹt mạng, 99% nguyên nhân đến từ việc API Key của bạn bị hết hạn mức (Rate Limit) hoặc cấu hình Cerebras Cloud thay đổi. Vui lòng kiểm tra lại tài khoản API.</p><p>Hệ thống mã nguồn đã được tối ưu hóa toàn diện theo chuẩn OOP Clean Architecture, mọi lỗi logic còn tồn đọng xin tiếp tục gửi Feedback vào Repository lưu trữ mã nguồn.</p>'
            },
            'howItWorks': {
                title: 'Hướng dẫn sử dụng (How it works)',
                html: '<ul class="list-disc pl-4 space-y-2 mb-4"><li><b>Bước 1:</b> Hệ thống gọi API đến mô hình ngôn ngữ Llama-3 70B thông qua nền tảng Cerebras Cloud để tự động lên ý tưởng.</li><li><b>Bước 2:</b> AI sẽ sinh ra các văn bản (khoảng 800-1200 từ) về các chủ đề ngẫu nhiên theo cấu trúc được thiết lập sẵn.</li><li><b>Bước 3:</b> Nội dung văn bản được hệ thống tự động biên dịch và tạo thành file định dạng PDF thông qua thư viện ReportLab.</li><li><b>Bước 4:</b> Toàn bộ các file PDF sinh ra được nén chung thành 1 tập tin ZIP và tải lên dịch vụ lưu trữ trung gian <a href="https://tmpfiles.org/" target="_blank" class="text-blue-500 hover:underline">tmpfiles.org</a>.</li><li><b>Bước 5:</b> Hệ thống sẽ trả về đường dẫn tải xuống tập tin ZIP. Mọi dữ liệu tạm thời trên ứng dụng sẽ được gỡ bỏ ngay sau đó để giải phóng bộ nhớ.</li></ul>'
            }
        };

        title.innerText = texts[type].title;
        body.innerHTML = texts[type].html;

        modal.classList.remove('hidden');
        // Trigger reflow for animation
        void modal.offsetWidth;
        modal.classList.remove('opacity-0');
        content.classList.remove('scale-95');
        content.classList.add('scale-100');
    }

    hideModal() {
        const modal = document.getElementById('legal-modal');
        const content = document.getElementById('legal-modal-content');
        
        modal.classList.add('opacity-0');
        content.classList.remove('scale-100');
        content.classList.add('scale-95');
        
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    }
}

class AppManager {
    constructor() {
        this.ui = new UIController();
        this.pollInterval = null;
        
        this.ui.btnGenerate.onclick = () => this.startGeneration();
    }

    async startGeneration() {
        const apiKey = this.ui.getApiKey();
        if (!apiKey) {
            this.ui.showError("Vui lòng nhập API Key hợp lệ của Cerebras");
            return;
        }

        this.ui.setGeneratingState();

        try {
            const res = await fetch("/api/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ api_key: apiKey, num_files: this.ui.fileCount }),
            });

            const data = await res.json();
            if (data.status === "error") {
                throw new Error(data.message);
            }

            this.pollInterval = setInterval(() => this.checkStatus(), 1000);
        } catch (err) {
            this.ui.showError(err.message);
            this.ui.resetGenerateButton();
        }
    }

    async checkStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();

            if (!data.is_running && data.total === 0) return;

            const targetFiles = data.total;
            const completedFiles = data.completed + data.failed;
            const percentage = targetFiles ? Math.round((completedFiles / targetFiles) * 100) : 0;
            const latestMessage = data.messages.length > 0 ? data.messages[data.messages.length - 1] : null;

            this.ui.updateProgress(percentage, completedFiles, targetFiles, latestMessage);

            if (!data.is_running && completedFiles > 0) {
                clearInterval(this.pollInterval);
                this.ui.setCompletedState(data);
            }
        } catch (err) {
            console.error("Polling error:", err);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.app = new AppManager();
});
