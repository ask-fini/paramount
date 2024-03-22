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
    evaluatedRowsOnly?: boolean
  ): Promise<TResult<ILatestDataResult, Error>> {
    // TODO: what to do with env vars? need VITE prefix
    const response = await fetch(`/api/latest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier_value: identifier,
        evaluated_rows_only: evaluatedRowsOnly,
      }),
    })

    if (response.ok) {
      const res = await response.json()
      console.log('Latest Data: ', res)
      return {
        data: { data: res.result, columnOrder: res.column_order },
        error: null,
      }
    }

    return { error: new Error(''), data: null }
  }

  static async SaveSession(
    data: any
  ): Promise<TResult<ILatestDataResult, Error>> {
    // TODO: what to do with env vars? need VITE prefix
    const response = await fetch(`/api/submit_evaluations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        updated_records: data,
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
