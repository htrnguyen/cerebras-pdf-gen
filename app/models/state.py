from typing import List, Tuple, Optional
import threading

class GenerationState:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.is_running: bool = False
            self.total: int = 0
            self.completed: int = 0
            self.failed: int = 0
            self.messages: List[str] = []
            self.download_url: Optional[str] = None
            self.generated_pdf_data: List[Tuple[str, bytes]] = []

    def start_generation(self, total: int):
        with self._lock:
            self.is_running = True
            self.total = total
            self.completed = 0
            self.failed = 0
            self.messages.clear()
            self.download_url = None
            self.generated_pdf_data.clear()

    def stop_generation(self):
        with self._lock:
            self.is_running = False

    def add_message(self, message: str, max_messages: int = 10):
        with self._lock:
            self.messages.append(message)
            if len(self.messages) > max_messages:
                self.messages.pop(0)

    def increment_completed(self, filename: str, pdf_bytes: bytes):
        with self._lock:
            self.completed += 1
            self.generated_pdf_data.append((filename, pdf_bytes))

    def increment_failed(self):
        with self._lock:
            self.failed += 1

    def set_download_url(self, url: str):
        with self._lock:
            self.download_url = url

    def get_public_status(self) -> dict:
        with self._lock:
            return {
                "is_running": self.is_running,
                "total": self.total,
                "completed": self.completed,
                "failed": self.failed,
                "messages": list(self.messages),
                "download_url": self.download_url,
            }

    def get_and_clear_pdf_data(self) -> List[Tuple[str, bytes]]:
        with self._lock:
            data = list(self.generated_pdf_data)
            self.generated_pdf_data.clear()
            return data

    @property
    def is_currently_running(self) -> bool:
        with self._lock:
            return self.is_running

global_state = GenerationState()
