import { useCallback, useContext, useEffect, useRef, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import DownloadIcon from '@/components/Icons/DownloadIcon'
import { AppContext } from '@/context'
import {
  findCommonValue,
  getHeadersFromConfig,
  getParamsForExport,
} from '@/lib/utils'
import PageSkeleton from '@/components/PageSkeleton'
import Dropdown from '@/components/Dropdown'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'
import { IRecord } from '@/lib/types'
import Services from '@/lib/services'
import { ColDef } from 'ag-grid-community'
import { COSINE_SIMILARITY } from '@/lib/constants'

export default function OptimizePage() {
  const {
    config,
    optimizeData,
    optimizeTableHeaders,
    getOptimizeData,
    loading,
    paramountColumns,
    paramountInputColumns,
    paramountOutputColumns,
    findParamountColumnHeader,
  } = useContext(AppContext)

  const gridRef = useRef<AgGridReact>(null)
  const bottomScrollRef = useRef<HTMLDivElement>(null)

  const [searchKey, setSearchKey] = useState<string>('')
  const [selectedInputParam, setSelectedInputParam] = useState('')
  const [selectedOutputParam, setSelectedOutputParam] = useState('')
  const [commonValue, setCommonValue] = useState('')
  const [testing, setTesting] = useState(false)
  const [similarityTestSet, setSimilarityTestSet] = useState<
    Partial<IRecord>[]
  >([])
  const [similarityScore, setSimilarityScore] = useState(0)
  const [similarityColumns, setSimilarityColumns] = useState<ColDef[]>([])

  const onExportClick = useCallback(() => {
    const params = getParamsForExport()
    gridRef.current!.api.exportDataAsCsv(params)
  }, [])

  const scrollToBottom = () => {
    setTimeout(() => {
      bottomScrollRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      })
    }, 200)
  }

  const getSimilarityTableHeaders = (headers: IRecord): ColDef[] => {
    return Object.keys(headers).map((header) => {
      if (header === COSINE_SIMILARITY) {
        const column: ColDef = {
          headerName: header,
          field: header,
          editable: false,
        }
        return column
      }

      const column: ColDef = {
        headerName: header.split('__')[1],
        field: header,
        editable: false,
        cellStyle: header.includes('test')
          ? { backgroundColor: '#2244CC44' }
          : { backgroundColor: '#cecece' },
      }
      return column
    })
  }

  const onTestClick = async () => {
    setTesting(true)
    const sessionOutputColumns = getHeadersFromConfig(
      config,
      'output_cols',
      'output__'
    )
    const colsToDisplay = [
      ...sessionOutputColumns,
      ...sessionOutputColumns.map((item) => 'test_' + item),
    ]

    const foundKey = findParamountColumnHeader(selectedInputParam)
    if (!foundKey) return

    // Create new array of object with changing the
    // `selectedInputParam` value with the most common value
    const formattedOptimizedData = optimizeData.map((o: IRecord) => ({
      ...o,
      [foundKey]: commonValue,
    }))

    let cleanTestSet: any = [...formattedOptimizedData]

    for (const [index, record] of formattedOptimizedData.entries()) {
      const { data, error } = await Services.Infer(record, sessionOutputColumns)
      if (error) {
        console.log('infer error: ', error)
        setTesting(false)
        return
      }

      const response = data.result[0]
      for (const output_col of sessionOutputColumns) {
        Object.keys(response).forEach((x) => {
          if (x.includes(output_col)) {
            cleanTestSet[index] = { ...cleanTestSet[index], [x]: response[x] }
          }
        })
      }

      // Prune `cleanTestSet` to include only some columns
      cleanTestSet = cleanTestSet.map((record: IRecord) => {
        const newRecord: Partial<IRecord> = {}
        for (const col of colsToDisplay) {
          newRecord[col as keyof IRecord] = record[col as keyof IRecord]
        }
        return newRecord
      })
    }

    setTesting(false)

    // Test set on optimize and infer??
    // NOTE: for the similairty, get the records from infer results and put the selectedOutputParam
    const { data, error } = await Services.CheckSimilarity(
      cleanTestSet,
      'output__' + selectedOutputParam
    )
    if (error) {
      console.log('similarity error: ', error)
      return
    }

    const similarityScores = data.result
    let score = 0
    for (const [index, set] of cleanTestSet.entries()) {
      set[COSINE_SIMILARITY] = (similarityScores[index] * 100).toFixed(1) + '%'
      score += similarityScores[index] * 100
    }

    const columnDefs = getSimilarityTableHeaders(cleanTestSet[0])
    setSimilarityColumns(columnDefs)
    setSimilarityScore(Number((score / similarityScores.length).toFixed(2)))
    setSimilarityTestSet(cleanTestSet)
    scrollToBottom()
  }

  const fetchOptimizeData = async () => {
    const foundIdentifier = localStorage.getItem('identifier')
    if (!foundIdentifier) return
    await getOptimizeData(foundIdentifier)
  }

  useEffect(() => {
    const foundKey = findParamountColumnHeader(selectedInputParam)
    if (!foundKey) return
    const commonValue = findCommonValue(optimizeData, foundKey as keyof IRecord)
    setCommonValue(commonValue)
  }, [
    findParamountColumnHeader,
    optimizeData,
    paramountColumns,
    selectedInputParam,
  ])

  useEffect(() => {
    if (!optimizeData.length) {
      fetchOptimizeData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="ag-theme-quartz h-[90vh] w-screen py-10 p-4 md:px-28 md:pb-20">
      {loading ? (
        <PageSkeleton />
      ) : (
        <>
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold mb-4">
              Optimize performance with tweaks
            </h1>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                className="border py-2 px-4 rounded-lg text-xs focus:outline-sky-500 w-24 md:w-60"
                placeholder="Search..."
                value={searchKey}
                onChange={(e) => setSearchKey(e.target.value)}
              />
              <button
                type="button"
                onClick={onExportClick}
                title="Download as CSV"
                className="focus:outline-0 border border-transparent
                  hover:border-black hover:bg-black hover:text-white"
              >
                <DownloadIcon />
              </button>
            </div>
          </div>
          <div className="w-full h-full shadow-lg rounded-xl max-h-[300px]">
            <AgGridReact
              ref={gridRef}
              rowData={optimizeData}
              columnDefs={optimizeTableHeaders}
              defaultColDef={{ editable: true, resizable: true }}
              quickFilterText={searchKey}
            />
          </div>
          {optimizeData.length ? (
            <>
              <div className="flex w-full mt-8 md:space-x-8 flex-wrap">
                <div className="flex flex-col space-y-8 flex-1">
                  <Dropdown
                    title="Select an input param to vary"
                    list={paramountInputColumns}
                    selected={selectedInputParam}
                    setSelected={setSelectedInputParam}
                  />
                  <Dropdown
                    title="Select an output param to measure similarity: ground truth <> test set"
                    list={paramountOutputColumns}
                    selected={selectedOutputParam}
                    setSelected={setSelectedOutputParam}
                  />
                </div>
                <div className="flex-1 w-full h-full mt-4 md:mt-0">
                  <p className="text-xs mb-1 font-medium">Most common value</p>
                  <textarea
                    className="w-full h-full min-h-[128px] min-w-[300px] border border-neutral-200
                      rounded-lg p-2 focus:outline-sky-500 shadow-md"
                    value={commonValue}
                    onChange={(e) => setCommonValue(e.target.value)}
                    spellCheck={false}
                  >
                    {' '}
                    asdfasdf
                  </textarea>
                </div>
              </div>
              <div className="flex justify-center mt-8">
                <button
                  type="button"
                  className="py-3 px-8 mb-8 md:mb-0 border border-black shadow
                    hover:bg-black hover:text-white hover:scale-105 hover:shadow-xl"
                  style={{ transition: '.2s ease-in-out 0s' }}
                  onClick={onTestClick}
                >
                  Test against ground truth
                </button>
              </div>
              <div className="w-full flex justify-center my-8">
                {testing && (
                  <div className="border w-full max-w-[600px] h-3 bg-neutral-100 rounded-lg">
                    <div className="bg-neutral-700 w-[250px] h-[10px] rounded-lg" />
                  </div>
                )}
              </div>
              {similarityTestSet.length ? (
                <div className="flex flex-col justify-center h-[400px] pb-16">
                  <div className="w-full h-full shadow-lg rounded-xl max-h-[300px]">
                    <AgGridReact
                      rowData={similarityTestSet}
                      columnDefs={similarityColumns}
                      defaultColDef={{ editable: false, resizable: true }}
                    />
                  </div>
                  <div className="flex flex-col justify-center items-center mt-8">
                    <p className="font-semibold text-xs">
                      Average similarity to evaluation
                    </p>
                    <span className="text-3xl">{similarityScore}%</span>
                  </div>
                </div>
              ) : null}
              <div ref={bottomScrollRef} />
            </>
          ) : null}
        </>
      )}
    </div>
  )
}
