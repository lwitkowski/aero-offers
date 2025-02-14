import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import OfferThumb from '../OfferThumb.vue'

describe('OfferThumb', () => {
  it('renders properly', () => {
    const offer = {
      category: 'glider',
      published_at: '2020-02-26',
      id: 2164,
      location: 'Edlb, L\u00fcdinghausen, Nordrhein-Westfalen, Germany',
      manufacturer: 'Rolladen Schneider',
      model: 'LS4',
      price: {
        amount: '28000.00',
        amount_in_euro: '28000.00',
        currency: 'EUR',
        exchange_rate: 1.0
      },
      title: 'LS-4',
      url: 'https://www.segelflug.de/osclass/index.php?page=item&id=42370'
    }

    const wrapper = mount(OfferThumb, { props: { offer: offer } })

    expect(wrapper.text()).toContain('LS4', '2020-02-26', '€28,000')
  })
})
