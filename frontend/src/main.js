import vSelect from 'vue-select';
import ToastService from 'primevue/toastservice';
import PrimeVue from 'primevue/config';
import App from './App.vue';
import router from './router';
import { createGtm } from '@gtm-support/vue-gtm';

import 'primeicons/primeicons.css';

import { createApp, h } from 'vue'

createApp({
  render: () => h(App)
})
  .component('v-select', vSelect)

  .use(router)
  .use(require('vue-chartist'), {
    messageNoData: 'Not enough data for display',
  })
  .use(PrimeVue)
  .use(ToastService)
  .use(
    createGtm({
      id: "G-RWT46PCQ0S",
      vueRouter: router
    })
  )

  .mount('#app');
