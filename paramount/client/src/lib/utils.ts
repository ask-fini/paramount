import {
  ACCURATE_EVALUTATION,
  EVALUTATION_HEADER,
  INACCURATE_EVALUTATION,
  INPUT_PREFIX,
  OUTPUT_PREFIX,
  PARAMOUNT_PREFIX,
} from '@/lib/constants.ts'
import { IRecord } from '@/lib/types.ts'
import paramountConfig from '../../../../paramount.toml'

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

  if (typeof mostCommonValue !== 'string') {
    mostCommonValue = JSON.stringify(mostCommonValue)
  }

  return mostCommonValue || ''
}

export function getEvaluateTableHeaders(): string[] {
  return [
    EVALUTATION_HEADER,
    ...getHeadersWithPrefix('VITE_META_COLS', PARAMOUNT_PREFIX),
    ...getHeadersWithPrefix('VITE_INPUT_COLS', INPUT_PREFIX),
    ...getHeadersWithPrefix('VITE_OUTPUT_COLS', OUTPUT_PREFIX),
  ]
}

export function getEditableTableHeaders(): string[] {
  return [
    ...getHeadersWithPrefix('VITE_OUTPUT_COLS', OUTPUT_PREFIX),
    EVALUTATION_HEADER,
  ]
}

export function getHeadersWithPrefix(header: any, prefix: string): string[] {
  return [
    ...JSON.parse(import.meta.env[header] || []).map((c: string) => prefix + c),
  ]
}

export function getEvaluateTableHeadersFromToml(): string[] {
  return [
    EVALUTATION_HEADER,
    ...getHeadersFromToml('meta_cols', PARAMOUNT_PREFIX),
    ...getHeadersFromToml('input_cols', INPUT_PREFIX),
    ...getHeadersFromToml('output_cols', OUTPUT_PREFIX),
  ]
}

export function getEditableTableHeadersFromToml(): string[] {
  return [
    ...getHeadersFromToml('output_cols', OUTPUT_PREFIX),
    EVALUTATION_HEADER,
  ]
}

export function getHeadersFromToml(header: string, prefix: string): string[] {
  // Considering there is a ui object as default!
  return paramountConfig['ui'][header].map((c: string) => prefix + c)
}

export function getEvaluateTableHeadersFromConfig(
  config: Record<string, string[]>
): string[] {
  return [
    EVALUTATION_HEADER,
    ...getHeadersFromConfig(config, 'meta_cols', PARAMOUNT_PREFIX),
    ...getHeadersFromConfig(config, 'input_cols', INPUT_PREFIX),
    ...getHeadersFromConfig(config, 'output_cols', OUTPUT_PREFIX),
  ]
}

export function getEditableTableHeadersFromConfig(
  config: Record<string, string[]>
): string[] {
  return [
    ...getHeadersFromConfig(config, 'output_cols', OUTPUT_PREFIX),
    EVALUTATION_HEADER,
  ]
}

export function getHeadersFromConfig(
  config: Record<string, string[]>,
  header: string,
  prefix: string
): string[] {
  if (config && Object.keys(config).length) {
    return config[header].map((c: string) => prefix + c)
  }
  return []
}

export function getCellEditorParams(): { values: string[] } {
  return {
    values: [ACCURATE_EVALUTATION, INACCURATE_EVALUTATION],
  }
}

export function timestampConverter(timestamp: number | string): string {
  const date = new Date(Number(timestamp))
  const formattedDate = date.toLocaleDateString('en-US', {
    // weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
  })
  return formattedDate
}
