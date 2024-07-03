import axios from 'axios'; /* eslint-disable */

const baseURL = 'http://127.0.0.1:5000/'; // is now done via proxy
let HTTP = axios.create({ baseURL });

// FIXME
export function setHTTPInstance(newInstance) {
    HTTP = newInstance; /* eslint-disable */
}

export { HTTP as default };
