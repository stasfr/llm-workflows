export const API_URL = '192.168.1.102';

export const MILVUS_ADDRESS = `${API_URL}:19530`;
export const COLLECTION_NAME = 'test_rag_collection_with_date';
export const VECTOR_DIMENSION = 1024;

export const EMBEDDING_SERVICE_URL = `${API_URL}:1234/v1/embeddings`;
export const EMBEDDING_MODEL_NAME = 'text-embedding-intfloat-multilingual-e5-large-instruct';

export const QUERY_TEXT = 'Павлино, стрельба, убийство';

export const BATCH_SIZE = 50;

export const PORT = 3000;

export const RESULT_FILE = 'plain_data/tg/result.json';
export const MAPPED_FILE = 'plain_data/mappedMessages.json';
export const PARSED_FILE = 'plain_data/parsedMessages.json';
export const FILTERED_FILE = 'plain_data/filteredMessages.json';
