import type { Tradition } from '../api/types'

/** Tailwind color classes for each tradition. */
export const TRADITION_COLORS: Record<Tradition, { dot: string; badge: string; label: string }> = {
  hindu: {
    dot: 'bg-orange-500',
    badge: 'bg-orange-100 text-orange-800 border-orange-300',
    label: 'হিন্দু',
  },
}
