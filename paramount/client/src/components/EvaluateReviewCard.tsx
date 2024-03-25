import Cross from '@/components/Icons/Cross'
import Done from '@/components/Icons/Done'
import { IChatList, IRecord, TParamountEvaluate } from '@/lib/types'

interface IProps {
  config: Record<string, any>
  evaluateData: IRecord[]
  reviewIndex: number
  onReviewButtonClick: (val: TParamountEvaluate) => void
}

export default function EvaluateReviewCard({
  config,
  evaluateData,
  reviewIndex,
  onReviewButtonClick,
}: IProps) {
  const chatList = config.chat_list as keyof IRecord
  const chatListRoleParam = config.chat_list_role_param as keyof IChatList
  const chatListContentParam = config.chat_list_content_param as keyof IChatList

  const chatListReferencesList =
    config.chat_list_references_list as keyof IRecord
  const chatListReferenceTitle = config.chat_list_references_titles
  const chatListReferenceUrl = config.chat_list_references_urls

  if (
    !evaluateData ||
    !evaluateData[reviewIndex] ||
    !evaluateData[reviewIndex][chatList]
  ) {
    return
  }

  return (
    <div className="py-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-base font-semibold">Reviewing one by one</h1>
      </div>
      <div className="overflow-y-scroll max-h-[400px] p-4 border rounded-xl shadow-md">
        {evaluateData[reviewIndex][chatList] &&
          evaluateData[reviewIndex][chatList]
            ?.slice(1)
            .map((m: IChatList, idx: number) => (
              <div
                key={idx}
                className="py-4 px-2 border-b-[1px] border-neutral-200"
              >
                <div className="flex flex-col">
                  <h2
                    className={`text-base font-semibold mb-2
                    ${m[chatListRoleParam] === 'user' ? 'text-sky-500' : 'text-orange-500'}`}
                  >
                    {m[chatListRoleParam]}
                  </h2>
                  <p>{m[chatListContentParam]}</p>
                  {/* Since we sliced the first object, we compare with length - 2 */}
                  {evaluateData[reviewIndex][chatList].length - 2 === idx &&
                    evaluateData[reviewIndex][chatListReferencesList].map(
                      (x: Record<string, any>, idx: number) => (
                        <a
                          key={idx}
                          href={x[chatListReferenceUrl]}
                          target="_blank"
                          className="mt-4 px-4 py-2 bg-sky-500 text-white rounded-lg hover:text-white w-fit"
                        >
                          {x[chatListReferenceTitle] || x[chatListReferenceUrl]}
                        </a>
                      )
                    )}
                </div>
              </div>
            ))}
      </div>
      {evaluateData[reviewIndex][chatList] && (
        <div className="p-4 flex justify-center items-center space-x-4 my-4">
          <button
            type="button"
            className="py-2 px-4 text-white bg-green-500 focus:outline-0 rounded-lg
              flex items-center hover:bg-green-600 shadow-md"
            style={{ transition: '.2s ease-in-out 0s' }}
            onClick={() => onReviewButtonClick('accept')}
          >
            <div className="h-5 w-5 mr-2">
              <Done />
            </div>
            <span className="font-semibold">Accept</span>
          </button>
          <button
            type="button"
            className="py-2 px-4 text-white bg-rose-500 focus:outline-0 rounded-lg
              flex items-center hover:bg-rose-600 shadow-md"
            style={{ transition: '.2s ease-in-out 0s' }}
            onClick={() => onReviewButtonClick('reject')}
          >
            <div className="h-5 w-5 mr-2">
              <Cross />
            </div>
            <span className="font-semibold">Reject</span>
          </button>
        </div>
      )}
    </div>
  )
}
