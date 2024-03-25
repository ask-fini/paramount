import { useEffect, useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AppContext } from '@/context'
import Services from '@/lib/services'
import { timestampConverter } from '@/lib/utils'
import LoaderIcon from '@/components/Icons/LoaderIcon'
import { IParamountSession } from '@/lib/types'

export default function HistoryPage() {
  const { identifier, setHistoryLookupForEvaluate } = useContext(AppContext)
  const navigator = useNavigate()

  const [history, setHistory] = useState<IParamountSession[]>([])
  const [loading, setLoading] = useState(false)

  const getSessions = async () => {
    const { data, error } = await Services.GetSessions(identifier)
    if (error) {
      console.log('error ', error)
      setLoading(false)
      return
    }
    setHistory(data)
    setLoading(false)
  }

  const onSessionClick = async (session: IParamountSession) => {
    setHistoryLookupForEvaluate(session.paramount__session_recorded_ids)
    navigator('/evaluate')
  }

  useEffect(() => {
    setLoading(true)
    if (identifier) {
      getSessions()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [identifier])

  return (
    <div className="h-[90vh] w-screen py-10 p-4 md:px-28 md:pb-20">
      {history.length ? (
        <div className="flex flex-col justify-center items-center mt-10">
          <h4 className="text-left text-base font-semibold mb-4">
            Saved Sessions
          </h4>
          <ul>
            {history.map((h) => (
              <div
                className="flex items-center my-2"
                key={h.paramount__session_id}
              >
                <button
                  type="button"
                  onClick={() => onSessionClick(h)}
                  className="text-sky-600 hover:underline"
                >
                  {timestampConverter(h.paramount__session_name) ||
                    timestampConverter(h.paramount__session_timestamp)}
                </button>
                <p className="text-sm">
                  - Accuracy:
                  <span className="font-semibold ml-2 text-base">
                    {(h.paramount__session_accuracy * 100).toFixed(1)}%
                  </span>
                </p>
              </div>
            ))}
          </ul>
        </div>
      ) : loading ? (
        <div className="h-10 mt-60 flex justify-center w-full">
          <LoaderIcon />
        </div>
      ) : (
        <div className="flex flex-col justify-center items-center mt-40 space-y-4 font-semibold">
          <p>Looks like there is no saved sessions, yet!</p>
          <Link
            to="/evaluate"
            className="px-4 py-2 border border-black text-sm rounded-xl
              text-black hover:border-sky-500 hover:text-sky-500 shadow-md"
          >
            Go to Evaluate
          </Link>
        </div>
      )}
    </div>
  )
}
