import { MimeType, TextEntity } from './telegram.js';

export interface ParsedData {
  id: number;
  date: string;
  date_unixtime: string;
  text: string | (TextEntity | string)[];
  text_entities: TextEntity[];
  photo?: string;
  file?: string;
  file_name?: string;
  mime_type?: MimeType;
}
