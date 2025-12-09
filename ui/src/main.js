import { createApp, h } from 'vue'
import axios from 'axios'
import vueChartist from 'vue-chartist'

import App from './App.vue'
import router from './router'

axios.defaults.baseURL = import.meta.env.VITE_API_URI
console.log('API: ', axios.defaults.baseURL)

const app = createApp({
  render: () => h(App)
})

app.use(router)
app.use(vueChartist)
app.mount('#app')
