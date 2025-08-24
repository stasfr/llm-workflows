import base64
import io
from openai import OpenAI
from PIL import Image

class ImageDescription:
    """
    A class to interact with a local Large Language Model that has vision capabilities,
    through an OpenAI-compatible API (like LM Studio).
    """
    def __init__(self, model_name: str, api_base: str = "http://127.0.0.1:1234/v1"):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=api_base,
            api_key="not-needed" # required even if not used by the server
        )

    def _image_to_base64(self, image: Image.Image) -> str:
        """Converts a PIL image to a base64 encoded string."""
        buffered = io.BytesIO()
        # Convert image to RGB to ensure compatibility
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def get_description(self, image: Image.Image) -> str:
        """
        Generates a description for a given image.
        """
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
                max_tokens=300,
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "Error: No response generated."
        except Exception as e:
            return f"Error: An exception occurred: {e}"

    def get_tag(self, image: Image.Image) -> str:
        """
        Generates tags for a given image.
        """
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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=50, # Tags are usually shorter
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "Error: No response generated."
        except Exception as e:
            return f"Error: An exception occurred: {e}"
