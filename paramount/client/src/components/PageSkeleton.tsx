export default function PageSkeleton() {
  return (
    <div className="w-full h-full flex justify-center items-center">
      <div
        className="isolate overflow-hidden shadow-xl shadow-black/5
          before:border-t before:border-gray-100/10 w-full rounded-xl"
      >
        <div className="-translate-x-full animate-[shimmer_1.5s_infinite]"></div>
        <div
          className="relative
            before:absolute before:inset-0
            before:-translate-x-full
            before:animate-[shimmer_1.5s_infinite]
            before:bg-gradient-to-r
            before:from-transparent before:via-neutral-300 before:to-transparent"
        >
          <div className="flex items-center justify-between mb-4 px-2">
            <div className="h-10 w-60 rounded-lg bg-neutral-200"></div>
            <div className="flex items-center space-x-2">
              <div className="h-10 w-40 rounded-lg bg-neutral-200"></div>
              <div className="h-10 w-60 rounded-lg bg-neutral-200"></div>
              <div className="h-10 w-10 rounded-lg bg-neutral-200"></div>
            </div>
          </div>
          <div
            className="space-y-5 rounded-2xl bg-neutral-200 p-2 w-full bg-gradient-to-r from-transparent
              via-neutral-100/10 to-transparent"
          >
            <div className="h-96 rounded-lg bg-neutral-100"></div>
            <div className="space-y-3 absolute top-16 left-0 w-full px-10">
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
              <div className="h-8 rounded-lg bg-neutral-200"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
