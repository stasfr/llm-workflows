import { TextEntity } from './telegram.js';

export interface MappedTelegramData {
  id: number;
  date: string;
  text_entities: TextEntity[];
  photo?: string;
}

export interface ParsedTelegramData extends Omit<MappedTelegramData, 'text_entities'> { text?: string; }
