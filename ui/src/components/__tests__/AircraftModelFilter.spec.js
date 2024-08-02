import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AircraftModelFilter from '../AircraftModelFilter.vue'

const models = {
  AlexanderSchleicher: {
    models: {
      glider: ['ASW 15', 'ASW 17', 'ASW 19', 'ASW 20'],
      tmg: ['ASK 14', 'ASK 16']
    }
  },
  Antonov: {
    models: {
      airplane: ['An-2', 'An-225 Mriya']
    }
  }
}

const mockRouter = {
  push: function () {}
}
const mockRoute = {
  path: '/'
}

function mocksWithPath(path) {
  mockRoute.path = path
  return {
    mocks: {
      $route: mockRoute,
      $router: mockRouter
    }
  }
}

describe('AircraftModelFilter', () => {
  it('should list all categories for homepage', () => {
    const wrapper = mount(AircraftModelFilter, {
      props: { models: models },
      global: mocksWithPath('/')
    })

    expect(wrapper.text())
      .toContain('AlexanderSchleicher', 'ASW 15', 'ASK 16') // both glider and tmg
      .toContain('Antonov', 'An-2', 'An-225 Mriya') // airplanes
  })

  it('should list only gliders on /glider', () => {
    const wrapper = mount(AircraftModelFilter, {
      props: { models: models },
      global: mocksWithPath('/glider')
    })

    expect(wrapper.text())
      .toContain('AlexanderSchleicher', 'ASW 15')
      .not.toContain('ASK 16', 'Antonov', 'An-2', 'An-225 Mriya')
  })
})
