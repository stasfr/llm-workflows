import fastify from 'fastify';
import cors from '@fastify/cors';
import { PORT } from './config.js';
import {
  serviceParser,
  mapPlainTelegramResultData,
  parseMappedTelegramData,
  filterParsedTelegramData,
} from './parse.js';
import { getPostsEmbeddings } from './embedding.js';

const server = fastify();

server.register(cors, {
  origin: '*',
  methods: ['OPTIONS', 'POST', 'GET'],
  maxAge: 2592000, // 30 days
  allowedHeaders: ['Content-Type'],
});

server.get('/service-parser', async (request, reply) => {
  try {
    const result = await serviceParser();
    console.log(result);
    reply.code(200)
      .send({ result });
  } catch (error) {
    console.error('Error processing request:', error);
    reply.code(500)
      .send({ message: 'Internal Server Error' });
  }
});

server.get('/map-plain-tg-data', async (request, reply) => {
  try {
    await mapPlainTelegramResultData();
    reply.code(200)
      .send({ message: 'Hello, world!' });
  } catch (error) {
    console.error('Error processing request:', error);
    reply.code(500)
      .send({ message: 'Internal Server Error' });
  }
});

server.get('/parse-mapped-tg-data', async (request, reply) => {
  try {
    await parseMappedTelegramData();
    reply.code(200)
      .send({ message: 'Hello, world!' });
  } catch (error) {
    console.error('Error processing request:', error);
    reply.code(500)
      .send({ message: 'Internal Server Error' });
  }
});

server.post('/filter-parsed-data', async (request, reply) => {
  try {
    const { garbagePrasesList, garbagePostsList, exceptions, wordOffset } = request.body as {
      garbagePrasesList: string[];
      garbagePostsList: string[];
      exceptions: string[];
      wordOffset: number;
    };
    const result = await filterParsedTelegramData(garbagePrasesList, garbagePostsList, exceptions, wordOffset);
    reply.code(200)
      .send({ result });
  } catch (error) {
    console.error('Error processing request:', error);
    reply.code(500)
      .send({ message: 'Internal Server Error' });
  }
});

server.get('/get-posts-embeddings', async (request, reply) => {
  try {
    await getPostsEmbeddings();
    reply.code(200)
      .send({ message: 'done!' });
  } catch (error) {
    console.error('Error processing request:', error);
    reply.code(500)
      .send({ message: 'Internal Server Error' });
  }
});

server.listen({ port: PORT }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }

  console.log(`Server listening at ${address}`);
});
