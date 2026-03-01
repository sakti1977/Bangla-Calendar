import { useCalendarStore } from '../../store/calendarStore'
import { TRADITION_COLORS } from '../../utils/festivalColors'
import type { Tradition } from '../../api/types'

const ALL_TRADITIONS: Tradition[] = ['hindu', 'muslim', 'buddhist', 'christian', 'civic']

export function TraditionFilter() {
  const { activeTraditions, toggleTradition } = useCalendarStore()

  return (
    <div className="flex gap-1.5 flex-wrap">
      {ALL_TRADITIONS.map((t) => {
        const colors = TRADITION_COLORS[t]
        const active = activeTraditions.includes(t)
        return (
          <button
            key={t}
            onClick={() => toggleTradition(t)}
            className={[
              'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border transition-all',
              active ? colors.badge : 'bg-gray-100 text-gray-400 border-gray-200',
            ].join(' ')}
            aria-pressed={active}
          >
            <span className={`w-2 h-2 rounded-full ${active ? colors.dot : 'bg-gray-300'}`} />
            <span className="bangla-font" lang="bn">{colors.label}</span>
          </button>
        )
      })}
    </div>
  )
}
