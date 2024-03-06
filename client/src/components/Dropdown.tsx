import { Fragment, useEffect } from 'react'
import { Listbox, Transition } from '@headlessui/react'

interface IProps {
  title: string
  list: string[]
  selected: string
  setSelected: (val: string) => void
}

export default function Dropdown({
  title,
  list,
  selected,
  setSelected,
}: IProps) {
  useEffect(() => {
    setSelected(list[0])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="w-full">
      <p className="text-xs font-medium">{title}</p>
      <Listbox value={selected} onChange={setSelected}>
        <div className="relative mt-1">
          <Listbox.Button
            className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10
                text-left shadow-md focus:outline-none focus-visible:border-indigo-500
                focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2
                focus-visible:ring-offset-orange-300 sm:text-sm"
          >
            <span className="block truncate">{selected}</span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <svg
                className="w-5 h-5 ml-auto"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 011.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </span>
          </Listbox.Button>
          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options
              className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1
                  text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm z-10 max-h-40"
            >
              {list.map((item, idx) => (
                <Listbox.Option
                  key={idx}
                  className={({ active }) =>
                    `relative cursor-default select-none py-2 pl-10 pr-4 ${
                      active ? 'bg-[#E2E8F0]' : 'text-gray-900'
                    }`
                  }
                  value={item}
                >
                  {({ selected }) => (
                    <>
                      <span
                        className={`block truncate ${
                          selected ? 'font-medium' : 'font-normal'
                        }`}
                      >
                        {item}
                      </span>
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
    </div>
  )
}
