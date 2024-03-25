import { ColDef } from 'ag-grid-community'

//
export type TResult<T, K> = Success<T> | Failure<K>
export type TParamountEvaluate = 'accept' | 'reject'

export interface IAppState {
  identifier: string
  setIdentifier: (val: string) => void
  config: Record<string, any>
  setConfig: (val: Record<string, any>) => void
  loading: boolean
  setLoading: (val: boolean) => void
  evaluateData: IRecord[]
  setEvaluateData: (val: IRecord[]) => void
  evaluateTableHeaders: ColDef[]
  setEvaluateTableHeaders: (val: ColDef[]) => void
  optimizeData: IRecord[]
  setOptimizeData: (val: IRecord[]) => void
  optimizeTableHeaders: ColDef[]
  setOptimizeTableHeaders: (val: ColDef[]) => void
  getEvaluateData: (val: string) => Promise<TResult<any, Error>>
  getOptimizeData: (val: string) => Promise<TResult<any, Error>>
  accuracy: number
  setAccuracy: (val: number) => void
  handleAccuracyChange: () => void
  paramountColumns: string[]
  setParamountColumns: (val: string[]) => void
  paramountInputColumns: string[]
  setParamountInputColumns: (val: string[]) => void
  paramountOutputColumns: string[]
  setParamountOutputColumns: (val: string[]) => void
  findParamountColumnHeader: (val: string) => string | null
  historyLookupForEvaluate: string[]
  setHistoryLookupForEvaluate: (val: string[]) => void
}

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
  output__1_messages: IChatList[]
  output__1_misc_data: IRecordMiscData
  output__2: number
  cosine_similarity?: number
}

export interface IParamountSession {
  paramount__session_accuracy: number
  paramount__session_id: string
  paramount__session_name: string
  paramount__session_recorded_ids: string[]
  paramount__session_splitter_id: string
  paramount__session_timestamp: string
}

export interface IChatList {
  role: string
  content: string
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
