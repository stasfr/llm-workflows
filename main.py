import os
from tg_parsing.parser import parse_raw_telegram_data, filter_parsed_telegram_data
import models
from tqdm import tqdm
from tg_parsing.data import ParsedTelegramData
from tg_parsing.parser import count_json_items, stream_filtered_tg_data

# Устанавливаем директорию для кэша Hugging Face
os.environ["HF_HOME"] = "F:\\huggingface_cache"

WORKING_DIR = './output'
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')

def main():
    parse_raw_telegram_data()
    filter_parsed_telegram_data([], [], [], 3)

    image_describer = models.ImageDescription(model_name="google/gemma-3-4b-it")
    text_embedder = models.TextEmbedder(model_name="intfloat/multilingual-e5-large-instruct")

    total_items = count_json_items(FILTERED_FILE, 'item')
    filtered_tg_data = stream_filtered_tg_data(FILTERED_FILE)

    with tqdm(total=total_items, desc="Parsing Telegram Data") as pbar:
        for item in filtered_tg_data:
            pbar.update(1)

if __name__ == "__main__":
    main()
