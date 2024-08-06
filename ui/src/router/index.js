import { createRouter, createWebHistory } from 'vue-router'
import OffersList from '../views/OffersList.vue'
import ModelDetails from '../views/ModelDetails.vue'
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
          name: 'model_details',
          component: ModelDetails,
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

      case 'model_details':
        document.title = `${to.params.manufacturer} ${to.params.model} (${to.params.aircraftType}) offers`
        break

      default:
        document.title = to.meta.title
    }
  })
})

export default router
