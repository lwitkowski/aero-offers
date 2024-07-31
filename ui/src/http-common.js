import axios from 'axios' /* eslint-disable */

const baseURL = import.meta.env.VITE_API_URI

const HTTP = axios.create({ baseURL })

export { HTTP as default }
