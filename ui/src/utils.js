export default function formatPrice(input, currency) {
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
