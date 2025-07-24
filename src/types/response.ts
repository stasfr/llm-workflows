enum ObjectTypes {
  Model = 'model',
  List = 'list',
  Completion = 'chat.completion',
  Embedding = 'embedding',
}

export interface IModelData {
  id: string;
  object: ObjectTypes.Model;
  owned_by: string;
}

export interface IModelDataResponse {
  data: IModelData[];
  object: ObjectTypes.List;
}

export type IFinishReason = 'stop';

export interface ICompletionMessage {
  role: 'assistant';
  content: string;
}

export interface IChoice {
  index: number;
  logprobs: unknown;
  finish_reason: IFinishReason;
  message: ICompletionMessage;
}

export interface IChatCompletionResponse {
  id: string;
  object: ObjectTypes.Completion;
  created: number;
  model: string;
  choices: IChoice[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  stats: unknown;
  system_fingerprint: string;
}

export interface IEmbeddingData {
  object: ObjectTypes.Embedding;
  embedding: number[];
  index: number;
}

export interface IEmbeddingResponse {
  object: ObjectTypes.List;
  data: IEmbeddingData[];
  model: string;
  usage: {
    prompt_tokens: number;
    total_tokens: number;
  }
}
