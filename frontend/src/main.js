import vSelect from 'vue-select';
import ToastService from 'primevue/toastservice';
import PrimeVue from 'primevue/config';
import App from './App.vue';
import router from './router';

import 'primeicons/primeicons.css';

import { createApp, h } from 'vue'

const app = createApp({
  render: () => h(App)
});

app.component('v-select', vSelect);
app.use(router);
app.use(require('vue-chartist'), {
  messageNoData: 'Not enough data for display',
});

app.use(PrimeVue);
app.use(ToastService);

app.mount('#app');
