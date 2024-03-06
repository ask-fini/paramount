import { useCallback, useContext, useEffect, useRef, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import DownloadIcon from '@/components/Icons/DownloadIcon'
import { AppContext } from '@/context'
import {
  findCommonValue,
  getHeadersWithPrefix,
  getParamsForExport,
} from '@/lib/utils'
import PageSkeleton from '@/components/PageSkeleton'
import Dropdown from '@/components/Dropdown'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'
import { IRecord } from '@/lib/types'
import Services from '@/lib/services'

export default function OptimizePage() {
  const {
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
  const [searchKey, setSearchKey] = useState<string>('')
  const [selectedInputParam, setSelectedInputParam] = useState('')
  const [selectedOutputParam, setSelectedOutputParam] = useState('')
  const [commonValue, setCommonValue] = useState('')
  const [testing, setTesting] = useState(false)

  const [cleanTestSet, setCleanTestSet] = useState<IRecord[]>([])

  const onExportClick = useCallback(() => {
    const params = getParamsForExport()
    gridRef.current!.api.exportDataAsCsv(params)
  }, [])

  // function getResultFromColname(result: any, output_col: string) {
  //   const identifying_info = output_col.split('__')[1].split('_')
  //   const output_index = parseInt(identifying_info[0]) - 1
  //   const output_colname =
  //     identifying_info.length < 2 ? null : identifying_info.slice(1).join('_')
  //   const data_item = output_colname
  //     ? result[output_index][output_colname]
  //     : result[output_index]
  //   return { output_index, output_colname, data_item }
  // }

  const onTestClick = async () => {
    setTesting(true)
    const sessionOutputColumns = getHeadersWithPrefix(
      'VITE_OUTPUT_COLS',
      'output__'
    )
    // const colsToDisplay = [
    //   ...sessionOutputColumns,
    //   ...sessionOutputColumns.map((item) => 'test_' + item),
    // ]

    const foundKey = findParamountColumnHeader(selectedInputParam)
    if (!foundKey) return

    // create new array of object with changing the selectedInputParam value with the most common value
    // NOTE to Hakim: This string arrays should be handled in server or here
    const ttt = optimizeData.map((o: IRecord) => ({
      ...o,
      [foundKey]: commonValue,
      input_args__message_history: JSON.parse(
        o.input_args__message_history.replace(/'/g, '"')
      ),
    }))
    console.log(123, ttt, foundKey)
    setCleanTestSet(ttt)

    for (const record of ttt) {
      const { data, error } = await Services.Infer(record, sessionOutputColumns)
      if (error) {
        console.log('infer error: ', error)
        setTesting(false)
        return
      }

      console.log('infer data: ', data)

      // for (const output_col of sessionOutputColumns) {
      //   const { data_item } = getResultFromColname(data, output_col)
      //   const aa = ('test_' + output_col) as keyof IRecord
      //   record[aa] = String(data_item)
      // }

      // // Prune `cleanTestSet` to include only some columns
      // const newCleanTestSet = cleanTestSet.map((record) => {
      //   const newRecord: any = {}
      //   for (const col of colsToDisplay) {
      //     newRecord[col] = record[col]
      //   }
      //   return newRecord
      // })
      // console.log('newCleanTestSet', newCleanTestSet)
      // setCleanTestSet(newCleanTestSet)
    }

    // console.log(123, sessionOutputColumns, colsToDisplay)
    // setTesting(false)

    // Test set on optimize and infer??
    // NOTE: for the similairty, get the records from infer results and put the selectedOutputParam
    // const { data, error } = await Services.CheckSimilarity(
    //   cleanTestSet,
    //   selectedOutputParam
    // )
    // if (error) {
    //   console.log('similarity error: ', error)
    //   return
    // }
    // console.log('similarity data: ', data)
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
    console.log('found commonValue', commonValue)
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
    <div className="ag-theme-quartz h-screen w-screen py-16 p-4 md:p-28">
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
                    <div className="bg-sky-500 w-[250px] h-[10px] rounded-lg" />
                  </div>
                )}
              </div>
            </>
          ) : null}
        </>
      )}
    </div>
  )
}
