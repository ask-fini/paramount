import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ErrorPage() {
  const navigator = useNavigate()

  useEffect(() => {
    navigator('/', { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="w-screen h-full text-center space-y-4">
      <h1>Oops!</h1>
      <p>Sorry, an unexpected error has occurred.</p>
      <p className="text-neutral-500"></p>
    </div>
  )
}
