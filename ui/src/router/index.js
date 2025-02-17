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
      path: '/:category',
      children: [
        {
          path: '/:category',
          name: 'offers_for_category',
          component: OffersList,
          props: true
        },
        {
          path: '/:category/:manufacturer/:model',
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
      case 'offers_for_category':
        document.title = `${to.params.category.charAt(0).toUpperCase()}${to.params.category.slice(1)} offers`
        break

      case 'model_details':
        document.title = `${to.params.manufacturer} ${to.params.model} (${to.params.category}) offers`
        break

      default:
        document.title = to.meta.title
    }
  })
})

export default router
