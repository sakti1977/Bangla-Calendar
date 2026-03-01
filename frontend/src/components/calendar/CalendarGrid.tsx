import type { MonthDay } from '../../api/types'
import { DayCell } from './DayCell'
import { WeekHeader } from './WeekHeader'

interface Props {
  year: number
  month: number
  days: MonthDay[]
}

export function CalendarGrid({ year, month, days }: Props) {
  // Compute day-of-week offset for the first of the month (0=Sunday)
  const firstDow = new Date(year, month - 1, 1).getDay()

  return (
    <div>
      <WeekHeader />
      <div className="grid grid-cols-7 gap-1">
        {/* Empty cells before the first day */}
        {Array.from({ length: firstDow }).map((_, i) => (
          <div key={`empty-${i}`} />
        ))}
        {/* Day cells */}
        {days.map((day) => (
          <DayCell key={day.gregorian} dayData={day} />
        ))}
      </div>
    </div>
  )
}
