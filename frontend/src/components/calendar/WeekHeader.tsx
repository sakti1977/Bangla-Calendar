/** Bengali weekday headers for the calendar grid. */
const WEEKDAYS_BN = ['রবি', 'সোম', 'মঙ্গল', 'বুধ', 'বৃহঃ', 'শুক্র', 'শনি']

export function WeekHeader() {
  return (
    <div className="grid grid-cols-7 gap-1 mb-1">
      {WEEKDAYS_BN.map((day) => (
        <div
          key={day}
          className="text-center text-xs font-semibold text-gray-500 py-1 bangla-font"
          lang="bn"
        >
          {day}
        </div>
      ))}
    </div>
  )
}
