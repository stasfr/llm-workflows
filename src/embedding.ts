import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  VECTOR_DIMENSION,
  EMBEDDING_SERVICE_URL,
  EMBEDDING_MODEL_NAME,
  BATCH_SIZE,
} from '@/config.js';

import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { MilvusClient, DataType, type RowData } from '@zilliz/milvus2-sdk-node';
import { createReadStream } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

import { normalizeSourceStr, isPost } from './textIndexer.js';

export interface Post {
  text: string;
  date: string;
}

export interface CompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: [
    {
      index: number;
      logprobs: unknown;
      finish_reason: string;
      message: {
        role: string;
        content: string;
      }
    },
  ];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  stats: unknown;
  system_fingerprint: string;
}

export interface EmbeddingResponse {
  object: string;
  data: {
    object: string;
    embedding: number[];
    index: number;
  }[];
  model: string;
  usage: {
    prompt_tokens: number;
    total_tokens: number;
  }
}

export interface BatchData {
  vector: number[];
  text: string;
}

/**
 * Получает эмбеддинг для заданного текста.
 * @param text - Входной текст.
 * @returns - Вектор эмбеддинга или null, если текст пустой.
 */
async function getEmbedding(text: string): Promise<number[] | null> {
  const payload = {
    model: EMBEDDING_MODEL_NAME,
    input: text,
  };

  const response = await fetch(EMBEDDING_SERVICE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    console.error(`Failed to get embedding for "${text}": ${response.statusText}`);

    return null;
  }

  const data = await response.json() as EmbeddingResponse;

  return data.data[0].embedding;
}

async function createMilvusCollection(milvusClient: MilvusClient): Promise<void> {
  await milvusClient.createCollection({
    collection_name: COLLECTION_NAME,
    fields: [
      {
        name: 'id',
        data_type: DataType.Int64,
        is_primary_key: true,
        autoID: true,
      },
      {
        name: 'vector',
        data_type: DataType.FloatVector,
        dim: VECTOR_DIMENSION,
      },
      {
        name: 'text',
        data_type: DataType.VarChar,
        max_length: 65535,
      },
    ],
  });
  await milvusClient.createIndex({
    collection_name: COLLECTION_NAME,
    field_name: 'vector',
    index_name: 'vector_idx',
    index_type: 'IVF_FLAT',
    metric_type: 'L2',
    params: { nlist: 1024 },
  });
}

async function main(): Promise<void> {
  const __filename: string = fileURLToPath(import.meta.url);
  const __dirname: string = dirname(__filename);
  const DATA_FILE_PATH: string = join(__dirname, '..', 'plain_data', 'posts.json');

  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });

  try {
    const hasCollection = await milvusClient.hasCollection({ collection_name: COLLECTION_NAME });

    if (!hasCollection) {
      await createMilvusCollection(milvusClient);
    }

    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });

    const pipeline = chain([
      createReadStream(DATA_FILE_PATH),
      parser(),
      new Pick({ filter: 'posts' }),
      new StreamArray(),
    ]);

    const processAndInsertBatch = async (posts: Post[]): Promise<void> => {
      const texts = posts
        .map((p) => normalizeSourceStr(p.text))
        .filter((text): text is string => !!text);

      if (texts.length === 0) return;

      console.log(`Получаем эмбеддинги для ${texts.length.toString()} текстов...`);
      const embeddings = await Promise.all(texts.map(getEmbedding));

      const batchData: BatchData[] = [];
      embeddings.forEach((embedding, index) => {
        if (embedding) {
          batchData.push({
            vector: embedding,
            text: texts[index],
          });
        }
      });

      if (batchData.length > 0) {
        console.log(`Вставляем пакет из ${batchData.length.toString()} элементов...`);
        const result = await milvusClient.insert({
          collection_name: COLLECTION_NAME,
          fields_data: batchData as unknown as RowData[],
        });

        if (result.status.error_code !== 'Success') {
          console.error(`Ошибка вставки порции: ${result.status.reason}`);
        }
      }
    };

    try {
      let postsBatch: Post[] = [];
      for await (const { value } of pipeline) {
        if (isPost(value)) {
          postsBatch.push(value);
        }

        if (postsBatch.length >= BATCH_SIZE) {
          await processAndInsertBatch(postsBatch);
          postsBatch = [];
        }
      }

      if (postsBatch.length > 0) {
        await processAndInsertBatch(postsBatch);
      }
    } catch (err) {
      console.error('Stream processing error:', err);
      throw err;
    }

    await milvusClient.flush({ collection_names: [COLLECTION_NAME] });
  } catch (error: unknown) {
    console.error('--- Произошла критическая ошибка! ---');
    console.error(error);
  } finally {
    if (milvusClient) {
      console.log(`Освобождаем коллекцию "${COLLECTION_NAME}" из памяти...`);
      await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
      console.log('--- Работа завершена ---');
    }
  }
}

await main();
