import { create } from 'zustand'
import type { Region, Tradition } from '../api/types'

interface CalendarState {
  viewYear: number
  viewMonth: number          // 1-12 (Gregorian)
  selectedDate: string | null  // ISO "YYYY-MM-DD"
  region: Region
  activeTraditions: Tradition[]

  setView: (year: number, month: number) => void
  nextMonth: () => void
  prevMonth: () => void
  selectDate: (date: string | null) => void
  setRegion: (region: Region) => void
  toggleTradition: (t: Tradition) => void
}

const today = new Date()

export const useCalendarStore = create<CalendarState>((set) => ({
  viewYear: today.getFullYear(),
  viewMonth: today.getMonth() + 1,
  selectedDate: null,
  region: 'WB',
  activeTraditions: ['hindu'],

  setView: (year, month) => set({ viewYear: year, viewMonth: month }),

  nextMonth: () =>
    set((s) => {
      if (s.viewMonth === 12) return { viewYear: s.viewYear + 1, viewMonth: 1 }
      return { viewMonth: s.viewMonth + 1 }
    }),

  prevMonth: () =>
    set((s) => {
      if (s.viewMonth === 1) return { viewYear: s.viewYear - 1, viewMonth: 12 }
      return { viewMonth: s.viewMonth - 1 }
    }),

  selectDate: (date) => set({ selectedDate: date }),

  setRegion: (region) => set({ region }),

  toggleTradition: (t) =>
    set((s) => {
      const active = s.activeTraditions.includes(t)
        ? s.activeTraditions.filter((x) => x !== t)
        : [...s.activeTraditions, t]
      return { activeTraditions: active }
    }),
}))
