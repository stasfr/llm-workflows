import torch
import os
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from huggingface_hub import login

HF_TOKEN = os.getenv("HF_TOKEN")

login(token=HF_TOKEN)

# 1. Загрузка модели и токенизатора
max_seq_length = 2048
dtype = None # None для автоматического определения
load_in_4bit = True # Используем 4-битную квантизацию для экономии памяти

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3-270m-unsloth-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 2. Добавление LoRA адаптеров для эффективной настройки
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = False,
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# 3. Подготовка данных из локального JSON
# Шаблон промпта для модели
prompt_template = """### Instruction:
Определи, является ли следующий текст рекламой. Ответь "1", если это реклама, и "0", если нет.

### Input:
{}

### Response:
{}"""

EOS_TOKEN = tokenizer.eos_token
def formatting_prompts_func(examples):
    inputs     = examples["text"]
    outputs    = examples["result"]
    texts = []
    for input_text, output_text in zip(inputs, outputs):
        # Форматируем текст по шаблону и добавляем токен конца строки
        text = prompt_template.format(input_text, output_text) + EOS_TOKEN
        texts.append(text)
    return { "text" : texts, }

# Загружаем JSON файл
dataset = load_dataset("json", data_files="dataset.json", split="train")
dataset = dataset.map(formatting_prompts_func, batched = True,)

# 4. Настройка и запуск обучения
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 8,
        gradient_accumulation_steps = 1,
        warmup_steps = 5,
        num_train_epochs = 2,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

print("Starting training...")
trainer.train()
print("Training finished.")

# 5. Сохранение LoRA адаптеров
print("Saving LoRA adapters to 'lora_model'...")
model.save_pretrained("lora_model")
print("Model saved successfully.")

# 6. Пример инференса после обучения
print("\nRunning inference example...")
from transformers import TextStreamer

# ЗАПОЛНИТЕ ЭТО ПОЛЕ ВАШИМ ТЕКСТОМ
input_text = """
"MEBELUX" (https://t.me/+emfagIYEsYViZGRi) - мебельная команда с безупречной репутацией.
Специализируются на производстве современной, удобной и надежной мебели, созданной для беспроблемной службы.

Почему выбирают MEBELUX? (https://t.me/+emfagIYEsYViZGRi)
◽25 лет опыта
◽Экономия до 50% – без посредников и розничных наценок
◽Срок изготовления 2-4 недели
◽Чистота и аккуратность при монтаже
◽Предоплата от 10%
⭐ Бесплатно: замер, проект, доставка!

✍️ Подпишитесь на "MEBELUX" (https://t.me/+emfagIYEsYViZGRi)
🤍 Посмотрите отзывы (https://t.me/MEBELYX/564) клиентов
🧮 Оставьте заявку на бесплатный расчет: @mebelsakas
📞 WhatsApp / Звонок: +7(927)093-37-88
"""

prompt = prompt_template.format(
    input_text, # Текст для инференса
    "",         # Пустой ответ для генерации
)

inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
text_streamer = TextStreamer(tokenizer)

print(f"Generating response for input: '{input_text}'")
_ = model.generate(**inputs, streamer=text_streamer, max_new_tokens=256)
