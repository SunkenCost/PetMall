import axios from 'axios'

axios.defaults.baseURL = '/'
axios.defaults.headers.post["Content-Type"] = 'application/json'
axios.defaults.timeout = 60000
axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';

export default axios
