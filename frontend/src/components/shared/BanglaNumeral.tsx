import { toBanglaNumeral } from '../../utils/banglaNumeral'

interface Props {
  value: number | string
  className?: string
}

/** Renders a number using Bengali numerals with the Bengali font. */
export function BanglaNumeral({ value, className }: Props) {
  return (
    <span className={className} lang="bn" dir="ltr">
      {toBanglaNumeral(value)}
    </span>
  )
}
