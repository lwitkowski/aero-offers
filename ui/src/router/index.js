import { createRouter, createWebHistory } from 'vue-router'
import Offers from '../views/Offers.vue'
import ModelInformation from '../views/ModelInformation.vue'
import { nextTick } from 'vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'All Offers',
      component: Offers,
      meta: {
        title: 'Aircraft Offers Overview',
        description:
          'Aircraft Offers from various marketplaces. Ranging from Gliders like ASK21 to Cessna and much more (Gliders, TMG, Ultralight, Airplanes)'
      },
      props: {
        filter: ''
      }
    },
    {
      path: '/gliders',
      name: 'Glider Offers',
      component: Offers,
      meta: {
        title: 'Aircraft Offers - Glider Offers',
        description: 'Glider Offers from various marketplaces with prices in EUR.'
      },
      props: {
        filter: 'aircraft_type=glider'
      }
    },
    {
      path: '/tmg',
      name: 'Touring Motorglider Offers',
      component: Offers,
      meta: {
        title: 'Aircraft Offers - Touring Motor Glider Offers',
        description:
          'Touring Motor Glider (like Super Dimona, Stemme) offers from various marketplaces with prices in EUR.'
      },
      props: {
        filter: 'aircraft_type=tmg'
      }
    },
    {
      path: '/ultralight',
      name: 'Ultralight Offers',
      component: Offers,
      meta: {
        title: 'Aircraft Offers - Ultralights',
        description: 'Ultralight (like C42) offers from various marketplaces with prices in EUR.'
      },
      props: {
        filter: 'aircraft_type=ultralight'
      }
    },
    {
      path: '/airplane',
      name: 'Airplane Offers',
      component: Offers,
      meta: {
        title: 'Aircraft Offers - Airplanes',
        description: 'Small Airplane (like Cessna) offers from various marketplaces with prices in EUR.'
      },
      props: {
        filter: 'aircraft_type=airplane'
      }
    },
    {
      path: '/model/:manufacturer/:model',
      name: 'ModelInformation',
      component: ModelInformation,
      props: true
    }
  ]
})

router.afterEach((to) => {
  nextTick(() => {
    // calculate title for ModelInformation dynamically
    if (to.name === 'ModelInformation') {
      document.title = `Model ${to.params.manufacturer} ${to.params.model}`
    } else {
      document.title = to.meta.title
    }
  })
})

export default router
