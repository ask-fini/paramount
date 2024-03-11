import { useCallback, useContext, useEffect, useRef, useState } from 'react'
import { CellValueChangedEvent } from 'ag-grid-community'
import { AgGridReact } from 'ag-grid-react'
import DownloadIcon from '@/components/Icons/DownloadIcon'
import { AppContext } from '@/context'
import SaveIcon from '@/components/Icons/SaveIcon'
import { getParamsForExport } from '@/lib/utils'
import { IRecord } from '@/lib/types'
import Services from '@/lib/services'
import PageSkeleton from '@/components/PageSkeleton'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// color: #E2E8F0

export default function EvaluatePage() {
  const {
    evaluateData,
    evaluateTableHeaders,
    getEvaluateData,
    accuracy,
    loading,
    handleAccuracyChange,
  } = useContext(AppContext)

  const gridRef = useRef<AgGridReact>(null)
  const [searchKey, setSearchKey] = useState<string>('')
  const [updatedRecords, setUpdatedRecords] = useState<Record<string, IRecord>>(
    {}
  )
  const [changeHappened, setChangeHappened] = useState(false)
  const [saving, setSaving] = useState(false)

  const onCellValueChanged = (event: CellValueChangedEvent) => {
    const foundRecord = evaluateData.find(
      (d: IRecord) =>
        d.paramount__recording_id === event.data.paramount__recording_id
    )

    if (foundRecord) {
      setUpdatedRecords((prevRecords) => ({
        ...prevRecords,
        [foundRecord.paramount__recording_id]: foundRecord,
      }))
    }

    handleAccuracyChange()
    setChangeHappened(true)
  }

  const onExportClick = useCallback(() => {
    const params = getParamsForExport()
    gridRef.current!.api.exportDataAsCsv(params)
  }, [])

  const onSaveSession = async () => {
    setSaving(true)
    const payload = Object.values(updatedRecords)
    const { error } = await Services.SaveSession(payload)
    if (error) {
      console.log('save session error: ', error)
    }
    setChangeHappened(false)
    setSaving(false)
  }

  const fetchEvaluateData = async () => {
    const foundIdentifier = localStorage.getItem('identifier')
    if (!foundIdentifier) return
    await getEvaluateData(foundIdentifier)
  }

  useEffect(() => {
    if (!evaluateData.length) {
      fetchEvaluateData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (evaluateData.length) {
      handleAccuracyChange()
    }
  }, [evaluateData, handleAccuracyChange])

  // To highlight rows, uncomment this and add getRowClass={getRowClass} to table
  // const getRowClass = (params: any) => {
  //   if (params.node.rowIndex % 2 === 0) {
  //     return 'bg-neutral-100'
  //   }
  // }

  return (
    <div className="ag-theme-quartz h-[90vh] w-screen py-10 p-4 md:px-28 md:pb-20">
      {loading ? (
        <PageSkeleton />
      ) : (
        <>
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold mb-4">Evaluate Responses</h1>
            <div className="flex items-center space-x-2">
              <p className="mr-2 font-semibold text-xs">
                Accuracy:{' '}
                <span className="text-base">{accuracy.toFixed(1)}%</span>
              </p>
              {changeHappened && (
                <button
                  type="button"
                  disabled={saving}
                  onClick={onSaveSession}
                  className="flex items-center border border-black focus:outline-0
                  hover:bg-green-500 hover:text-white hover:border-green-500"
                >
                  <SaveIcon />
                  <span className="ml-2 text-xs">
                    {saving ? 'Saving...' : 'Save Session'}
                  </span>
                </button>
              )}
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
          <div className="w-full h-full shadow-lg rounded-xl">
            <AgGridReact
              ref={gridRef}
              rowData={evaluateData}
              columnDefs={evaluateTableHeaders}
              defaultColDef={{ editable: true, resizable: true }}
              onCellValueChanged={onCellValueChanged}
              quickFilterText={searchKey}
            />
          </div>
        </>
      )}
    </div>
  )
}
