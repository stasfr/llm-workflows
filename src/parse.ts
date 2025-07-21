import {
  RESULT_FILE,
  MAPPED_FILE,
  PARSED_FILE,
  FILTERED_FILE,
} from './config.js';

import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import fs from 'fs/promises';
import { createReadStream } from 'fs';

import type { MappedTelegramData, ParsedTelegramData } from './types/data.js';
import { MessageType, type Message, type TgData } from './types/telegram.js';

export const serviceParser = async (): Promise<Set<string>> => {
  const ServiceSet = new Set<string>();

  const rawData = await fs.readFile(RESULT_FILE, 'utf8');
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
          text_entities: value.text_entities,
          photo: value.photo,
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

    return 'id' in value && 'date' in value && 'text_entities' in value;
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
        if (value.text_entities.length > 0 || value.photo) {
          const text = value.text_entities.map((entity) => entity.text)
            .join('');

          const parsedTelegramData: ParsedTelegramData = {
            id: value.id,
            date: value.date,
            photo: value.photo,
          };

          if (text) {
            parsedTelegramData.text = text;
          }

          result.push(parsedTelegramData);
        }
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

export async function filterParsedTelegramData(
  garbagePrasesList: string[],
  garbagePostsList: string[],
  exceptions: string[],
  wordOffset: number,
): Promise<[string, number][]> {
  const dataBaseMap = new Map<string, number>();

  const isParsedTelegramData = (value: unknown): value is ParsedTelegramData => {
    if (value === null || typeof value !== 'object') {
      return false;
    }

    return 'id' in value && 'date' in value && ('text' in value || 'photo' in value);
  };

  const pipeline = chain([
    createReadStream(PARSED_FILE),
    parser(),
    new StreamArray(),
  ]);

  try {
    const result: ParsedTelegramData[] = [];

    for await (const { value } of pipeline) {
      if (isParsedTelegramData(value)) {
        if (value.text) {
          // проверяем на рекламные посты
          const garbageSearchResult = garbagePostsList.some((garbage) => value.text?.includes(garbage));

          if (garbageSearchResult) {
            continue;
          }

          // очищаем от мусорных фраз
          let cleanStr = value.text;

          garbagePrasesList.forEach((garbage) => {
            cleanStr = cleanStr.replace(garbage, '');
          });

          cleanStr = cleanStr.trim();

          // делаем n gramm
          const normalizedStrArray = cleanStr
            .split(' ')
            .filter(Boolean);

          const firstIndex = 0;
          const lastIndex = normalizedStrArray.length - wordOffset;

          for (let index = firstIndex; index <= lastIndex; index++) {
            const entrySlice = normalizedStrArray.slice(index, index + wordOffset);
            const entryKey = entrySlice.join(' ');

            const currentCount = dataBaseMap.get(entryKey) ?? 0;
            dataBaseMap.set(entryKey, currentCount + 1);
          }

          // сохраняем "чистый" пост
          result.push({
            ...value,
            text: cleanStr,
          });
        }
      }
    }

    const outputString = JSON.stringify(result, null, 2);
    await fs.writeFile(FILTERED_FILE, outputString);

    console.log(`✅ Файл ${FILTERED_FILE} успешно создан!`);
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }

  const sortedDataBase = [...dataBaseMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10 + exceptions.length)
    .filter((entry) => !exceptions.includes(entry[0]));

  return sortedDataBase;
}
