export function formatPrice(input, currency) {
  try {
    let n = Number(input)
    return n.toLocaleString(navigator.languages[0] || 'en', {
      style: 'currency',
      currency: currency || 'EUR',
      maximumFractionDigits: 0
    })
  } catch {
    return input
  }
}
export function median(values) {
  if (values.length === 0) {
    throw new Error('Input array is empty')
  }

  values.sort((a, b) => a - b)

  const half = Math.floor(values.length / 2)

  return values.length % 2 ? values[half] : (values[half - 1] + values[half]) / 2
}
export default {}
