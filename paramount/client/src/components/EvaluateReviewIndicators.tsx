export default function EvaluateReviewIndicators() {
  return (
    <div className="flex justify-center items-center ml-3">
      <div className="flex items-center space-x-3">
        <div className="flex items-center">
          <span className="h-3 w-3 rounded-xl bg-sky-500"></span>
          <p className="ml-1 text-xs">Current</p>
        </div>
        <div className="flex items-center">
          <span className="h-3 w-3 rounded-xl bg-green-500"></span>
          <p className="ml-1 text-xs">Accepted</p>
        </div>
        <div className="flex items-center">
          <span className="h-3 w-3 rounded-xl bg-rose-500"></span>
          <p className="ml-1 text-xs">Rejected</p>
        </div>
      </div>
    </div>
  )
}
