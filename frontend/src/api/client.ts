/** Base API client with typed fetch wrapper. */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

async function apiFetch<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
  const url = new URL(BASE_URL + path, window.location.origin)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }
  const res = await fetch(url.toString())
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API error ${res.status}: ${body}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  getDateInfo: (params: {
    date: string
    region: string
    lat?: number
    lon?: number
    include_panchanga?: boolean
  }) => apiFetch<import('./types').DateInfo>('/calendar/date-info', params as Record<string, string | number | boolean>),

  getMonth: (year: number, month: number, region: string) =>
    apiFetch<import('./types').MonthData>('/calendar/month', { year, month, region }),

  getPanchanga: (date: string, lat: number, lon: number, region: string) =>
    apiFetch<import('./types').Panchanga>('/panchanga', { date, lat, lon, region }),

  getIslamicDate: (date: string) =>
    apiFetch<import('./types').HijriDate>('/islamic-date', { date }),
}
