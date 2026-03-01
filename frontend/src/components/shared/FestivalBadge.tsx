import type { Festival } from '../../api/types'
import { TRADITION_COLORS } from '../../utils/festivalColors'

interface Props {
  festival: Festival
}

export function FestivalBadge({ festival }: Props) {
  const colors = TRADITION_COLORS[festival.tradition]
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs border font-medium ${colors.badge}`}
      lang="bn"
    >
      {festival.name_bn}
      {festival.is_public_holiday && (
        <span className="ml-1 text-xs opacity-70">★</span>
      )}
    </span>
  )
}
