import { createRouter, createWebHistory } from 'vue-router'
import OffersList from '../views/OffersList.vue'
import OfferDetails from '../views/OfferDetails.vue'
import { nextTick } from 'vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'all_offers',
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
      children: [
        {
          path: '/:aircraftType',
          name: 'offers_for_type',
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
    switch (to.name) {
      case 'offers_for_type':
        document.title = `${to.params.aircraftType.charAt(0).toUpperCase()}${to.params.aircraftType.slice(1)} offers`
        break

      case 'offer_details':
        document.title = `${to.params.manufacturer} ${to.params.model} (${to.params.aircraftType}) offers`
        break

      default:
        document.title = to.meta.title
    }
  })
})

export default router
