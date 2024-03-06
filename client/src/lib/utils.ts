import { ACCURATE_EVALUTATION, EVALUTATION_HEADER } from '@/lib/constants'
import { IRecord } from '@/lib/types'

function getBoolean(inputSelector: string): boolean {
  return !!(document.querySelector(inputSelector) as HTMLInputElement)?.checked
}

export function getParamsForExport() {
  return {
    suppressQuotes: getBoolean('#suppressQuotes'),
  }
}

export function findCommonValue(
  records: IRecord[],
  keyToSearch: keyof IRecord
): string {
  const frequency: Record<string, number> = {}
  let mostCommonValue: string = ''
  let maxCount: number = 0

  for (const record of records) {
    const key = record[keyToSearch]
    if (frequency[key]) {
      frequency[key] += 1
    } else {
      frequency[key] = 1
    }

    if (frequency[key] > maxCount) {
      mostCommonValue = key
      maxCount = frequency[key]
    }
  }

  return mostCommonValue || ''
}

export function getEvaluateTableHeaders(): string[] {
  return [
    EVALUTATION_HEADER,
    ...getHeadersWithPrefix('VITE_META_COLS', 'paramount__'),
    ...getHeadersWithPrefix('VITE_INPUT_COLS', 'input_'),
    ...getHeadersWithPrefix('VITE_OUTPUT_COLS', 'output__'),
  ]
}

export function getEditableTableHeaders(): string[] {
  return [
    ...getHeadersWithPrefix('VITE_OUTPUT_COLS', 'output__'),
    EVALUTATION_HEADER,
  ]
}

export function getHeadersWithPrefix(header: any, prefix: string): string[] {
  return [
    ...JSON.parse(import.meta.env[header] || []).map((c: string) => prefix + c),
  ]
}

export function getCellEditorParams(): { values: string[] } {
  return {
    values: [
      ACCURATE_EVALUTATION,
      '❔ Missing Info',
      '❌ Irrelevant Extra Info',
      '🕰️ Wrong/Outdated Info',
      "📃 Didn't follow instruction",
    ],
  }
}
