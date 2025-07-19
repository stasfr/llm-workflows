import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import fs from 'fs/promises';
import { createReadStream } from 'fs';

import type { ParsedData } from './types/data.js';
import { MessageType, type Message, type TgData } from './types/telegram.js';

const INPUT_FILE = 'plain_data/tg/result.json';
const OUTPUT_FILE = 'plain_data/parsedMessages.json';

type TextValue = string | { text: string } | (string | { text: string })[];

interface InputData { messages: Message[]; }

interface Post {
  text: string;
  date: string;
}

export const serviceParser = async (): Promise<Set<string>> => {
  const ServiceSet = new Set<string>();

  const rawData = await fs.readFile(INPUT_FILE, 'utf8');
  const inputJson = JSON.parse(rawData) as TgData;

  inputJson.messages.forEach((message) => {
    if (Array.isArray(message.text) && message.text.length) {
      message.text.forEach((text) => {
        if (typeof text === 'object') {
          const keys = JSON.stringify(Object.keys(text));

          ServiceSet.add(keys);
        }
      });
    }
  });

  return ServiceSet;
};

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

export const parsePlainTelegramTResultData = async (): Promise<void> => {
  const isMessage = (value: unknown): value is Message => {
    if (value === null || typeof value !== 'object') {
      return false;
    }

    return 'type' in value && value.type === MessageType.Message;
  };

  const pipeline = chain([
    createReadStream(INPUT_FILE),
    parser(),
    new Pick({ filter: 'messages' }),
    new StreamArray(),
  ]);

  try {
    const result: ParsedData[] = [];

    for await (const { value } of pipeline) {
      if (isMessage(value)) {
        const parsedData: ParsedData = {
          id: value.id,
          date: value.date,
          date_unixtime: value.date_unixtime,
          text: value.text,
          text_entities: value.text_entities,
          photo: value.photo,
          file: value.file,
          file_name: value.file_name,
          mime_type: value.mime_type,
        };

        result.push(parsedData);
      }
    }

    const outputString = JSON.stringify(result, null, 2);
    await fs.writeFile(OUTPUT_FILE, outputString);

    console.log(`✅ Файл ${OUTPUT_FILE} успешно создан!`);
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
};
