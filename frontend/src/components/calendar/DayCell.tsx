import type { MonthDay } from '../../api/types'
import { useCalendarStore } from '../../store/calendarStore'
import { TRADITION_COLORS } from '../../utils/festivalColors'

interface Props {
  dayData: MonthDay
  isCurrentMonth?: boolean
}

export function DayCell({ dayData, isCurrentMonth = true }: Props) {
  const { selectedDate, selectDate, activeTraditions } = useCalendarStore()
  const isSelected = selectedDate === dayData.gregorian
  const today = new Date().toISOString().split('T')[0]
  const isToday = dayData.gregorian === today

  const bd = dayData.bd
  const gregorianDay = parseInt(dayData.gregorian.split('-')[2])

  const visibleFestivals = dayData.festivals.filter((f) =>
    activeTraditions.includes(f.tradition)
  )

  const handleClick = () => selectDate(isSelected ? null : dayData.gregorian)

  return (
    <button
      onClick={handleClick}
      className={[
        'relative w-full h-20 p-1 text-left border rounded-md transition-colors',
        isCurrentMonth ? 'bg-white' : 'bg-gray-50 opacity-60',
        isSelected ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-300' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
        isToday && !isSelected ? 'border-orange-400 bg-orange-50' : '',
      ].join(' ')}
      aria-label={`${dayData.gregorian}${bd ? `, ${bd.day_bn} ${bd.month_name_bn} ${bd.year_bn} বঙ্গাব্দ` : ''}`}
      aria-pressed={isSelected}
    >
      {/* Primary: Bangla day number */}
      <div className={`text-xl font-bold leading-none bangla-font ${isToday ? 'text-orange-600' : isSelected ? 'text-blue-700' : 'text-gray-800'}`} lang="bn">
        {bd ? bd.day_bn : ''}
      </div>

      {/* Secondary: Gregorian day */}
      <div className="text-xs text-gray-400 leading-none mt-0.5">
        {gregorianDay}
      </div>

      {/* Hijri day */}
      {dayData.hijri && (
        <div className="text-xs text-gray-400 leading-none" lang="bn">
          {dayData.hijri.day_bn}
        </div>
      )}

      {/* Festival dots */}
      {visibleFestivals.length > 0 && (
        <div className="absolute bottom-1 left-1 right-1 flex gap-0.5 flex-wrap">
          {visibleFestivals.slice(0, 4).map((f) => (
            <span
              key={f.id}
              className={`w-1.5 h-1.5 rounded-full ${TRADITION_COLORS[f.tradition].dot}`}
              title={f.name_en}
              data-testid={`festival-dot-${f.tradition}`}
            />
          ))}
          {visibleFestivals.length > 4 && (
            <span className="text-xs text-gray-400 leading-none">+{visibleFestivals.length - 4}</span>
          )}
        </div>
      )}
    </button>
  )
}
