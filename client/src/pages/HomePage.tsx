import { useContext, useEffect, useState } from 'react'
import { AppContext } from '../context'
import { useNavigate, useSearchParams } from 'react-router-dom'
import LoaderIcon from '../components/Icons/LoaderIcon'
import ArrowRightIcon from '../components/Icons/ArrowRightIcon'

export default function HomePage() {
  const { identifier, setIdentifier, loading, getEvaluateData } =
    useContext(AppContext)
  const navigator = useNavigate()
  const [searchParams] = useSearchParams()
  const [error, setError] = useState<string>('')

  const onSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    setError('')

    localStorage.setItem('identifier', identifier)
    const { error } = await getEvaluateData(identifier)
    if (error) {
      setError('Something went wrong!')
      return
    }

    navigator('/evaluate')
  }

  useEffect(() => {
    const identifierQuery = searchParams.get('identifier')
    if (identifierQuery) {
      setIdentifier(identifierQuery)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="w-screen h-full flex flex-col justify-center items-center">
      <div className="p-4 w-full flex flex-col justify-center items-center">
        <h1 className="text-2xl font-medium mb-5">Enter Your Identifier</h1>
        <form
          onSubmit={onSubmit}
          className="relative w-full text-center"
          style={{ maxWidth: 500 }}
        >
          <input
            type="text"
            className="border border-black w-full text-sm focus:outline-sky-500 relative"
            style={{
              padding: '1.05882rem .94118rem',
              height: '3.3em',
              borderRadius: 12,
              maxWidth: 480,
            }}
            disabled={loading}
            placeholder="Identifier.."
            value={identifier}
            onChange={(e) => {
              setIdentifier(e.target.value)
              setError('')
            }}
          />
          <div
            className="absolute bg-neutral-700 text-white rounded-lg flex items-center justify-center"
            style={{
              height: '2.4rem',
              width: '2.9rem',
              borderRadius: 8,
              top: 4,
              right: 14,
            }}
          >
            <button
              type="submit"
              className="border-0 hover:border-none focus:outline-none flex justify-center items-center"
              disabled={loading}
            >
              <span className="h-5 w-5">
                <ArrowRightIcon />
              </span>
            </button>
          </div>
        </form>
        {error && <p className="text-rose-500 font-semibold mt-4">{error}</p>}
        <div className="h-6 w-6 mt-4">{loading && <LoaderIcon />}</div>
      </div>
    </div>
  )
}
