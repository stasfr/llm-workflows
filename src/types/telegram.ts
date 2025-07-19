type MimeType =
  | 'application/pdf'
  | 'video/mp4'
  | 'image/jpeg'
  | 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  | 'video/quicktime'
  | 'audio/mpeg'
  | 'audio/ogg';

enum MessageType {
  Service = 'service',
  Message = 'message',
}
type MessageAction = 'create_channel' | 'pin_message';

interface Answer {
  text: string;
  voters: number;
  chosen: boolean;
}

interface Poll {
  question: string;
  closed: boolean;
  total_voters: number;
  answers: Answer[]
}

enum ReactionType {
  Emoji = 'emoji',
  Paid = 'paid',
}

interface PaidReaction {
  type: ReactionType.Paid;
  count: number
}

interface EmojiReaction {
  type: ReactionType.Emoji;
  count: number;
  emoji: string;
}

type TextEntityType =
  | 'plain'
  | 'link'
  | 'mention'
  | 'text_link'
  | 'italic'
  | 'bold'
  | 'underline'
  | 'email'
  | 'strikethrough'
  | 'spoiler'
  | 'bot_command'
  | 'code'
  | 'custom_emoji'
  | 'blockquote'
  | 'phone'
  | 'hashtag';

interface TextEntity {
  type: TextEntityType;
  text: string;
  href?: string;
  document_id?: string;
  collapsed?: boolean;
}

interface MessageBase {
  id: number;
  date: string; // 2021-10-04T21:33:22
  date_unixtime: string;
  text: string | (TextEntity | string)[];
  text_entities: TextEntity[];
}

export interface Service extends MessageBase {
  type: MessageType.Service;
  actor: string;
  actor_id: string;
  action: MessageAction;
  title: string;
}

export interface Message extends MessageBase {
  type: MessageType.Message;
  edited?: string;
  edited_unixtime?: string;
  from: string;
  from_id: string;
  photo?: string;
  photo_file_size?: number;
  width?: number;
  height?: number;
  reactions?: (EmojiReaction | PaidReaction)[];
  poll?: Poll;
  file?: string;
  file_name?: string;
  file_size?: number;
  mime_type?: MimeType;
  thumbnail?: string;
  thumbnail_file_size?: number;
  duration_seconds?: number;
  reply_to_message_id?: number;
}

export interface TgData {
  name: string;
  type: string;
  id: number;
  messages: Message[]
}
