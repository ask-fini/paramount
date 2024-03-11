import { AppContext } from '@/context.tsx'
import { useContext } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { identifier } = useContext(AppContext)
  const location = useLocation()
  const routesToDisplay = ['/evaluate', '/optimize']
  const routes = [
    { id: 1, to: routesToDisplay[0], name: 'Evaluate' },
    { id: 2, to: routesToDisplay[1], name: 'Optimize' },
  ]

  if (!routesToDisplay.includes(location.pathname)) {
    return null
  }

  return (
    <nav className="w-full flex justify-between items-center p-4 md:px-32">
      <div>
        <Link
          to="/"
          className={`mx-2 p-1 border border-transparent font-semibold
              hover:border-b-sky-500 text-neutral-800 hover:text-neutral-800
              ${location.pathname === '/' && 'border-b-sky-500'}`}
        >
          Paramount
        </Link>
        {routes.map((r) => (
          <Link
            key={r.id}
            to={r.to}
            className={`mx-2 p-1 border border-transparent
              hover:border-b-sky-500 text-neutral-800 hover:text-neutral-800
              ${location.pathname === r.to && 'border-b-sky-500'}`}
          >
            {r.name}
          </Link>
        ))}
      </div>
      <input
        type="text"
        className="border-b border-b-black p-2 w-full max-w-[270px] text-xs focus:outline-0"
        value={identifier || 'No Identifier found'}
        readOnly
      />
    </nav>
  )
}
