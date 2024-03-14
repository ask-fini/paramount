import { ACCURATE_EVALUTATION, EVALUTATION_HEADER } from '@/lib/constants.ts'
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

export function getEvaluateTableHeadersFromToml(): string[] {
  return [
    EVALUTATION_HEADER,
    ...getHeadersFromToml('meta_cols', 'paramount__'),
    ...getHeadersFromToml('input_cols', 'input_'),
    ...getHeadersFromToml('output_cols', 'output__'),
  ]
}

export function getEditableTableHeadersFromToml(): string[] {
  return [...getHeadersFromToml('output_cols', 'output__'), EVALUTATION_HEADER]
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
    ...getHeadersFromConfig(config, 'meta_cols', 'paramount__'),
    ...getHeadersFromConfig(config, 'input_cols', 'input_'),
    ...getHeadersFromConfig(config, 'output_cols', 'output__'),
  ]
}

export function getEditableTableHeadersFromConfig(
  config: Record<string, string[]>
): string[] {
  return [
    ...getHeadersFromConfig(config, 'output_cols', 'output__'),
    EVALUTATION_HEADER,
  ]
}

export function getHeadersFromConfig(
  config: Record<string, string[]>,
  header: string,
  prefix: string
): string[] {
  return config[header].map((c: string) => prefix + c)
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
