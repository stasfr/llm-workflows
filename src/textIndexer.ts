import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { createReadStream } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const WORDS_OFFSET = 3;

const normalizedDataBaseMap = new Map<string, number>();
const dataBaseMap = new Map<string, number>();

interface Post { text: string; }

function isPost(value: unknown): value is Post {
  if (value === null || typeof value !== 'object') {
    return false;
  }

  return 'text' in value && typeof (value as { text: unknown }).text === 'string';
}

function buildNgramMap(sourceStr: string, dataBaseMap: Map<string, number>): void {
  const normalizedStr = sourceStr
    .replace(/[\n]/g, ' ')
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

function buildNormalizedNgramMap(sourceStr: string, normalizedDataBaseMap: Map<string, number>): void {
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

    const currentCount = normalizedDataBaseMap.get(entryKey) ?? 0;
    normalizedDataBaseMap.set(entryKey, currentCount + 1);
  }
}

async function processJsonStream(filePath: string): Promise<Map<string, number>[]> {
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
        buildNormalizedNgramMap(value.text, normalizedDataBaseMap);
      }
    }

    return [dataBaseMap, normalizedDataBaseMap];
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
}

// --- Main execution ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dataFilePath = join(__dirname, '..', 'plain_data', 'posts.json');

async function main(): Promise<void> {
  const [dataBaseMap, normalizedDataBaseMap] = await processJsonStream(dataFilePath);

  console.log('Top 10 n-grams:');
  console.log([...dataBaseMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10));

  console.log('Top 10 n-grams:');
  console.log([...normalizedDataBaseMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10));
}

void main();
