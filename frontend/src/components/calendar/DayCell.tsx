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

  const wb = dayData.wb
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
      aria-label={`${dayData.gregorian}${wb ? `, ${wb.day_bn} ${wb.month_name_bn} ${wb.year_bn} বঙ্গাব্দ` : ''}`}
      aria-pressed={isSelected}
    >
      {/* Primary: Bangla day number */}
      <div className={`text-xl font-bold leading-none bangla-font ${isToday ? 'text-orange-600' : isSelected ? 'text-blue-700' : 'text-gray-800'}`} lang="bn">
        {wb ? wb.day_bn : ''}
      </div>

      {/* Secondary: Gregorian day */}
      <div className="text-[10px] text-gray-500 leading-none mt-1">
        {gregorianDay}
      </div>

      {/* Hindu Panchanga (Tithi & Sankranti) */}
      <div className="flex flex-col gap-0.5 mt-0.5 overflow-hidden">
        {dayData.panchanga && (
          <div className="text-[10px] text-indigo-600 truncate bangla-font" lang="bn" title={dayData.panchanga.tithi_name_bn}>
            {dayData.panchanga.tithi_name_bn}
          </div>
        )}
        {wb?.is_sankranti && wb.sankranti_time_ist && (
          <div className="text-[9px] text-red-600 bg-red-50 px-0.5 py-px rounded shrink-0 w-fit bangla-font" lang="bn">
            সংক্রান্তি: {wb.sankranti_time_ist}
          </div>
        )}
      </div>

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
