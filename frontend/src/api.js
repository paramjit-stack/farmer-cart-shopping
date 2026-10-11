import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000' });
api.interceptors.request.use(config => { const token = localStorage.getItem('token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
export const errorText = e => { const d = e.response?.data?.detail; return typeof d === 'string' ? d : Array.isArray(d) ? d.map(x => x.msg).join(', ') : 'Request failed. Check the backend connection.'; };
