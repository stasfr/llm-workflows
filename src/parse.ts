import fs from 'fs/promises';

const processText = (textValue) => {
  if (!textValue) return '';

  if (typeof textValue === 'string') return textValue;

  if (Array.isArray(textValue)) {
    return textValue.map((part) => processText(part))
      .join('');
  }

  if (typeof textValue === 'object' && typeof textValue.text === 'string') {
    return textValue.text;
  }

  return '';
};

const transformMessagesToPosts = (inputData) => {
  if (!inputData || !Array.isArray(inputData.messages)) {
    console.error('Ошибка: Входной JSON не содержит массив \'messages\'.');

    return { posts: [] };
  }

  const posts = inputData.messages
    .map((message) => {
      // Используем нашу новую мощную функцию для обработки текста
      const processedText = processText(message.text);

      // Возвращаем объект с обработанным текстом и датой
      return {
        text: processedText,
        date: message.date,
      };
    })
    // Отфильтровываем посты, у которых в итоге не оказалось текста
    .filter((post) => post.text.trim() !== '');

  return { posts: posts };
};

const INPUT_FILE = 'plain_data/input.json';
const OUTPUT_FILE = 'plain_data/output.json';

// Основная асинхронная функция для выполнения всех действий
const processFile = async () => {
  try {
    // 1. Читаем исходный файл
    const rawData = await fs.readFile(INPUT_FILE, 'utf8');

    // 2. Парсим JSON в объект JavaScript
    const inputJson = JSON.parse(rawData);

    // 3. Вызываем нашу функцию для трансформации данных
    const outputJson = transformMessagesToPosts(inputJson);

    // 4. Преобразуем результирующий объект обратно в строку JSON (с красивым форматированием)
    const outputString = JSON.stringify(outputJson, null, 2);

    // 5. Записываем результат в новый файл
    await fs.writeFile(OUTPUT_FILE, outputString);

    console.log(`✅ Файл ${OUTPUT_FILE} успешно создан!`);
  } catch (error) {
    console.error('❌ Произошла ошибка во время выполнения скрипта:', error);
  }
};

// Запускаем процесс
processFile();
