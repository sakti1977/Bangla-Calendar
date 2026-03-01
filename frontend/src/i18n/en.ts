/**
 * English UI strings (fallback / accessibility labels).
 * Keys mirror bn.ts exactly — add new keys to both files.
 */
export const en = {
  appTitle: 'Bangla Calendar',

  // Region names
  regionBD: 'Bangladesh',
  regionWB: 'West Bengal',

  // Tradition names
  traditionAll: 'All traditions',
  traditionHindu: 'Hindu',
  traditionMuslim: 'Muslim',
  traditionBuddhist: 'Buddhist',
  traditionChristian: 'Christian',
  traditionCivic: 'National',

  // Navigation
  prevMonth: 'Previous month',
  nextMonth: 'Next month',
  today: 'Today',

  // Calendar header
  era: 'Bangla Era',
  hijriEra: 'Hijri',

  // Day detail panel
  selectDayHint: 'Select a date to see details',
  panchangaSection: 'Panchanga',
  tithi: 'Tithi',
  nakshatra: 'Nakshatra',
  yoga: 'Yoga',
  karana: 'Karana',
  paksha: 'Paksha',
  sunrise: 'Sunrise',
  sunset: 'Sunset',
  adhikaMasa: 'Adhika Masa',
  festivalsSection: 'Festivals & Holidays',
  noFestivals: 'No festivals',

  // Hijri note
  hijriTabular: 'Computed (subject to moon sighting)',
  hijriConfirmed: 'Moon sighting confirmed',

  // Location input
  locationPlaceholder: 'City…',
  locationReset: 'Reset to default',

  // Errors / loading
  loading: 'Loading…',
  errorLoading: 'Failed to load data',
  retry: 'Try again',
} as const

export type EnKey = keyof typeof en
