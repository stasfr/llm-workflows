import TelegramBot from 'node-telegram-bot-api';
import { TELEGRAM_BOT_API, TELEGRAM_CHAT_IDS } from '@/config.js';

if (!TELEGRAM_BOT_API) {
  throw new Error('TELEGRAM_BOT_API is not defined in the environment variables');
}

const bot = new TelegramBot(TELEGRAM_BOT_API);

export async function sendTelegramMessage(message: string): Promise<void> {
  if (TELEGRAM_CHAT_IDS.length === 0) {
    console.warn('TELEGRAM_CHAT_IDS is empty. No messages will be sent.');

    return;
  }

  const promises = TELEGRAM_CHAT_IDS.map((chatId) => bot.sendMessage(chatId, message));

  try {
    await Promise.all(promises);
  } catch (error) {
    console.error('Failed to send message to one or more chats:', error);
  }
}
