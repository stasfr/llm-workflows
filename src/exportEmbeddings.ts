import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
} from '@/config.js';
import { MilvusClient, type RowData } from '@zilliz/milvus2-sdk-node';
import fs from 'fs/promises';
import { resolve as resolvePath, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OUTPUT_FILE = resolvePath(__dirname, '../plain_data', 'embeddings.json');
const BATCH_SIZE = 1000;

export async function exportEmbeddings() {
  console.log('--- Запуск экспорта эмбеддингов из Milvus ---');
  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });
  const allData: RowData[] = [];

  try {
    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });
    console.log(`Коллекция "${COLLECTION_NAME}" успешно загружена.`);

    let offset = 0;
    let hasMore = true;

    while (hasMore) {
      const results = await milvusClient.query({
        collection_name: COLLECTION_NAME,
        output_fields: ['post_id', 'text', 'vector'],
        limit: BATCH_SIZE,
        offset,
      });

      if (results.data.length > 0) {
        allData.push(...results.data);
        offset += results.data.length;
        console.log(`Получено ${allData.length.toString()} записей...`);
      }

      if (results.data.length < BATCH_SIZE) {
        hasMore = false;
      }
    }

    console.log(`Всего получено ${allData.length.toString()} записей.`);

    const outputString = JSON.stringify(allData, null, 2);
    await fs.writeFile(OUTPUT_FILE, outputString);

    console.log(`✅ Эмбеддинги успешно сохранены в файл ${OUTPUT_FILE}`);
  } catch (error) {
    console.error('--- Произошла критическая ошибка во время экспорта! ---');
    console.error(error);
  } finally {
    if (milvusClient) {
      await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
      console.log(`Коллекция "${COLLECTION_NAME}" освобождена.`);
    }

    console.log('--- Работа завершена ---');
  }
}
