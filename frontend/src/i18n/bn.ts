/**
 * Bengali UI strings.
 * Keys mirror en.ts exactly — add new keys to both files.
 */
export const bn = {
  appTitle: 'বাংলা ক্যালেন্ডার',

  // Region names
  regionBD: 'বাংলাদেশ',
  regionWB: 'পশ্চিমবঙ্গ',

  // Tradition names
  traditionAll: 'সব ঐতিহ্য',
  traditionHindu: 'হিন্দু',
  traditionMuslim: 'মুসলিম',
  traditionBuddhist: 'বৌদ্ধ',
  traditionChristian: 'খ্রিস্টান',
  traditionCivic: 'জাতীয়',

  // Navigation
  prevMonth: 'আগের মাস',
  nextMonth: 'পরের মাস',
  today: 'আজ',

  // Calendar header
  era: 'বঙ্গাব্দ',
  hijriEra: 'হিজরি',

  // Day detail panel
  selectDayHint: 'বিস্তারিত দেখতে একটি তারিখ নির্বাচন করুন',
  panchangaSection: 'পঞ্চাঙ্গ',
  tithi: 'তিথি',
  nakshatra: 'নক্ষত্র',
  yoga: 'যোগ',
  karana: 'করণ',
  paksha: 'পক্ষ',
  sunrise: 'সূর্যোদয়',
  sunset: 'সূর্যাস্ত',
  adhikaMasa: 'অধিক মাস',
  festivalsSection: 'উৎসব ও ছুটি',
  noFestivals: 'কোনো উৎসব নেই',

  // Hijri note
  hijriTabular: 'গণনা ভিত্তিক (চাঁদ দেখা সাপেক্ষে)',
  hijriConfirmed: 'চাঁদ দেখা নিশ্চিত',

  // Location input
  locationPlaceholder: 'শহর…',
  locationReset: 'ডিফল্টে ফিরুন',

  // Errors / loading
  loading: 'লোড হচ্ছে…',
  errorLoading: 'ডেটা লোড করতে ব্যর্থ হয়েছে',
  retry: 'আবার চেষ্টা করুন',
} as const

export type BnKey = keyof typeof bn
