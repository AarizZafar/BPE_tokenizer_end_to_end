import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 300000,
})

export function getErrorMessage(error) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map(item => `${item.loc?.join('.')}: ${item.msg}`).join('; ')
  }
  return detail || error.message
}

export default api
