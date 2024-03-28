import { ILatestDataResult, IRecord, TResult } from '@/lib/types.ts'

// Uncomment this if will deploy the client and the server
// separately and add this prefix to the endpoints
// const API_URL = import.meta.env.VITE_API_ENDPOINT

export default class Services {
  static async GetConfig(): Promise<TResult<Record<string, string[]>, Error>> {
    const response = await fetch(`/api/config`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      const res = await response.json()
      return {
        data: res,
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async GetLatestData(
    identifier: string,
    recordingIds: string[],
    evaluatedRowsOnly?: boolean
  ): Promise<TResult<ILatestDataResult, Error>> {
    const response = await fetch(`/api/latest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier_value: identifier,
        recording_ids: recordingIds || [],
        evaluated_rows_only: evaluatedRowsOnly,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('Latest Data: ', res)
      // To protect against someone pasting a random UUID and seeing internal datastructures
      if (res.result.length === 0) return { error: new Error('No data found'), data: null }
      return {
        data: { data: res.result, columnOrder: res.column_order },
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async SaveSession(
    updatedRecords: IRecord[],
    sessionAccuracy: number, // It's float on server side, should be between 0 & 1
    sessionName: string,
    recordedIds: string[],
    identifier: string
  ): Promise<TResult<ILatestDataResult, Error>> {
    const response = await fetch(`/api/submit_evaluations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        updated_records: updatedRecords,
        session_accuracy: sessionAccuracy,
        session_name: sessionName,
        recorded_ids: recordedIds,
        identifier_value: identifier,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('SAVED SESSION', res)
      return {
        data: res,
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async GetSessions(
    identifierValue: string
  ): Promise<TResult<any[], Error>> {
    const response = await fetch(`/api/get_sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier_value: identifierValue,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('GET SESSIONS', res)
      return {
        data: res,
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async Infer(
    record: IRecord,
    outputColumns: string[]
  ): Promise<TResult<any, Error>> {
    const response = await fetch(`/api/infer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record,
        output_cols: outputColumns,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('infer response: ', res)
      return {
        data: res,
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async CheckSimilarity(
    records: any[],
    outputColumnToBeTested: string
  ): Promise<TResult<any, Error>> {
    const response = await fetch(`/api/similarity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        records,
        output_col_to_be_tested: outputColumnToBeTested,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('similarity response: ', res)
      return {
        data: res,
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }
}
