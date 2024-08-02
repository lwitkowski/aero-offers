import { createRouter, createWebHistory } from 'vue-router'
import OffersList from '../views/OffersList.vue'
import OfferDetails from '../views/OfferDetails.vue'
import { nextTick } from 'vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'all_listing',
      component: OffersList,
      meta: {
        title: 'Aircraft Offers Overview',
        description:
          'Aircraft Offers from various marketplaces. Ranging from Gliders like ASK21 to Cessna and much more (Gliders, TMG, Ultralight, Airplanes)'
      },
      props: true
    },
    {
      path: '/:aircraftType',
      name: 'category_listing',
      children: [
        {
          path: '/:aircraftType',
          component: OffersList,
          props: true
        },
        {
          path: '/:aircraftType/:manufacturer/:model',
          name: 'offer_details',
          component: OfferDetails,
          props: true
        }
      ]
    }
  ]
})

router.afterEach((to) => {
  nextTick(() => {
    if (to.name === 'offer_details') {
      document.title = `${to.params.aircraftType} ${to.params.manufacturer} ${to.params.model}`
    } else {
      document.title = to.meta.title
    }
  })
})

export default router
