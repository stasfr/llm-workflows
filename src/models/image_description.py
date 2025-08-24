from PIL import Image
from transformers import pipeline
import torch

class ImageDescription:
    def __init__(self, model_name):
        self.pipe = pipeline(
            "image-to-text",
            model=model_name,
            model_kwargs={"torch_dtype": torch.bfloat16, "low_cpu_mem_usage": True},
            device_map="auto"
        )

    def get_completion(self, image: Image.Image, prompt: str) -> str:
        outputs = self.pipe(image, prompt=prompt, max_new_tokens=256)

        if outputs and isinstance(outputs, list) and 'generated_text' in outputs[0]:
            return outputs[0]['generated_text']
        else:
            return "Error: Could not generate a response."
