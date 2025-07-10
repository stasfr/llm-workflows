import { MilvusClient } from '@zilliz/milvus2-sdk-node';
import { promises as fs } from 'fs'; // Импортируем модуль для работы с файлами

// --- Конфигурация (должна быть такая же, как в index.js) ---
const MILVUS_ADDRESS = '192.168.1.103:19530';
const COLLECTION_NAME = 'test_rag_collection_with_date';

// Данные для сервиса эмбеддингов
const EMBEDDING_SERVICE_URL = 'http://192.168.1.103:1234/v1/embeddings';
const MODEL_NAME = 'text-embedding-intfloat-multilingual-e5-large-instruct';

// --- ТЕКСТ, ПО КОТОРОМУ БУДЕМ ИСКАТЬ ---
const QUERY_TEXT = 'Павлино, стрельба, убийство';
// Можете поменять на "Кто такая Афина?" или любой другой для теста

// Функция для получения эмбеддинга (такая же, как в index.js)
async function getEmbedding(text) {
  const payload = {
    model: MODEL_NAME,
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

  const data = await response.json();

  return data.data[0].embedding;
}

// --- Основная функция поиска ---
async function main() {
  console.log(`--- Запускаем поиск по коллекции "${COLLECTION_NAME}" ---`);
  console.log(`Текст запроса: "${QUERY_TEXT}"`);

  // 1. Инициализируем клиент с таймаутом
  const milvusClient = new MilvusClient({
    address: MILVUS_ADDRESS,
    timeout: 30000,
  });

  try {
    // 2. Получаем эмбеддинг для нашего поискового запроса
    console.log('Получаем вектор для поискового запроса...');
    const queryVector = await getEmbedding(QUERY_TEXT);
    console.log('Вектор успешно получен.');

    // 3. Загружаем коллекцию в память перед поиском
    console.log('Загружаем коллекцию в память...');
    await milvusClient.loadCollection({ collection_name: COLLECTION_NAME });
    console.log('Коллекция загружена.');

    // 4. Выполняем поиск
    const searchParams = {
      // Параметры для типа индекса IVF_FLAT. nprobe - сколько "кластеров" проверять.
      // Больше nprobe -> точнее, но медленнее. 16 - хорошее начало.
      nprobe: 16,
    };

    console.log('Выполняем поиск похожих векторов...');
    const searchResults = await milvusClient.search({
      collection_name: COLLECTION_NAME,
      vector: queryVector,
      topk: 3, // Искать 3 самых похожих результата
      output_fields: ['id', 'text', 'date_str'], // Какие поля вернуть вместе с результатом
      params: searchParams,
    });

    // 5. Обрабатываем и выводим результаты в консоль
    console.log('\n--- Результаты поиска (от самого похожего к наименее) ---');

    if (searchResults.results.length > 0) {
      searchResults.results.forEach((result) => {
        console.log(`- Score: ${result.score.toFixed(4)} (Чем меньше, тем лучше для L2)`);
        console.log(`  Текст: "${result.string}"`);
        console.log(`  ID: ${result.id}\n`);
      });
    } else {
      console.log('Ничего не найдено.');
    }

    // 6. Сохраняем полный ответ в JSON файл
    const outputPath = 'search_results.json';
    await fs.writeFile(outputPath, JSON.stringify(searchResults, null, 2));
    console.log(`--- Полный ответ от Milvus сохранен в файл: ${outputPath} ---`);
  } catch (error) {
    console.error('--- Произошла критическая ошибка! ---');
    console.error(error);
  } finally {
    // 7. Освобождаем ресурсы
    console.log('Освобождаем коллекцию из памяти...');
    await milvusClient.releaseCollection({ collection_name: COLLECTION_NAME });
    console.log('--- Работа завершена ---');
  }
}

main();
