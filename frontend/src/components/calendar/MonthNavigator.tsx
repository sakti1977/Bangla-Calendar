import { useCalendarStore } from '../../store/calendarStore'

// BD month names for the header
const BD_MONTHS_BN = [
  'বৈশাখ', 'জ্যৈষ্ঠ', 'আষাঢ়', 'শ্রাবণ', 'ভাদ্র', 'আশ্বিন',
  'কার্তিক', 'অগ্রহায়ণ', 'পৌষ', 'মাঘ', 'ফাল্গুন', 'চৈত্র',
]

const GREG_MONTHS_EN = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const BD_DIGITS = '০১২৩৪৫৬৭৮৯'
function toBn(n: number) {
  return String(n).split('').map(c => BD_DIGITS[parseInt(c)] ?? c).join('')
}

export function MonthNavigator() {
  const { viewYear, viewMonth, nextMonth, prevMonth } = useCalendarStore()

  // Approximate Bangla month displayed: Gregorian April → Boishakh (1)
  // Show the Bangla month that starts in this Gregorian month
  const approxBanglaMonth = ((viewMonth + 8) % 12)  // April=0 → index 0 (Boishakh)
  const banglaMonthName = BD_MONTHS_BN[approxBanglaMonth]
  const banglaYear = viewMonth >= 4 ? viewYear - 593 : viewYear - 594

  return (
    <div className="flex items-center justify-between py-3 px-2">
      <button
        onClick={prevMonth}
        className="p-2 rounded-full hover:bg-gray-100 text-gray-600 font-bold text-lg"
        aria-label="Previous month"
      >
        ◄
      </button>

      <div className="text-center">
        <div className="text-xl font-bold text-gray-800 bangla-font" lang="bn">
          {banglaMonthName} {toBn(banglaYear)} বঙ্গাব্দ
        </div>
        <div className="text-sm text-gray-500">
          {GREG_MONTHS_EN[viewMonth - 1]} {viewYear}
        </div>
      </div>

      <button
        onClick={nextMonth}
        className="p-2 rounded-full hover:bg-gray-100 text-gray-600 font-bold text-lg"
        aria-label="Next month"
      >
        ►
      </button>
    </div>
  )
}
