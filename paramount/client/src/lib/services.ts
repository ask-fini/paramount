import { ILatestDataResult, IRecord, TResult } from '@/lib/types.ts'

// TODO: change this after fixing env variable issue
const API_URL = 'http://localhost:9001'

export default class Services {
  static async GetLatestData(
    identifier: string,
    evaluatedRowsOnly?: boolean
  ): Promise<TResult<ILatestDataResult, Error>> {
    // TODO: what to do with env vars? need VITE prefix
    const response = await fetch(`${API_URL}/latest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_uuid: identifier,
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
    const response = await fetch(`${API_URL}/submit_evaluations`, {
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
    const response = await fetch(`${API_URL}/infer`, {
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
    const response = await fetch(`${API_URL}/similarity`, {
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
