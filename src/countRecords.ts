import { createReadStream } from 'fs';
import { chain } from 'stream-chain';
import parser from 'stream-json';
import StreamArray from 'stream-json/streamers/StreamArray.js';
import { FILTERED_FILE } from '@/config.js';

export async function countRecords(): Promise<number | null> {
  let count = 0;
  const pipeline = chain([
    createReadStream(FILTERED_FILE),
    parser(),
    new StreamArray(),
  ]);

  try {
    for await (const _ of pipeline) {
      count++;
    }

    return count;
  } catch (err) {
    console.error('Error counting records:', err);

    return null;
  }
}
