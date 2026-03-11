import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../client'
import type { MonthData, Region } from '../types'

export function useMonthData(year: number, month: number, region: Region, lat?: number, lon?: number) {
  const queryClient = useQueryClient()

  // Prefetch adjacent months on mount
  const prefetch = (y: number, m: number) => {
    queryClient.prefetchQuery({
      queryKey: ['month', region, y, m, lat, lon],
      queryFn: () => api.getMonth(y, m, region, lat, lon),
      staleTime: 7 * 24 * 60 * 60 * 1000,
    })
  }

  // Prefetch next and previous months
  const prevM = month === 1 ? 12 : month - 1
  const prevY = month === 1 ? year - 1 : year
  const nextM = month === 12 ? 1 : month + 1
  const nextY = month === 12 ? year + 1 : year

  prefetch(prevY, prevM)
  prefetch(nextY, nextM)

  return useQuery<MonthData>({
    queryKey: ['month', region, year, month, lat, lon],
    queryFn: () => api.getMonth(year, month, region, lat, lon),
    staleTime: 7 * 24 * 60 * 60 * 1000,
    gcTime: 30 * 24 * 60 * 60 * 1000,
    placeholderData: (prev) => prev,
  })
}
