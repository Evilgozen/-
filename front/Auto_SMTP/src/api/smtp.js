import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/smtp',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const smtpApi = {
  // SMTP配置相关
  getConfig: () => api.get('/config'),
  addConfig: (config) => api.post('/config', config),
  updateConfig: (configId, config) => api.put(`/config/${configId}`, config),
  deleteConfig: (configId) => api.delete(`/config/${configId}`),
  testConnection: (config) => api.post('/test-connection', config),
  
  // 邮件发送相关
  sendEmail: (emailData) => api.post('/send', emailData),
  sendToTeachers: (data) => api.post('/send-to-teachers', data),
  
  // 邮件记录相关
  getEmailLogs: (params = {}) => {
    const queryParams = new URLSearchParams()
    if (params.status) queryParams.append('status', params.status)
    if (params.email) queryParams.append('email', params.email)
    if (params.limit) queryParams.append('limit', params.limit)
    
    const queryString = queryParams.toString()
    return api.get(`/logs${queryString ? '?' + queryString : ''}`)
  },
  
  getLogsByStatus: (status, limit = 100) => api.get(`/logs/status/${status}?limit=${limit}`),
  getLogsByEmail: (email, limit = 100) => api.get(`/logs/email/${email}?limit=${limit}`)
}

export default smtpApi