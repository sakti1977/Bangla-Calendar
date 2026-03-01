import { useCalendarStore } from '../../store/calendarStore'
import { useMonthData } from '../../api/hooks/useMonthData'
import { MonthNavigator } from './MonthNavigator'
import { CalendarGrid } from './CalendarGrid'

export function MonthView() {
  const { viewYear, viewMonth, region } = useCalendarStore()
  const { data, isLoading, isError } = useMonthData(viewYear, viewMonth, region)

  return (
    <div className="flex-1 p-4">
      <MonthNavigator />

      {isLoading && (
        <div className="flex items-center justify-center h-64 text-gray-400">
          <div className="animate-spin w-8 h-8 border-4 border-gray-200 border-t-orange-500 rounded-full" />
        </div>
      )}

      {isError && (
        <div className="flex items-center justify-center h-64 text-red-500 text-sm">
          Calendar data unavailable. Is the backend running?
        </div>
      )}

      {data && (
        <CalendarGrid year={viewYear} month={viewMonth} days={data.days} />
      )}
    </div>
  )
}
