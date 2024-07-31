import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URI

const HTTP = axios.create({ baseURL })

export { HTTP as default }
