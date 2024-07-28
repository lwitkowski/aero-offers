import axios from 'axios'; /* eslint-disable */

const baseURL = process.env.VUE_APP_BASE_URI;
let HTTP = axios.create({ baseURL });

// FIXME
export function setHTTPInstance(newInstance) {
    HTTP = newInstance; /* eslint-disable */
}

export { HTTP as default };
