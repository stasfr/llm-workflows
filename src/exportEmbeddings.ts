import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
} from '@/config.js';
import { MilvusClient } from '@zilliz/milvus2-sdk-node';
import fs from 'fs';
import { resolve as resolvePath, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OUTPUT_FILE = resolvePath(__dirname, '../plain_data', 'embeddings.json');
const BATCH_SIZE = 1000;

export async function exportEmbeddings() {
  console.log('--- Запуск экспорта эмбеддингов из Milvus ---');
  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });
  const writeStream = fs.createWriteStream(OUTPUT_FILE);

  writeStream.write('[');

  let totalRecords = 0;

  try {
    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });
    console.log(`Коллекция "${COLLECTION_NAME}" успешно загружена.`);

    let hasMore = true;
    let lastPostId = 0;
    let isFirstRecord = true;

    while (hasMore) {
      const results = await milvusClient.query({
        collection_name: COLLECTION_NAME,
        output_fields: ['post_id', 'text', 'vector'],
        limit: BATCH_SIZE,
        expr: `post_id > ${lastPostId.toString()}`,
        consistency_level: 3,
      });

      if (results.data.length > 0) {
        results.data.sort((a, b) => a.post_id - b.post_id);

        for (const record of results.data) {
          if (!isFirstRecord) {
            writeStream.write(',');
          }

          writeStream.write(JSON.stringify(record, null, 2));
          isFirstRecord = false;
        }

        totalRecords += results.data.length;
        lastPostId = results.data[results.data.length - 1].post_id as number;
        console.log(`Получено ${totalRecords.toString()} записей... Последний post_id: ${lastPostId.toString()}`);
      }

      if (results.data.length < BATCH_SIZE) {
        hasMore = false;
      }
    }

    writeStream.write(']');
    writeStream.end();

    console.log(`Всего сохранено ${totalRecords.toString()} записей.`);
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

// Для прямого запуска скрипта
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  exportEmbeddings();
}
