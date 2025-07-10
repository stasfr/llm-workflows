import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  VECTOR_DIMENSION,
  EMBEDDING_SERVICE_URL,
  EMBEDDING_MODEL_NAME,
  BATCH_SIZE,
} from '@/config.js';

import { MilvusClient, DataType, type RowData } from '@zilliz/milvus2-sdk-node';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

interface Post {
  text: string;
  date: string;
}

interface EmbeddingResponse { data: { embedding: number[]; }[]; }

interface BatchData {
  vector: number[];
  text: string;
  date_str: string;
}

const __filename: string = fileURLToPath(import.meta.url);
const __dirname: string = path.dirname(__filename);
const DATA_FILE_PATH: string = path.join(__dirname, '..', 'plain_data', 'output.json');

/**
 * Получает эмбеддинг для заданного текста.
 * @param text - Входной текст.
 * @returns - Вектор эмбеддинга или null, если текст пустой.
 */
async function getEmbedding(text: string): Promise<number[]> {
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
    throw new Error(`Failed to get embedding for "${text}": ${response.statusText}`);
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
      {
        name: 'date_str',
        data_type: DataType.VarChar,
        max_length: 100,
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

/**
 * Основная функция для индексации данных в Milvus.
 */
async function main(): Promise<void> {
  let sourceData: Post[];

  try {
    console.log(`--- Читаем данные из файла: ${DATA_FILE_PATH} ---`);
    const fileContent = await fs.readFile(DATA_FILE_PATH, 'utf-8');
    const rawData = JSON.parse(fileContent) as { posts: Post[] };

    if (!rawData.posts) {
      throw new Error('Неверный формат файла');
    }

    sourceData = rawData.posts;

    if (!Array.isArray(sourceData)) {
      throw new Error('Ключ "posts" в JSON-файле не найден или не является массивом.');
    }

    console.log(`--- Успешно загружено ${String(sourceData.length)} записей из файла ---`);
  } catch (error: unknown) {
    console.error('Критическая ошибка при чтении файла: ', error);

    return;
  }

  if (!sourceData || sourceData.length === 0) {
    console.log('Файл с данными пуст. Работа завершена.');

    return;
  }

  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });

  try {
    const hasCollection = await milvusClient.hasCollection({ collection_name: COLLECTION_NAME });

    if (!hasCollection) {
      await createMilvusCollection(milvusClient);
    }

    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });

    console.log(`Начинаем обработку и вставку ${String(sourceData.length)} записей порциями по ${String(BATCH_SIZE)}...`);
    let totalInserted = 0;

    for (let i = 0; i < sourceData.length; i += BATCH_SIZE) {
      const batch: Post[] = sourceData.slice(i, i + BATCH_SIZE);
      const currentPortion: number = Math.floor(i / BATCH_SIZE) + 1;
      const totalPortions: number = Math.ceil(sourceData.length / BATCH_SIZE);
      console.log(`Обработка порции ${String(currentPortion)} / ${String(totalPortions)} (записи с ${String(i + 1)} по ${String(i + batch.length)})`);

      const embeddingPromises: Promise<number[] | null>[] = batch.map((item) => getEmbedding(item.text));
      const embeddings: (number[] | null)[] = await Promise.all(embeddingPromises);
      const filteredEmbeddings = embeddings.filter((embedding) => embedding !== null);

      const batchToInsert: BatchData[] = [];
      for (let j = 0; j < filteredEmbeddings.length; j++) {
        if (filteredEmbeddings[j]) {
          batchToInsert.push({
            vector: filteredEmbeddings[j],
            text: batch[j].text,
            date_str: batch[j].date,
          });
        }
      }

      if (batchToInsert.length > 0) {
        const result = await milvusClient.insert({
          collection_name: COLLECTION_NAME,
          fields_data: batchToInsert as unknown as RowData[],
        });

        if (result.status.error_code !== 'Success') {
          throw new Error(`Ошибка вставки порции ${String(currentPortion)}: ${result.status.reason}`);
        }

        totalInserted += result.succ_index.length;
        console.log(`--- Порция ${String(currentPortion)} успешно вставлена. Всего вставлено: ${String(totalInserted)} ---`);
      } else {
        console.log(`--- В порции ${String(currentPortion)} нет данных для вставки (возможно, все тексты были пустыми). ---`);
      }
    }

    console.log(`Всего вставлено ${String(totalInserted)} записей. Фиксируем данные на диске...`);
    await milvusClient.flush({ collection_names: [COLLECTION_NAME] });
    console.log('Данные успешно зафиксированы и готовы к поиску.');
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
