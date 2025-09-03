from unsloth import FastLanguageModel
from transformers import TextStreamer
import os

# --- Конфигурация ---
# Путь к сохраненным LoRA адаптерам
LORA_MODEL_PATH = "./lora_model"

# --- 1. Загрузка модели и токенизатора ---
max_seq_length = 2048
dtype = None      # None для автоматического определения
load_in_4bit = True # 4-битная квантизация для экономии памяти

print("Loading base model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/gemma-3-270m-unsloth-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# --- 2. Применение LoRA адаптеров ---
print(f"Loading LoRA adapters from: {LORA_MODEL_PATH}")
# Проверка существования директории
if not os.path.exists(LORA_MODEL_PATH):
    raise FileNotFoundError(
        f"Директория с адаптерами не найдена: {LORA_MODEL_PATH}. "
        f"Убедитесь, что путь указан верно относительно расположения скрипта."
    )

model.load_adapter(LORA_MODEL_PATH)
print("LoRA adapters loaded successfully.")

# --- 3. Подготовка к инференсу ---
# Шаблон промпта должен быть идентичен тому, что использовался при обучении
prompt_template = """### Instruction:
Определи, является ли следующий текст рекламой. Ответь "1", если это реклама, и "0", если нет.

### Input:
{}

### Response:
{}"""

# Инициализация стримера для вывода текста в реальном времени
text_streamer = TextStreamer(tokenizer)

def run_inference(input_text):
    """Функция для форматирования промпта и запуска генерации."""
    prompt = prompt_template.format(
        input_text,
        "", # Пустой ответ для генерации
    )
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

    print("---")
    _ = model.generate(**inputs, streamer=text_streamer, max_new_tokens=5) # 5 токенов достаточно для "1" или "0"
    print("\n")

# --- 4. Запуск тестового инференса ---

# Пример №1: Рекламный текст
ad_text = """
Студия Бажолик ищет мастера перманентного макияжа с опытом работы. Мы ориентируемся на профессионализм, качество услуг и безопасность клиентов. Если вы готовы стать частью нашей дружелюбной команды и развиваться в области красоты, мы будем рады видеть вашу заявку.

🏡Мы находимся по адресу Юбилейная 28/1
⏰Режим работы с 9:00 до 21:00
📱Телефон +7(495)1015258
"""
run_inference(ad_text)

# Пример №2: Обычный текст
non_ad_text = "Привет, как твои дела? Я вчера посмотрел новый фильм, очень понравился. А ты что делаешь на выходных?"
run_inference(non_ad_text)

# Пример №3: Ссылка без рекламного контекста
link_text = "Кстати, вот интересная статья про квантовую физику: example.com/article"
run_inference(link_text)

example_text = """
🤓 Звонок для учителя, а новые знания — для всех

Нейросеть Сбера ГигаЧат (https://t.me/gigachat_bot?start=mk_BTW_students_seeding_bts_w_moscowach&erid=2Vtzquu1o87) станет надёжным напарником в учёбе и саморазвитии. Она объяснит сложную тему доступным языком и даст советы, как освоить полезные навыки.

Используйте искусственный интеллект, чтобы освежить школьную программу или написать эссе. В Телеграм-боте (https://t.me/gigachat_bot?start=mk_BTW_students_seeding_bts_w_moscowach&erid=2Vtzquu1o87) как раз есть функция для работы с роликами — выбирайте «Пересказать видео по ссылке» в основном меню.
"""
run_inference(example_text)

print("---")
print("Inference examples finished.")
