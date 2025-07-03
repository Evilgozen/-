import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/files',
  timeout: 30000, // 文件上传可能需要更长时间
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('File API Error:', error)
    return Promise.reject(error)
  }
)

export const fileApi = {
  // 文件上传
  uploadFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 获取文件列表
  getFilesList: () => api.get('/list'),
  
  // 获取文件信息
  getFileInfo: (fileId) => api.get(`/info/${fileId}`),
  
  // 删除文件
  deleteFile: (fileId) => api.delete(`/delete/${fileId}`),
  
  // 下载文件
  downloadFile: (fileId) => {
    return api.get(`/download/${fileId}`, {
      responseType: 'blob'
    })
  }
}