import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTeacherCartStore = defineStore('teacherCart', () => {
  // 购物车中的教师列表
  const cartTeachers = ref([])
  
  // 计算属性：购物车中教师数量
  const cartCount = computed(() => cartTeachers.value.length)
  
  // 计算属性：获取所有教师邮箱
  const cartEmails = computed(() => cartTeachers.value.map(teacher => teacher.email))
  
  // 计算属性：获取所有教师ID
  const cartTeacherIds = computed(() => cartTeachers.value.map(teacher => teacher.id))
  
  // 添加教师到购物车
  const addTeacher = (teacher) => {
    // 检查是否已存在
    const exists = cartTeachers.value.find(t => t.id === teacher.id)
    if (!exists) {
      cartTeachers.value.push({
        id: teacher.id,
        name: teacher.name,
        email: teacher.email,
        title: teacher.title,
        school_college: teacher.school_college
      })
      return true
    }
    return false
  }
  
  // 从购物车移除教师
  const removeTeacher = (teacherId) => {
    const index = cartTeachers.value.findIndex(t => t.id === teacherId)
    if (index > -1) {
      cartTeachers.value.splice(index, 1)
      return true
    }
    return false
  }
  
  // 检查教师是否在购物车中
  const isInCart = (teacherId) => {
    return cartTeachers.value.some(t => t.id === teacherId)
  }
  
  // 清空购物车
  const clearCart = () => {
    cartTeachers.value = []
  }
  
  // 批量添加教师
  const addMultipleTeachers = (teachers) => {
    let addedCount = 0
    teachers.forEach(teacher => {
      if (addTeacher(teacher)) {
        addedCount++
      }
    })
    return addedCount
  }
  
  return {
    cartTeachers,
    cartCount,
    cartEmails,
    cartTeacherIds,
    addTeacher,
    removeTeacher,
    isInCart,
    clearCart,
    addMultipleTeachers
  }
})