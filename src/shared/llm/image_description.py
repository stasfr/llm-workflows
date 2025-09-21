from src.config import LLM_API_URL

from typing import Tuple, Dict, Optional

import base64
import io
import time
from openai import OpenAI
from PIL import Image


class ImageDescription:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=LLM_API_URL,
            api_key="not-needed"  # required even if not used by the server
        )

    def _image_to_base64(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        # Convert image to RGB to ensure compatibility
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def get_description(self, image: Image.Image) -> Tuple[str, Optional[Dict], float]:
        system_prompt = '''
        Твоя задача — составить короткое и объективное описание изображения (1-2 предложения).

        Правила:
        1.  Описывай только факты: кто/что изображено, что делает, где находится.
        2.  Начинай ответ сразу с описания. Никаких приветствий и фраз вроде "На этом фото...".
        3.  Не анализируй настроение, эмоции или атмосферу.
        4.  Игнорируй любые логотипы и надписи, особенно "инстажелдор".
        5.  Отвечай строго на русском языке.

        Примеры правильного ответа:
        - Люди отдыхают на песчаном пляже у моря.
        - Рыжая собака породы корги лежит на зеленой траве.
        - Два человека в камуфляже ведут перестрелку на городской улице.
        '''
        base64_image = self._image_to_base64(image)

        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                temperature=1,
            )
            end_time = time.time()
            duration = end_time - start_time
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content, response.usage.model_dump() if response.usage else None, duration
            return "Error: No response generated.", None, duration
        except Exception as e:
            return f"Error: An exception occurred: {e}", None, 0.0

    def get_tag(self, image: Image.Image) -> Tuple[str, Optional[Dict], float]:
        system_prompt = """
        Твоя задача — сгенерировать список тегов для изображения.

        Правила:
        1.  Теги должны быть существительными или короткими фразами, описывающими ключевые объекты, действия или концепции на изображении.
        2.  Разделяй теги запятыми.
        3.  Не используй предложения.
        4.  Игнорируй любые логотипы и надписи, особенно "инстажелдор".
        5.  Отвечай строго на русском языке.

        Примеры правильного ответа:
        - человек, собака, парк, прогулка
        - город, ночь, огни, здания, улица
        - еда, тарелка, овощи, ужин
        """
        base64_image = self._image_to_base64(image)

        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
            )
            end_time = time.time()
            duration = end_time - start_time
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content, response.usage.model_dump() if response.usage else None, duration
            return "Error: No response generated.", None, duration
        except Exception as e:
            return f"Error: An exception occurred: {e}", None, 0.0

    def get_structured_description(self, image: Image.Image) -> Tuple[str, Optional[Dict], float]:
        system_prompt = '''
        Твоя задача — извлечь структурированную информацию из изображения и вернуть ее в формате JSON.

        Правила:
        1.  Проанализируй изображение и заполни значения для следующих ключей: "main_subject", "action", "setting", "secondary_objects", "composition".
        2.  Ответ должен быть строго в формате JSON. Не добавляй никаких пояснений или приветствий до или после JSON-объекта.
        3.  Описывай только объективные факты.
        4.  Игнорируй любые логотипы и надписи.
        5.  Все значения в JSON должны быть на русском языке.

        Ключи для заполнения:
        - main_subject: Кто или что является главным объектом на изображении?
        - action: Какое основное действие происходит? (Если нет действия, укажи "статика")
        - setting: Где происходит действие (окружение, фон)?
        - secondary_objects: Какие значимые второстепенные объекты присутствуют? (список строкой)
        - composition: Краткое описание композиции (например: крупный план, панорама, портрет, вид сверху).

        Пример правильного ответа:
        {
          "main_subject": "Рыжая собака породы корги",
          "action": "лежит",
          "setting": "зеленая трава в парке",
          "secondary_objects": "деревья на фоне, желтый мяч",
          "composition": "крупный план"
        }
        '''
        base64_image = self._image_to_base64(image)

        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
            )
            end_time = time.time()
            duration = end_time - start_time
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content, response.usage.model_dump() if response.usage else None, duration
            return "Error: No response generated.", None, duration
        except Exception as e:
            return f"Error: An exception occurred: {e}", None, 0.0
