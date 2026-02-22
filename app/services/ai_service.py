import json
import time
import re
from typing import List, Tuple
from cerebras.cloud.sdk import Cerebras

from app.services.prompt_service import PromptService


class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        """Initialize Cerebras client with API Key"""
        self.client = Cerebras(api_key=api_key)

    @staticmethod
    def verify_api_key(api_key: str) -> bool:
        """Perform a quick, low-cost check to verify if the API key is active"""
        try:
            temp_client = Cerebras(api_key=api_key)
            # Perform a minimal 1-token request to strictly force authentication
            temp_client.chat.completions.create(
                model="llama3.1-8b",
                messages=[{"role": "user", "content": "hi"}],
                max_completion_tokens=1
            )
            return True
        except Exception:
            return False

    def generate_topics(self, num_topics: int) -> List[str]:
        prompt = f'Tạo một mảng JSON chứa {num_topics} chủ đề học thuật hoặc kiến thức phổ thông ngẫu nhiên (hoàn toàn bằng Tiếng Việt). Mỗi chủ đề mang tính giáo dục chuyên sâu, ngẫu nhiên ở đa dạng các lĩnh vực như Lịch sử, Địa lý, Toán, Lý, Hóa, Sinh... Trả về đúng 1 JSON object có dạng: {{\n"topics": [ "chủ đề 1", "chủ đề 2", ... ]\n}}'

        try:
            response = self.client.chat.completions.create(
                model="llama3.1-8b",
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn là chuyên gia giáo dục. Chỉ trả về JSON thuần hợp lệ, không text nào khác.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,
                max_completion_tokens=4096,
                response_format={"type": "json_object"},
            )

            data = json.loads(response.choices[0].message.content.strip())
            topics = data.get("topics", [])

            # Fill with fallbacks if generation comes up short
            if len(topics) < num_topics:
                fallbacks = PromptService.get_fallback_topics()
                import random

                while len(topics) < num_topics:
                    topics.append(random.choice(fallbacks))

            return topics[:num_topics]
        except Exception as e:
            raise RuntimeError(f"Failed to generate topics: {e}")

    def generate_single_document_content(
        self, chosen_area: str
    ) -> Tuple[str, str, str]:
        """Returns (full_topic, base_filename, markdown_content)"""
        prompt = PromptService.construct_single_prompt(chosen_area)
        system_role = PromptService.get_system_role()

        data = None
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model="llama3.1-8b",
                    messages=[
                        {"role": "system", "content": system_role},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.9,
                    max_completion_tokens=4096,
                    response_format={"type": "json_object"},
                )

                response_text = response.choices[0].message.content.strip()
                data = json.loads(response_text)
                break  # Success
            except json.JSONDecodeError as e:
                if attempt == 1:
                    raise Exception(
                        f"Failed to parse JSON after 2 attempts. LLM Error: {e}"
                    )
                time.sleep(1)  # Wait 1s and retry

        full_topic = data.get("full_topic", "Untitled Topic").strip()
        short_topic = data.get("short_topic", "generated_doc").strip()
        content = data.get("content", "No content generated.").strip()

        cleaned_short_topic = re.sub(r'[\\/:*?"<>|]', "", short_topic).strip()
        import random

        base_filename = (
            f"[Reference][AI][{cleaned_short_topic[:70]}][{random.randint(1000,9999)}]"
        )

        return full_topic, base_filename, content
