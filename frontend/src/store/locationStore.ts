import { create } from 'zustand'
import type { Region } from '../api/types'

interface LocationState {
  lat: number
  lon: number
  timezone: string
  locationName: string
  isCustom: boolean
  setLocation: (lat: number, lon: number, name: string) => void
  resetToRegionDefault: (region: Region) => void
}

const REGION_DEFAULTS: Record<Region, { lat: number; lon: number; locationName: string; timezone: string }> = {
  BD: { lat: 23.8103, lon: 90.4125, locationName: 'Dhaka', timezone: 'Asia/Dhaka' },
  WB: { lat: 22.5726, lon: 88.3639, locationName: 'Kolkata', timezone: 'Asia/Kolkata' },
}

export const useLocationStore = create<LocationState>((set) => ({
  ...REGION_DEFAULTS.BD,
  isCustom: false,

  setLocation: (lat, lon, name) =>
    set({ lat, lon, locationName: name, isCustom: true }),

  resetToRegionDefault: (region) =>
    set({ ...REGION_DEFAULTS[region], isCustom: false }),
}))
