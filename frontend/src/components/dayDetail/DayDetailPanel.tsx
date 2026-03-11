import { useCalendarStore } from '../../store/calendarStore'
import { useLocationStore } from '../../store/locationStore'
import { useDateInfo } from '../../api/hooks/useDateInfo'
import { FestivalBadge } from '../shared/FestivalBadge'

export function DayDetailPanel() {
  const { selectedDate, region, selectDate } = useCalendarStore()
  const { lat, lon } = useLocationStore()

  const { data, isLoading } = useDateInfo(selectedDate, region, lat, lon, true)

  if (!selectedDate) return null

  return (
    <aside className="w-80 border-l border-gray-200 bg-white overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100">
        <h2 className="text-sm font-semibold text-gray-600">তারিখের বিবরণ</h2>
        <button
          onClick={() => selectDate(null)}
          className="text-gray-400 hover:text-gray-600 text-lg"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin w-6 h-6 border-4 border-gray-200 border-t-orange-500 rounded-full" />
        </div>
      )}

      {data && (
        <div className="p-4 space-y-4">
          {/* Hindu Date (primary) */}
          {data.wb && (
            <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
              <div className="text-2xl font-bold text-orange-700 bangla-font" lang="bn">
                {data.wb.day_bn} {data.wb.month_name_bn}
              </div>
              <div className="text-sm text-orange-600 bangla-font" lang="bn">
                {data.wb.year_bn} {data.wb.era_bn}
              </div>
            </div>
          )}

          {/* Gregorian date */}
          <div className="text-sm text-gray-600">
            {new Date(data.gregorian).toLocaleDateString('en-US', {
              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
            })}
          </div>

          {/* Panchanga */}
          {data.panchanga && (
            <div className="border border-gray-200 rounded-lg p-3 space-y-2">
              <h3 className="text-sm font-semibold text-gray-700 bangla-font" lang="bn">পঞ্চাঙ্গ</h3>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <PanchangaRow label="তিথি" valueBn={`${data.panchanga.tithi_name_bn} (${data.panchanga.paksha_bn})`} />
                <PanchangaRow label="নক্ষত্র" valueBn={data.panchanga.nakshatra_name_bn} />
                <PanchangaRow label="যোগ" valueBn={data.panchanga.yoga_name_bn} />
                <PanchangaRow label="করণ" valueBn={data.panchanga.karana_name_bn} />
                <PanchangaRow label="সূর্যোদয়" valueBn={data.panchanga.sunrise_local} />
                <PanchangaRow label="সূর্যাস্ত" valueBn={data.panchanga.sunset_local} />
              </div>
              {data.panchanga.is_adhika_masa && (
                <div className="text-xs text-purple-600 bangla-font" lang="bn">★ অধিক মাস</div>
              )}
            </div>
          )}

          {/* Festivals */}
          {data.festivals.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-700 bangla-font" lang="bn">উৎসব ও ছুটি</h3>
              <div className="flex flex-wrap gap-1.5">
                {data.festivals.map((f) => (
                  <FestivalBadge key={f.id} festival={f} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}

function PanchangaRow({ label, valueBn }: { label: string; valueBn: string }) {
  return (
    <div>
      <div className="text-gray-400 bangla-font text-xs" lang="bn">{label}</div>
      <div className="text-gray-800 bangla-font font-medium" lang="bn">{valueBn}</div>
    </div>
  )
}
