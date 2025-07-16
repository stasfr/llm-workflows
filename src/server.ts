import http from 'http';

import { PORT } from './config.js';
import { indexText } from './textIndexer.js';

const requestHandler = async (request: http.IncomingMessage, response: http.ServerResponse) => {
  try {
    const { url, method } = request;

    if (method === 'GET' && url === '/heartbeat') {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({ message: 'Hello, world!' }));

      return;
    }

    if (method === 'GET' && url === '/index-texts') {
      await indexText();
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({ message: 'Indexing complete!' }));

      return;
    }

    response.writeHead(404, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({ message: 'Not Found' }));
  } catch (error) {
    console.error('Error processing request:', error);
    response.writeHead(500, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({ message: 'Internal Server Error' }));
  }
};

const server = http.createServer((request, response) => {
  void requestHandler(request, response);
});

server.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT.toString()}`);
});
