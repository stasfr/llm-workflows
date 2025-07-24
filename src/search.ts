import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  LM_STUDIO_URL,
  EMBEDDING_MODEL_NAME,
  QUERY_TEXT,
} from '@/config.js';

import { MilvusClient, type RowData } from '@zilliz/milvus2-sdk-node';
import type { IEmbeddingRequest } from './types/request.js';
import type { IEmbeddingResponse } from './types/response.js';

interface SearchResult extends RowData {
  score: number;
  text: string;
  post_id: number;
  date: string;
}

async function getEmbedding(text: string): Promise<number[] | null> {
  const payload: IEmbeddingRequest = {
    model: EMBEDDING_MODEL_NAME,
    input: [text],
  };

  const response = await fetch(`${LM_STUDIO_URL}/v1/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    console.error(`Failed to get embedding for "${text}": ${response.statusText}`);

    return null;
  }

  const data = await response.json() as IEmbeddingResponse;

  return data.data[0].embedding;
}

export async function searchText(): Promise<void> {
  console.log(`--- Запрос поиска: ${QUERY_TEXT} ---`);

  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });

  try {
    const queryVector = await getEmbedding(QUERY_TEXT);

    if (!queryVector) {
      console.error('Не удалось получить вектор для запроса.');

      return;
    }

    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });

    const searchParams = { nprobe: 16 };

    const searchResults = await milvusClient.search({
      collection_name: COLLECTION_NAME,
      vector: queryVector,
      topk: 5,
      params: searchParams,
      output_fields: ['text', 'post_id', 'date'],
    });

    console.log('\n--- Результаты поиска (от самого похожего к наименее) ---');

    if (searchResults.results.length > 0) {
      (searchResults.results as unknown as SearchResult[]).forEach((result) => {
        console.log(`- Score: ${result.score.toFixed(4)} (Чем меньше, тем лучше для L2)`);
        console.log(`  Post ID: ${result.post_id.toString()}`);
        console.log(`  Date: ${result.date}`);
        console.log(`  Текст: "${result.text}"\n`);
      });
    } else {
      console.log('Ничего не найдено.');
    }
  } catch (error: unknown) {
    console.error('--- Произошла критическая ошибка! ---');
    console.error(error);
  } finally {
    if (milvusClient) {
      await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
    }
  }
}
