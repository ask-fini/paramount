import { createContext, useEffect, useState } from 'react'
import { IAppState, IRecord, TResult } from '@/lib/types'
import { ColDef } from 'ag-grid-community'
import {
  getCellEditorParams,
  getEditableTableHeaders,
  getEvaluateTableHeaders,
} from '@/lib/utils'
import { ACCURATE_EVALUTATION, EVALUTATION_HEADER } from '@/lib/constants'
import Services from '@/lib/services'

export const AppContext = createContext<IAppState>({} as IAppState)

const AppContextProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [identifier, setIdentifier] = useState('')
  const [loading, setLoading] = useState<boolean>(false)
  const [accuracy, setAccuracy] = useState<number>(0)
  // Original, untouched columns
  const [paramountColumns, setParamountColumns] = useState<string[]>([])
  const [paramountInputColumns, setParamountInputColumns] = useState<string[]>(
    []
  )
  const [paramountOutputColumns, setParamountOutputColumns] = useState<
    string[]
  >([])

  const [evaluateData, setEvaluateData] = useState<IRecord[]>([])
  const [evaluateTableHeaders, setEvaluateTableHeaders] = useState<ColDef[]>([])
  const [optimizeData, setOptimizeData] = useState<IRecord[]>([])
  const [optimizeTableHeaders, setOptimizeTableHeaders] = useState<ColDef[]>([])

  useEffect(() => {
    const foundIdentifier = localStorage.getItem('identifier')
    if (foundIdentifier) {
      setIdentifier(foundIdentifier)
    }
  }, [])

  const getEvaluateData = async (
    identifier: string
  ): Promise<TResult<any, Error>> => {
    setLoading(true)
    const { data, error } = await Services.GetLatestData(identifier)
    if (error) {
      setLoading(false)
      return { data: null, error }
    }

    const editableColumns = getEditableTableHeaders()
    const headers = getEvaluateTableHeaders()
    const columnDefs = headers.map((header) => {
      const isEditable = editableColumns.includes(header)
      const column: ColDef = {
        headerName: header.split('__')[1],
        field: header,
        sortable: true,
        filter: true,
        editable: isEditable,
        cellStyle: isEditable ? {} : { backgroundColor: '#2244CC44' },
      }

      if (header === EVALUTATION_HEADER) {
        column.cellRenderer = (params: any) => {
          return params.value || 'None'
        }
        column.cellEditor = 'agSelectCellEditor'
        column.cellEditorParams = getCellEditorParams()
      }

      return column
    })

    setEvaluateData(
      data.data.map((d: IRecord) => ({
        ...d,
        evaluation: d.paramount__evaluation,
      }))
    )
    setEvaluateTableHeaders(columnDefs as ColDef[])
    setLoading(false)
    return { data: null, error: null }
  }

  const getOptimizeData = async (
    identifier: string
  ): Promise<TResult<any, Error>> => {
    setLoading(true)
    const { data, error } = await Services.GetLatestData(identifier, true)
    if (error) {
      setLoading(false)
      return { data: null, error }
    }

    const inputColumns = data.columnOrder
      .filter((c: string) => c.startsWith('input'))
      .map((c: string) => c.split('__')[1])

    const outputColumns = data.columnOrder
      .filter((c: string) => c.startsWith('output'))
      .map((c: string) => c.split('__')[1])

    setParamountColumns(data.columnOrder)
    setParamountInputColumns(inputColumns)
    setParamountOutputColumns(outputColumns)

    const columnDefs = data.columnOrder.map((header) => {
      const column: ColDef = {
        headerName: header.split('__')[1],
        field: header,
        editable: false,
      }

      if (header === EVALUTATION_HEADER) {
        column.cellEditor = 'agSelectCellEditor'
        column.cellEditorParams = getCellEditorParams()
      }

      return column
    })

    setOptimizeData(data.data)
    setOptimizeTableHeaders(columnDefs as ColDef[])
    setLoading(false)

    return { data: null, error: null }
  }

  const handleAccuracyChange = () => {
    const totalRecords = evaluateData.length
    const evaluatedRecords = evaluateData.filter(
      (record) => record[EVALUTATION_HEADER] === ACCURATE_EVALUTATION
    ).length
    const accuracy = 100 * (evaluatedRecords / totalRecords)
    setAccuracy(accuracy || 0)
  }

  const findParamountColumnHeader = (key: string): string | null => {
    const foundKey = paramountColumns.find((c) => c.includes(key))
    if (!foundKey) {
      return null
    }
    return foundKey
  }

  return (
    <AppContext.Provider
      value={{
        identifier,
        setIdentifier,
        loading,
        setLoading,
        evaluateData,
        setEvaluateData,
        evaluateTableHeaders,
        optimizeData,
        setOptimizeData,
        optimizeTableHeaders,
        setOptimizeTableHeaders,
        setEvaluateTableHeaders,
        getEvaluateData,
        getOptimizeData,
        accuracy,
        setAccuracy,
        handleAccuracyChange,
        paramountColumns,
        setParamountColumns,
        paramountInputColumns,
        setParamountInputColumns,
        paramountOutputColumns,
        setParamountOutputColumns,
        findParamountColumnHeader,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export default AppContextProvider
