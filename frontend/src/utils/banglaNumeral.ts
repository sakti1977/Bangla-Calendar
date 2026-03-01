const BANGLA_DIGITS = '০১২৩৪৫৬৭৮৯'

export function toBanglaNumeral(n: number | string): string {
  return String(n)
    .split('')
    .map((ch) => (ch >= '0' && ch <= '9' ? BANGLA_DIGITS[parseInt(ch)] : ch))
    .join('')
}

export function toArabicNumeral(s: string): string {
  return s
    .split('')
    .map((ch) => {
      const idx = BANGLA_DIGITS.indexOf(ch)
      return idx !== -1 ? String(idx) : ch
    })
    .join('')
}
