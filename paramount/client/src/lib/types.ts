//
// const { data, error } = await apiCall(): Promise<Data, Error>
export type TResult<T, K> = Success<T> | Failure<K>

export interface ILatestDataResult {
  data: IRecord[]
  columnOrder: string[]
}

// Example records on Postgres
export interface IRecord extends IParamountRecordFields {
  input_args__bot_uuid: string
  input_args__categories: any
  input_args__company_uuid: string
  input_args__function_call: any
  input_args__functions: any
  input_args__infer: boolean
  input_args__language: string
  input_args__message_history: string
  input_args__new_question: string
  input_args__stop: any
  input_args__stream: boolean
  input_args__temperature: number
  input_kwargs__seed: any
  output__1_answer: string
  output__1_answer_uuid: string
  output__1_based_on: string
  output__1_categories: any
  output__1_error: any
  output__1_function_call: IFunctionCall
  output__1_messages: string
  output__1_misc_data: IRecordMiscData
  output__2: number
}

interface IParamountRecordFields {
  paramount__evaluated_at: string
  paramount__evaluation: string
  paramount__execution_time: number
  paramount__function_name: string
  paramount__recorded_at: string
  paramount__recording_id: string
}

interface IFunctionCall {}

interface IRecordMiscData {
  seed: any
  system_fingerprint: any
  usage: IRecordMiscDataUsage
}

interface IRecordMiscDataUsage {
  completion_tokens: number
  prompt_tokens: number
  total_tokens: number
}

type Success<T> = {
  data: T
  error: null
}

type Failure<K> = {
  data: null
  error: K | Error
}
