import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  VECTOR_DIMENSION,
  LM_STUDIO_URL,
  EMBEDDING_MODEL_NAME,
  CHAT_COMPLETION_MODEL_NAME,
  BATCH_SIZE,
  FILTERED_FILE,
} from '@/config.js';

import { chain } from 'stream-chain';
import parser from 'stream-json';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { MilvusClient, DataType, type RowData } from '@zilliz/milvus2-sdk-node';
import { createReadStream, readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve as resolvePath } from 'path';

import { sendTelegramMessage } from './telegram.js';
import { type IEmbeddingRequest, type IChatCompletionRequest, IContentType } from './types/request.js';
import type { IEmbeddingResponse, IChatCompletionResponse } from './types/response.js';
import type { ParsedTelegramData } from './types/data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function getEmbedding(text: string): Promise<{
  embedding: number[];
  usage: {
    prompt_tokens: number;
    total_tokens: number
  }
} | null> {
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

  return {
    embedding: data.data[0].embedding,
    usage: data.usage,
  };
}

async function getChatCompletion(image: string): Promise<{
  content: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  }
} | null> {
  const payload: IChatCompletionRequest = {
    model: CHAT_COMPLETION_MODEL_NAME,
    messages: [
      {
        role: 'system',
        content: `
        Твоя задача — составить короткое и объективное описание изображения (1-2 предложения).

        Правила:
        1.  Описывай только факты: кто/что изображено, что делает, где находится.
        2.  Начинай ответ сразу с описания. Никаких приветствий и фраз вроде "На этом фото...".
        3.  Не анализируй настроение, эмоции или атмосферу.
        4.  Игнорируй любые логотипы и надписи, особенно "инстажелдор".
        5.  Отвечай строго на русском языке.

        Примеры правильного ответа:
        - Люди отдыхают на песчаном пляже у моря.
        - Рыжая собака породы корги лежит на зеленой траве.
        - Два человека в камуфляже ведут перестрелку на городской улице.
        `,
      },
      {
        role: 'user',
        content: [
          {
            type: IContentType.Image,
            image_url: { url: image },
          },
        ],
      },
    ],
    temperature: 1,
  };

  const response = await fetch(`${LM_STUDIO_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    console.error(`Failed to get chat completion: ${response.statusText}`);

    return null;
  }

  const data = await response.json() as IChatCompletionResponse;

  return {
    content: data.choices[0].message.content,
    usage: data.usage,
  };
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
        name: 'post_id',
        data_type: DataType.Int64,
      },
      {
        name: 'text',
        data_type: DataType.VarChar,
        max_length: 65535,
      },
      {
        name: 'date',
        data_type: DataType.VarChar,
        max_length: 65535,
      },
      {
        name: 'image_process_usage',
        data_type: DataType.JSON,
      },
      {
        name: 'embedding_usage',
        data_type: DataType.JSON,
      },
    ],
  });
  await milvusClient.createIndex({
    collection_name: COLLECTION_NAME,
    field_name: 'vector',
    index_name: 'vector_idx',
    index_type: 'FLAT',
    metric_type: 'IP',
  });
}

interface ProcessedPostData {
  embeddingData: {
    embedding: number[];
    usage: {
      prompt_tokens: number;
      total_tokens: number
    };
  } | null;
  imageUsage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number
  } | null;
}

async function processPost(post: ParsedTelegramData, withImages: boolean): Promise<ProcessedPostData | null> {
  let imageDescription = '';
  let imageUsage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number
  } | null = null;

  if (post.photo && withImages) {
    const imagePath = resolvePath(__dirname, '..', 'plain_data', 'tg', post.photo);

    try {
      const imageBuffer = readFileSync(imagePath);
      const base64Image = imageBuffer.toString('base64');
      const imageDataUrl = `data:image/jpeg;base64,${base64Image}`;
      const completionData = await getChatCompletion(imageDataUrl);

      if (completionData) {
        imageDescription = completionData.content;
        imageUsage = completionData.usage;
      }
    } catch (error) {
      console.error(`Failed to process image ${post.photo}:`, error);
    }
  }

  const postText = `
      ${post.text ?? ''}
      ${imageDescription}
    `;

  const embeddingData = await getEmbedding(postText);

  if (!embeddingData) {
    return null;
  }

  return {
    embeddingData,
    imageUsage,
  };
}

export async function getPostsEmbeddings(count: number, withImages: boolean): Promise<void> {
  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });
  let firstIteration = true;
  const batchTimes: number[] = [];

  try {
    const hasCollection = await milvusClient.hasCollection({ collection_name: COLLECTION_NAME });

    if (!hasCollection.value) {
      await createMilvusCollection(milvusClient);
    }

    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });

    const isParsedTelegramData = (value: unknown): value is ParsedTelegramData => {
      if (value === null || typeof value !== 'object') {
        return false;
      }

      return 'id' in value && 'date' in value && ('text' in value || 'photo' in value);
    };

    const pipeline = chain([
      createReadStream(FILTERED_FILE),
      parser(),
      new StreamArray(),
    ]);

    let batch: ParsedTelegramData[] = [];
    let processedCount = 0;
    const processBatch = async (posts: ParsedTelegramData[]): Promise<void> => {
      if (posts.length === 0) {
        return;
      }

      const batchStartTime = Date.now();

      processedCount += posts.length;

      if (firstIteration) {
        const message = `-- обработка ${processedCount.toString()}/${count.toString()} записей. Вычисляем примерное время... --`;
        console.log(message);
        void sendTelegramMessage(message);
        firstIteration = false;
      } else {
        const averageTime = batchTimes.reduce((a, b) => a + b, 0) / batchTimes.length;
        const batchesRemaining = (count - processedCount) / BATCH_SIZE;
        const timeRemaining = new Date(batchesRemaining * averageTime);
        const hours = timeRemaining.getUTCHours();
        const minutes = timeRemaining.getUTCMinutes();
        const seconds = timeRemaining.getUTCSeconds();

        const message = `-- обработка ${processedCount.toString()}/${count.toString()}. время до окончания: ${hours.toString()}ч ${minutes.toString()}м ${seconds.toString()}с  --`;
        console.log(message);
        void sendTelegramMessage(message);
      }

      const processedData = await Promise.all(posts.map((post) => processPost(post, withImages)));
      const dataToInsert: RowData[] = [];

      for (let i = 0; i < posts.length; i++) {
        const post = posts[i];
        const data = processedData[i];

        if (data?.embeddingData) {
          const text = Array.isArray(post.text)
            ? post.text.join('\n')
            : (post.text ?? '');

          dataToInsert.push({
            post_id: post.id,
            date: post.date,
            text,
            vector: data.embeddingData.embedding,
            embedding_usage: data.embeddingData.usage ?? {
              prompt_tokens: 0,
              total_tokens: 0,
            },
            image_process_usage: data.imageUsage ?? {
              prompt_tokens: 0,
              completion_tokens: 0,
              total_tokens: 0,
            },
          });
        }
      }

      if (dataToInsert.length > 0) {
        await milvusClient.insert({
          collection_name: COLLECTION_NAME,
          fields_data: dataToInsert,
        });
      }

      const batchEndTime = Date.now();
      batchTimes.push(batchEndTime - batchStartTime);
    };

    try {
      for await (const { value } of pipeline) {
        if (!isParsedTelegramData(value)) {
          continue;
        }

        batch.push(value);

        if (batch.length >= BATCH_SIZE) {
          await processBatch(batch);
          batch = [];
        }
      }

      if (batch.length > 0) {
        await processBatch(batch);
      }
    } catch (err) {
      console.error('Stream processing error:', err);
      throw err;
    }

    await milvusClient.flush({ collection_names: [COLLECTION_NAME] });
  } catch (error: unknown) {
    const errorMessage = '--- Произошла критическая ошибка! ---';
    console.error(errorMessage);
    console.error(error);
    void sendTelegramMessage(`${errorMessage}\n${error instanceof Error
      ? error.message
      : String(error)}`);
  } finally {
    if (milvusClient) {
      console.log(`Освобождаем коллекцию "${COLLECTION_NAME}" из памяти...`);
      await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
      console.log('--- Работа завершена ---');
    }
  }
}
