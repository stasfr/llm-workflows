import { MilvusClient, DataType } from '@zilliz/milvus2-sdk-node';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// --- Конфигурация ---
const MILVUS_ADDRESS = "192.168.1.103:19530";
const COLLECTION_NAME = "test_rag_collection_with_date";
const VECTOR_DIMENSION = 1024;

// Данные для сервиса эмбеддингов
const EMBEDDING_SERVICE_URL = 'http://192.168.1.103:1234/v1/embeddings';
const MODEL_NAME = 'text-embedding-intfloat-multilingual-e5-large-instruct';

const REQUEST_TIMEOUT_MS = 120000;
const BATCH_SIZE = 50;

// Путь к файлу
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_FILE_PATH = path.join(__dirname, 'plain_data', 'output.json');

// Функция getEmbedding с увеличенным таймаутом
async function getEmbedding(text) {
    if (typeof text !== 'string' || text.trim() === '') {
        console.warn("Пропущена пустая или некорректная строка для создания эмбеддинга.");
        return null;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
        const payload = { model: MODEL_NAME, input: text };
        const response = await fetch(EMBEDDING_SERVICE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal,
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`Failed to get embedding for "${text.substring(0, 50)}...": ${response.statusText}. Body: ${errorBody}`);
        }

        const data = await response.json();
        return data.data[0].embedding;
    } finally {
        clearTimeout(timeoutId);
    }
}

// --- Основная функция ---
async function main() {
    let sourceData;
    try {
        console.log(`--- Читаем данные из файла: ${DATA_FILE_PATH} ---`);
        const fileContent = await fs.readFile(DATA_FILE_PATH, 'utf-8');
        sourceData = JSON.parse(fileContent).posts;

        if (!Array.isArray(sourceData)) {
            throw new Error('Ключ "posts" в JSON-файле не найден или не является массивом.');
        }
        console.log(`--- Успешно загружено ${sourceData.length} записей из файла ---`);
    } catch (error) {
        console.error(`Критическая ошибка при чтении файла: ${error.message}`);
        return;
    }

    if (!sourceData || sourceData.length === 0) {
        console.log("Файл с данными пуст. Работа завершена.");
        return;
    }

    const milvusClient = new MilvusClient({ address: MILVUS_ADDRESS, timeout: 60000 });
    console.log(`--- Подключаемся к Milvus по адресу ${MILVUS_ADDRESS} ---`);

    try {
        const hasCollection = await milvusClient.hasCollection({ collection_name: COLLECTION_NAME });

        if (!hasCollection.value) {
            console.log(`Коллекция "${COLLECTION_NAME}" не найдена. Создаем новую...`);
            await milvusClient.createCollection({
                collection_name: COLLECTION_NAME,
                fields: [
                    { name: "id", data_type: DataType.Int64, is_primary_key: true, autoID: true },
                    { name: "vector", data_type: DataType.FloatVector, dim: VECTOR_DIMENSION },
                    { name: "text", data_type: DataType.VarChar, max_length: 65535 },
                    { name: "date_str", data_type: DataType.VarChar, max_length: 100 },
                ],
            });
            console.log("Коллекция создана. Создаем индекс...");
            await milvusClient.createIndex({
                collection_name: COLLECTION_NAME,
                field_name: "vector",
                index_name: "vector_idx",
                index_type: "IVF_FLAT",
                metric_type: "L2",
                params: { nlist: 1024 },
            });
            console.log("Индекс успешно создан.");
        } else {
             console.log(`Коллекция "${COLLECTION_NAME}" уже существует.`);
        }

        console.log(`Загружаем коллекцию "${COLLECTION_NAME}" в память...`);
        await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });
        console.log("Коллекция успешно загружена.");

        // Обработка данных порциями (батчами)
        console.log(`Начинаем обработку и вставку ${sourceData.length} записей порциями по ${BATCH_SIZE}...`);
        let totalInserted = 0;

        for (let i = 0; i < sourceData.length; i += BATCH_SIZE) {
            const batch = sourceData.slice(i, i + BATCH_SIZE);
            const currentPortion = Math.floor(i / BATCH_SIZE) + 1;
            const totalPortions = Math.ceil(sourceData.length / BATCH_SIZE);
            console.log(`--- Обработка порции ${currentPortion} / ${totalPortions} (записи с ${i+1} по ${i + batch.length}) ---`);

            const embeddingPromises = batch.map(item => getEmbedding(item.text));
            const embeddings = await Promise.all(embeddingPromises);

            // Создаем массив для вставки ТОЛЬКО для этой порции
            const batchToInsert = [];
            for (let j = 0; j < batch.length; j++) {
                if (embeddings[j]) {
                    batchToInsert.push({
                        vector: embeddings[j],
                        text: batch[j].text,
                        date_str: batch[j].date,
                    });
                }
            }

            // Если в порции есть что вставлять, вставляем немедленно
            if (batchToInsert.length > 0) {
                const result = await milvusClient.insert({
                    collection_name: COLLECTION_NAME,
                    fields_data: batchToInsert,
                });
                if (result.status.error_code !== 'Success') {
                    throw new Error(`Ошибка вставки порции ${currentPortion}: ${result.status.reason}`);
                }
                totalInserted += result.succ_index.length;
                console.log(`--- Порция ${currentPortion} успешно вставлена. Всего вставлено: ${totalInserted} ---`);
            } else {
                console.log(`--- В порции ${currentPortion} нет данных для вставки (возможно, все тексты были пустыми). ---`);
            }
        }

        console.log(`Всего вставлено ${totalInserted} записей. Фиксируем данные на диске...`);
          await milvusClient.flush({ collection_names: [COLLECTION_NAME] });
          console.log("Данные успешно зафиксированы и готовы к поиску.");

    } catch (error) {
        console.error("--- Произошла критическая ошибка! ---");
        console.error(error);
    } finally {
        if (milvusClient) {
            console.log(`Освобождаем коллекцию "${COLLECTION_NAME}" из памяти...`);
            await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
            console.log("--- Работа завершена ---");
        }
    }
}

main();
