import { useQuery } from '@tanstack/react-query'
import { api } from '../client'
import type { DateInfo, Region } from '../types'

export function useDateInfo(
  dateStr: string | null,
  region: Region,
  lat?: number,
  lon?: number,
  includePanchanga = true
) {
  return useQuery<DateInfo>({
    queryKey: ['dateInfo', dateStr, region, lat, lon, includePanchanga],
    queryFn: () =>
      api.getDateInfo({
        date: dateStr!,
        region,
        lat,
        lon,
        include_panchanga: includePanchanga,
      }),
    enabled: !!dateStr,
    staleTime: 24 * 60 * 60 * 1000,
  })
}
