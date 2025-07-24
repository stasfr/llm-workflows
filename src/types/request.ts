export type IChatRequestMessageRole = 'system' | 'user';

export enum IContentType {
  Text = 'text',
  Image = 'image_url',
}

export interface ITextContent {
  type: IContentType.Text;
  text: string;
}

export interface IImageContent {
  type: IContentType.Image;
  image_url: { url: string };
}

export interface IChatRequestMessage {
  role: IChatRequestMessageRole;
  content: string | (ITextContent | IImageContent)[];
}

export type IModel = 'google/gemma-3-4b' | 'text-embedding-intfloat-multilingual-e5-large-instruct';

export interface IChatCompletionRequest {
  model: IModel;
  messages: IChatRequestMessage[];
  temperature?: number;
}

export interface IEmbeddingRequest {
  model: IModel;
  input: string[];
}
