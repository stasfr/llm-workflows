import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import fs from 'fs/promises';
import { createReadStream } from 'fs';

import type { MappedTelegramData, ParsedTelegramData } from './types/data.js';
import { MessageType, type Message, type TgData } from './types/telegram.js';

const RESULT_FILE = 'plain_data/tg/result.json';
const MAPPED_FILE = 'plain_data/mappedMessages.json';
const PARSED_FILE = 'plain_data/parsedMessages.json';

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

export const mapPlainTelegramResultData = async (): Promise<void> => {
  const isMessage = (value: unknown): value is Message => {
    if (value === null || typeof value !== 'object') {
      return false;
    }

    return 'type' in value && value.type === MessageType.Message;
  };

  const pipeline = chain([
    createReadStream(RESULT_FILE),
    parser(),
    new Pick({ filter: 'messages' }),
    new StreamArray(),
  ]);

  try {
    const result: MappedTelegramData[] = [];

    for await (const { value } of pipeline) {
      if (isMessage(value)) {
        const parsedData: MappedTelegramData = {
          id: value.id,
          date: value.date,
          date_unixtime: value.date_unixtime,
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
    await fs.writeFile(MAPPED_FILE, outputString);

    console.log(`✅ Файл ${MAPPED_FILE} успешно создан!`);
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
};

export const parseMappedTelegramData = async (): Promise<void> => {
  const isMappedTelegramData = (value: unknown): value is MappedTelegramData => {
    if (value === null || typeof value !== 'object') {
      return false;
    }

    return 'id' in value && 'date' in value && 'date_unixtime' in value && 'text_entities' in value;
  };

  const pipeline = chain([
    createReadStream(MAPPED_FILE),
    parser(),
    new StreamArray(),
  ]);

  try {
    const result: ParsedTelegramData[] = [];

    for await (const { value } of pipeline) {
      if (isMappedTelegramData(value)) {
        const mappedTelegramData = value;

        const text = mappedTelegramData.text_entities.map((entity) => entity.text)
          .join('');

        const parsedTelegramData: ParsedTelegramData = {
          id: mappedTelegramData.id,
          date: mappedTelegramData.date,
          date_unixtime: mappedTelegramData.date_unixtime,
          photo: mappedTelegramData.photo,
          file: mappedTelegramData.file,
          file_name: mappedTelegramData.file_name,
          mime_type: mappedTelegramData.mime_type,
          text,
        };

        result.push(parsedTelegramData);
      }
    }

    const outputString = JSON.stringify(result, null, 2);
    await fs.writeFile(PARSED_FILE, outputString);

    console.log(`✅ Файл ${PARSED_FILE} успешно создан!`);
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
};
