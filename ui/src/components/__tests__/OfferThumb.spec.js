import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import OfferThumb from '../OfferThumb.vue'

describe('OfferThumb', () => {
  it('renders properly', () => {
    const offer = {
      aircraft_typ: 'glider',
      classified: true,
      creationDate: 'Thu, 27 Feb 2020 05:00:09 GMT',
      currency: '\u20ac',
      currency_code: 'EUR',
      date: '2020-02-26',
      exchange_rate: '1.0',
      id: 2164,
      location: 'Edlb, L\u00fcdinghausen, Nordrhein-Westfalen, Germany',
      manufacturer: 'Rolladen Schneider',
      model: 'LS4',
      price: '28000.00',
      price_in_euro: '28000.00',
      title: 'LS-4',
      url: 'https://www.segelflug.de/osclass/index.php?page=item&id=42370'
    }

    const wrapper = mount(OfferThumb, { props: { offer: offer } })

    expect(wrapper.text()).toContain('Rolladen Schneider LS4', '2020-02-26')
  })
})
