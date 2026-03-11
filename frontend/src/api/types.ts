/** TypeScript types mirroring the FastAPI response schemas. */

export interface BanglaDate {
  year: number
  month: number
  day: number
  month_name_bn: string
  month_name_en: string
  year_bn: string
  day_bn: string
  era_bn: string
  region: 'BD' | 'WB'
  is_sankranti: boolean
  sankranti_time_ist: string | null
}

export interface Panchanga {
  tithi_number: number
  tithi_name_bn: string
  tithi_name_en: string
  paksha_bn: string
  paksha_en: string
  nakshatra_number: number
  nakshatra_name_bn: string
  nakshatra_name_en: string
  yoga_number: number
  yoga_name_bn: string
  yoga_name_en: string
  karana_name_bn: string
  karana_name_en: string
  sunrise_local: string
  sunset_local: string
  moon_longitude: number
  sun_longitude: number
  ayanamsa: number
  is_adhika_masa: boolean
  tithi_is_kshaya: boolean
  tithi_is_vriddhi: boolean
}

export interface Festival {
  id: string
  name_bn: string
  name_en: string
  tradition: 'hindu'
  is_public_holiday: boolean
  note_bn: string | null
}

export interface DateInfo {
  gregorian: string
  wb: BanglaDate | null
  panchanga: Panchanga | null
  festivals: Festival[]
}

export interface MonthDay {
  gregorian: string
  wb: BanglaDate | null
  panchanga: Panchanga | null
  festivals: Festival[]
}

export interface MonthData {
  year: number
  month: number
  region: 'BD' | 'WB'
  days: MonthDay[]
}

export type Region = 'BD' | 'WB'
export type Tradition = 'hindu'
