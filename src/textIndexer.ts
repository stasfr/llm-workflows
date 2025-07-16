import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { createReadStream } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const WORDS_OFFSET = 3;

// const normalizedDataBaseMap = new Map<string, number>();
const dataBaseMap = new Map<string, number>();

interface Post { text: string; }

function isPost(value: unknown): value is Post {
  if (value === null || typeof value !== 'object') {
    return false;
  }

  return 'text' in value && typeof (value as { text: unknown }).text === 'string';
}

const GARBAGE_LIST: string[] = [
  'Предложить новость ⬅️ \nРезервный канал ⬅️',
  'Заявка на вступление ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Заявка на вступление ⬅️\nПредложить новость - @zheldor_admin',
  'Вступить тут ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Ссылки для вступления тут ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Ссылки для вступления тут ⬅️\nНаш второй канал: ➡️ Барахолка ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'новость - @zheldor_admin',
];

const GARBAGE_POSTS_LIST: string[] = [
  'Маяковского 24а \nUP Луговая 14к1\nТел.',
  'Подписаться на канал ПУТЁВЫЙ✔\n- Кликнуть',
  'разрядов и званий\n-подготовка с НУЛЯ\n-профилактика',
  '79771106050',
  '8-926-319-96-17 Отрада Окна',
  'https://t.me/justeatsu',
  '+7(916)426-60-37',
];

function replaceGarbage(sourceStr: string): string {
  let cleanStr = sourceStr;

  if (!GARBAGE_LIST.length) {
    return cleanStr;
  }

  GARBAGE_LIST.forEach((garbage) => {
    cleanStr = cleanStr.replace(garbage, '');
  });

  return cleanStr;
}

function buildNgramMap(sourceStr: string, dataBaseMap: Map<string, number>): void {
  const postIsGarbage = GARBAGE_POSTS_LIST.some((garbage) => sourceStr.includes(garbage));

  if (postIsGarbage) {
    return;
  }

  const normalizedStr = replaceGarbage(sourceStr.trim())
    .split(' ')
    .filter(Boolean);

  const firstIndex = 0;
  const lastIndex = normalizedStr.length - WORDS_OFFSET;

  for (let index = firstIndex; index <= lastIndex; index++) {
    const entrySlice = normalizedStr.slice(index, index + WORDS_OFFSET);
    const entryKey = entrySlice.join(' ');

    const currentCount = dataBaseMap.get(entryKey) ?? 0;
    dataBaseMap.set(entryKey, currentCount + 1);
  }
}

// function buildNormalizedNgramMap(sourceStr: string, normalizedDataBaseMap: Map<string, number>): void {
//   const normalizedStr = sourceStr
//     .replace(/[^а-яА-ЯёЁ ]/g, ' ')
//     .trim()
//     .split(' ')
//     .filter(Boolean)
//     .map((word) => word.toLocaleLowerCase());

//   const firstIndex = 0;
//   const lastIndex = normalizedStr.length - WORDS_OFFSET;

//   for (let index = firstIndex; index <= lastIndex; index++) {
//     const entrySlice = normalizedStr.slice(index, index + WORDS_OFFSET);
//     const entryKey = entrySlice.join(' ');

//     const currentCount = normalizedDataBaseMap.get(entryKey) ?? 0;
//     normalizedDataBaseMap.set(entryKey, currentCount + 1);
//   }
// }

async function processJsonStream(filePath: string): Promise<Map<string, number>> {
  const pipeline = chain([
    createReadStream(filePath),
    parser(),
    new Pick({ filter: 'posts' }),
    new StreamArray(),
  ]);

  try {
    for await (const { value } of pipeline) {
      if (isPost(value)) {
        buildNgramMap(value.text, dataBaseMap);
        // buildNormalizedNgramMap(value.text, normalizedDataBaseMap);
      }
    }

    return dataBaseMap;
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
}

// --- Main execution ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dataFilePath = join(__dirname, '..', 'plain_data', 'posts.json');

export async function indexText(): Promise<[string, number][]> {
  const dataBaseMap = await processJsonStream(dataFilePath);

  const sortedDataBase = [...dataBaseMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  console.log('Top 10 n-grams:');
  console.log(sortedDataBase);

  return sortedDataBase;
}
