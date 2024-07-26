import axios from 'axios'; /* eslint-disable */

const baseURL = '/api/';
let HTTP = axios.create({ baseURL });

// FIXME
export function setHTTPInstance(newInstance) {
    HTTP = newInstance; /* eslint-disable */
}

export { HTTP as default };
