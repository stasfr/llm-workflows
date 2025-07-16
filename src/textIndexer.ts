import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { createReadStream } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const WORDS_OFFSET = 3;

const dbMap = new Map<string, number>();

interface Post { text: string; }

function isPost(value: unknown): value is Post {
  if (value === null || typeof value !== 'object') {
    return false;
  }

  return 'text' in value && typeof (value as { text: unknown }).text === 'string';
}

function buildNgramMap(sourceStr: string, dataBaseMap: Map<string, number>): void {
  const normalizedStr = sourceStr
    .replace(/[^а-яА-ЯёЁ ]/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.toLocaleLowerCase());

  const firstIndex = 0;
  const lastIndex = normalizedStr.length - WORDS_OFFSET;

  for (let index = firstIndex; index <= lastIndex; index++) {
    const entrySlice = normalizedStr.slice(index, index + WORDS_OFFSET);
    const entryKey = entrySlice.join(' ');

    const currentCount = dataBaseMap.get(entryKey) ?? 0;
    dataBaseMap.set(entryKey, currentCount + 1);
  }
}

async function processJsonStream(filePath: string): Promise<Map<string, number>> {
  const pipeline = chain([
    createReadStream(filePath),
    parser(),
    new Pick({ filter: 'posts' }),
    new StreamArray(),
  ]);

  return new Promise((resolve, reject) => {
    pipeline.on('data', ({ value }) => {
      if (isPost(value)) {
        buildNgramMap(value.text, dbMap);
      }
    });

    pipeline.on('end', () => {
      resolve(dbMap);
    });

    pipeline.on('error', (err) => {
      console.error('Stream processing error:', err);
      reject(err);
    });
  });
}

// --- Main execution ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dataFilePath = join(__dirname, '..', 'plain_data', 'posts.json');

console.log(`Starting to process file: ${dataFilePath}`);

processJsonStream(dataFilePath)
  .then((finalMap) => {
    console.log('Processing finished.');
    console.log('Total unique n-grams found:', finalMap.size);
    // Выведем топ-10 для примера
    const sortedMap = [...finalMap.entries()].sort((a, b) => b[1] - a[1]);
    console.log('Top 10 n-grams:');
    console.log(sortedMap.slice(0, 10));
  })
  .catch((error: unknown) => {
    console.error('Failed to process JSON stream.', error);
  });
