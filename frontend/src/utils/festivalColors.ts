import type { Tradition } from '../api/types'

/** Tailwind color classes for each tradition. */
export const TRADITION_COLORS: Record<Tradition, { dot: string; badge: string; label: string }> = {
  hindu: {
    dot: 'bg-orange-500',
    badge: 'bg-orange-100 text-orange-800 border-orange-300',
    label: 'হিন্দু',
  },
  muslim: {
    dot: 'bg-green-600',
    badge: 'bg-green-100 text-green-800 border-green-300',
    label: 'মুসলিম',
  },
  buddhist: {
    dot: 'bg-yellow-500',
    badge: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    label: 'বৌদ্ধ',
  },
  christian: {
    dot: 'bg-blue-500',
    badge: 'bg-blue-100 text-blue-800 border-blue-300',
    label: 'খ্রিস্টান',
  },
  civic: {
    dot: 'bg-red-600',
    badge: 'bg-red-100 text-red-800 border-red-300',
    label: 'জাতীয়',
  },
}
