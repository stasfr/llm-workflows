import http from 'http';

import { PORT } from './config.js';
import {
  serviceParser,
  mapPlainTelegramResultData,
  parseMappedTelegramData,
  filterParsedTelegramData,
} from './parse.js';

const requestHandler = async (request: http.IncomingMessage, response: http.ServerResponse) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, POST, GET',
    'Access-Control-Max-Age': 2592000, // 30 days
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };

  if (request.method === 'OPTIONS') {
    response.writeHead(204, headers);
    response.end();

    return;
  }

  try {
    const { url, method } = request;

    if (method === 'GET' && url === '/service-parser') {
      const result = await serviceParser();
      console.log(result);

      response.writeHead(200, headers);
      response.end(JSON.stringify({ result }));

      return;
    }

    // 1. Маппим пустую тг выгрузку в text_entities
    if (method === 'GET' && url === '/map-plain-tg-data') {
      await mapPlainTelegramResultData();
      response.writeHead(200, headers);
      response.end(JSON.stringify({ message: 'Hello, world!' }));

      return;
    }

    // 2. Парсим text_entities в text: string
    if (method === 'GET' && url === '/parse-mapped-tg-data') {
      await parseMappedTelegramData();
      response.writeHead(200, headers);
      response.end(JSON.stringify({ message: 'Hello, world!' }));

      return;
    }

    // для пункта 3 нам нужно иметь: список мусорных слов ("подписаться на канал") и список слова, указывающих на мусорный пост ("рекламный пост")
    // у нас пустые массивы, смещение - 3 слова. надо составить н-грамму. после этого на клиенте выбрать что мы считаем мусором и повторить пунтк 3.1. n раз
    // далее на клиенте у нас список мусора. а на сервере мы будем создавать фильтрованный файл
    // 3. Удаляем лишние посты (рекламные) и удаляем лишние слова в тексте ("подписаться на канал") => filteredParsedData
    if (method === 'POST' && url === '/filter-parsed-data') {
      let body = '';

      request.on('data', (chunk) => {
        body += chunk.toString();
      });

      request.on('end', async () => {
        try {
          const { garbagePrasesList, garbagePostsList, exceptions, wordOffset } = JSON.parse(body);
          const result = await filterParsedTelegramData(garbagePrasesList, garbagePostsList, exceptions, wordOffset);

          response.writeHead(200, headers);
          response.end(JSON.stringify({ result }));
        } catch (error) {
          console.error('Error parsing request body:', error);
          response.writeHead(400, headers);
          response.end(JSON.stringify({ message: 'Bad Request: Invalid JSON' }));
        }
      });

      return;
    }

    // 4. обработать фото в текст, соединить описание фото и сам пост, закинуть в embedder, получить вектор, закинуть вектор в базу данных

    // 5. получить поисковую строку и найти релевантные посты

    response.writeHead(404, headers);
    response.end(JSON.stringify({ message: 'Not Found' }));
  } catch (error) {
    console.error('Error processing request:', error);
    response.writeHead(500, headers);
    response.end(JSON.stringify({ message: 'Internal Server Error' }));
  }
};

const server = http.createServer((request, response) => {
  void requestHandler(request, response);
});

server.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT.toString()}`);
});
