import { useCalendarStore } from '../../store/calendarStore'
import { useLocationStore } from '../../store/locationStore'
import type { Region } from '../../api/types'

export function RegionToggle() {
  const { region, setRegion } = useCalendarStore()
  const { resetToRegionDefault } = useLocationStore()

  const toggle = (r: Region) => {
    setRegion(r)
    resetToRegionDefault(r)
  }

  return (
    <div className="flex rounded-lg border border-gray-300 overflow-hidden">
      {(['BD', 'WB'] as Region[]).map((r) => (
        <button
          key={r}
          onClick={() => toggle(r)}
          className={[
            'px-3 py-1.5 text-sm font-medium transition-colors',
            region === r
              ? 'bg-orange-500 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-50',
          ].join(' ')}
          aria-pressed={region === r}
        >
          <span className="bangla-font" lang="bn">
            {r === 'BD' ? 'বাংলাদেশ' : 'পশ্চিমবঙ্গ'}
          </span>
        </button>
      ))}
    </div>
  )
}
