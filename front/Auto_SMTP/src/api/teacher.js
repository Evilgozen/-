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
  
  // 添加教师
  addTeacher: (teacher) => api.post('/', teacher),
  
  // 更新教师
  updateTeacher: (id, teacher) => api.put(`/${id}`, teacher),
  
  // 删除教师
  deleteTeacher: (id) => api.delete(`/${id}`),
  
  // 按学校层次筛选教师
  getTeachersBySchoolLevel: (schoolLevel) => api.post('/search/school_level', { school_level: schoolLevel }),
  
  // 按学校筛选教师
  getTeachersBySchool: (school) => api.post('/search/school', { school: school }),
  
  // 按学院筛选教师 (保留兼容性)
  getTeachersByCollege: (college) => api.get(`/college/${college}`),
  
  // 按研究方向筛选教师 (保留兼容性)
  getTeachersByResearch: (research) => api.get(`/research/${research}`)
}

export default teacherApi