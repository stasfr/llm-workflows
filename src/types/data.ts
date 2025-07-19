import { MimeType, TextEntity } from './telegram.js';

export interface MappedTelegramData {
  id: number;
  date: string;
  date_unixtime: string;
  text_entities: TextEntity[];
  photo?: string;
  file?: string;
  file_name?: string;
  mime_type?: MimeType;
}

export interface ParsedTelegramData extends Omit<MappedTelegramData, 'text_entities'> { text: string; }
