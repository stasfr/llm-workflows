import fs from 'fs/promises';

const INPUT_FILE = 'plain_data/input.json';
const OUTPUT_FILE = 'plain_data/output.json';

type TextValue = string | { text: string } | (string | { text: string })[];

interface Message {
  text: TextValue;
  date: string;
}

interface InputData { messages: Message[]; }

interface Post {
  text: string;
  date: string;
}

/**
 * Рекурсивно обрабатывает текстовые значения, если они в виде массива - конкатенирует
 * @param textValue - Входное значение текста.
 * @returns - Обработанная текстовая строка.
 */
const processText = (textValue: TextValue): string => {
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

/**
 * Преобразует сообщения в посты.
 * @param inputData - Входные данные с сообщениями.
 * @returns - Объект с постами.
 */
const transformMessagesToPosts = (inputData: InputData): Post[] => {
  if (!inputData || !Array.isArray(inputData.messages)) {
    console.error('Ошибка: Входной JSON не содержит массив \'messages\'.');

    return [];
  }

  const posts: Post[] = inputData.messages
    .map((message: Message) => {
      const processedText = processText(message.text);

      return {
        text: processedText,
        date: message.date,
      };
    })
    .filter((post: Post) => post.text.trim() !== '');

  return posts;
};

/**
 * Основная функция для обработки файла.
 */
const processFile = async (): Promise<void> => {
  const rawData = await fs.readFile(INPUT_FILE, 'utf8');
  const inputJson = JSON.parse(rawData) as InputData;

  const parsedPosts = transformMessagesToPosts(inputJson);
  const outputJson = { posts: parsedPosts };

  const outputString = JSON.stringify(outputJson, null, 2);
  await fs.writeFile(OUTPUT_FILE, outputString);
  console.log(`✅ Файл ${OUTPUT_FILE} успешно создан!`);
};

await processFile();
