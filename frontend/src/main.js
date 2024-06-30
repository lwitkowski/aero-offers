import VueGtag from 'vue-gtag';
import vSelect from 'vue-select';
import ToastService from 'primevue/toastservice';
import PrimeVue from 'primevue/config';
import App from './App.vue';
import router from './router';

import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';

import { createApp, h } from 'vue'

const app = createApp({
  render: () => h(App)
});

app.component('v-select', vSelect);
app.use(router);
app.use(VueGtag, {
  config: { id: 'UA-154630401-1' },
}, router);
app.use(require('vue-chartist'), {
  messageNoData: 'Not enough data for display',
});

app.use(PrimeVue);
app.use(ToastService);

app.mount('#app');