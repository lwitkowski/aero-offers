import { createApp, h } from 'vue'
import vSelect from 'vue-select'
import ToastService from 'primevue/toastservice'
import vueChartist from 'vue-chartist'
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'

const app = createApp({
  render: () => h(App)
})

app.component('VSelect', vSelect)
app.use(router)
app.use(vueChartist)
app.use(PrimeVue)
app.use(ToastService)
app.mount('#app')
