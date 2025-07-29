export const API_URL = process.env.API_URL ?? '192.168.1.103';

export const MILVUS_ADDRESS = `${API_URL}:19530`;
export const COLLECTION_NAME = 'insta_jeldor_rag_flat_ip';
export const VECTOR_DIMENSION = 1024;

export const LM_STUDIO_URL = `${API_URL}:1234`;
export const CHAT_COMPLETION_MODEL_NAME = 'google/gemma-3-4b';
export const EMBEDDING_MODEL_NAME = 'text-embedding-intfloat-multilingual-e5-large-instruct';

export const BATCH_SIZE = 50;

export const PORT = 3000;

export const RESULT_FILE = 'plain_data/tg/result.json';
export const MAPPED_FILE = 'plain_data/mappedMessages.json';
export const PARSED_FILE = 'plain_data/parsedMessages.json';
export const FILTERED_FILE = 'plain_data/filteredMessages.json';

export const TELEGRAM_BOT_API = process.env.TELEGRAM_BOT_API;
export const TELEGRAM_CHAT_IDS = process.env.TELEGRAM_CHAT_IDS?.split(',') ?? [];
