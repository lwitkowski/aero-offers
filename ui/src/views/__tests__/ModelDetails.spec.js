import { describe, it, expect } from 'vitest'
import axios from 'axios'
import { mount } from '@vue/test-utils'
import ModelDetails from '../ModelDetails.vue'
import { vi } from 'vitest'

import offers_response from '@/views/__tests__/offers_resp.json'

vi.mock('axios')

describe('ModelDetails', () => {
  it('renders median and avg prices properly', async () => {
    vi.mocked(axios).get.mockResolvedValue({ data: offers_response })

    const wrapper = mount(ModelDetails, {
      props: { manufacturer: 'Rolladen Schneider', model: 'LS-4' }
    })
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalled())

    expect(wrapper.text()).toContain('There were 3 offer(s). Median offer price is €45,000, average €43,500')
  })
})
