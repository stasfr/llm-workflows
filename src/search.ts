import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  EMBEDDING_SERVICE_URL,
  EMBEDDING_MODEL_NAME,
  QUERY_TEXT,
} from '@/config.js';

import { MilvusClient } from '@zilliz/milvus2-sdk-node';

interface EmbeddingResponse { data: { embedding: number[]; }[]; }

interface SearchResult {
  score: number;
  text: string;
  id: string;
}

/**
 * Получает эмбеддинг для заданного текста.
 * @param text - Входной текст.
 * @returns - Вектор эмбеддинга.
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

/**
 * Основная функция для выполнения поиска в Milvus.
 */
export async function searchText(): Promise<void> {
  console.log(`--- Запрос поиска: ${QUERY_TEXT} ---`);

  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });

  try {
    const queryVector: number[] = await getEmbedding(QUERY_TEXT);

    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });

    const searchParams = { nprobe: 16 };

    const searchResults = await milvusClient.search({
      collection_name: COLLECTION_NAME,
      vector: queryVector,
      topk: 3,
      params: searchParams,
    });

    console.log('\n--- Результаты поиска (от самого похожего к наименее) ---');

    if (searchResults.results.length > 0) {
      (searchResults.results as SearchResult[]).forEach((result) => {
        console.log(`- Score: ${result.score.toFixed(4)} (Чем меньше, тем лучше для L2)`);
        console.log(`  Текст: "${result.text}"`);
        console.log(`  ID: ${result.id}\n`);
      });
    } else {
      console.log('Ничего не найдено.');
    }
  } catch (error: unknown) {
    console.error('--- Произошла критическая ошибка! ---');
    console.error(error);
  } finally {
    await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
  }
}
