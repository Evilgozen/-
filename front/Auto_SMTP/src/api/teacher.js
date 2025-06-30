import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/teacher',
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

export const teacherApi = {
  // 获取所有教师
  getAllTeachers: () => api.get('/'),
  
  // 获取单个教师
  getTeacher: (id) => api.get(`/${id}`),
  
  // 按学院筛选教师
  getTeachersByCollege: (college) => api.get(`/college/${college}`),
  
  // 按研究方向筛选教师
  getTeachersByResearch: (research) => api.get(`/research/${research}`)
}

export default teacherApi