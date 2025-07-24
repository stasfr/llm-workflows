import {
  MILVUS_ADDRESS,
  COLLECTION_NAME,
  VECTOR_DIMENSION,
  LM_STUDIO_URL,
  EMBEDDING_MODEL_NAME,
  CHAT_COMPLETION_MODEL_NAME,
  // BATCH_SIZE,
  FILTERED_FILE,
} from '@/config.js';

import { chain } from 'stream-chain';
import parser from 'stream-json';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { MilvusClient, DataType, type RowData } from '@zilliz/milvus2-sdk-node';
import { createReadStream, readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve as resolvePath } from 'path';

import { type IEmbeddingRequest, type IChatCompletionRequest, IContentType } from './types/request.js';
import type { IEmbeddingResponse, IChatCompletionResponse } from './types/response.js';
import type { ParsedTelegramData } from './types/data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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

async function getChatCompletion(image: string): Promise<string | null> {
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

  return data.choices[0].message.content;
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

async function processPost(post: ParsedTelegramData): Promise<number[] | null> {
  let imageDescription = '';

  if (post.photo) {
    const imagePath = resolvePath(__dirname, '..', 'plain_data', 'tg', post.photo);

    try {
      const imageBuffer = readFileSync(imagePath);
      const base64Image = imageBuffer.toString('base64');
      const imageDataUrl = `data:image/jpeg;base64,${base64Image}`;
      const completion = await getChatCompletion(imageDataUrl);

      if (completion) {
        imageDescription = completion;
      }
    } catch (error) {
      console.error(`Failed to process image ${post.photo}:`, error);
    }
  }

  const postText = `
      ${post.text ?? ''}
      ${imageDescription}
    `;

  return await getEmbedding(postText);
}

export async function getPostsEmbeddings(): Promise<void> {
  const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS });

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

    try {
      for await (const { value } of pipeline) {
        if (!isParsedTelegramData(value)) {
          continue;
        }

        const embedding = await processPost(value);

        if (embedding) {
          const text = Array.isArray(value.text)
            ? value.text.join('\n')
            : (value.text ?? '');

          const dataToInsert: RowData = {
            post_id: value.id,
            date: value.date,
            text,
            vector: embedding,
          };

          await milvusClient.insert({
            collection_name: COLLECTION_NAME,
            fields_data: [dataToInsert],
          });
        }
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
