<template>
  <div class="teacher-container">
    <a-card title="教师信息" class="teacher-card">
      <template #extra>
        <a-space>
          <a-badge :count="cartStore.cartCount" :offset="[10, 0]">
            <a-button type="primary" @click="showCart">
              <ShoppingCartOutlined /> 购物车
            </a-button>
          </a-badge>
          <a-button type="default" @click="goToSMTP" :disabled="cartStore.cartCount === 0">
            去结算
          </a-button>
        </a-space>
      </template>
      <!-- 筛选条件 -->
      <div class="filter-section" style="margin-bottom: 24px;">
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="学校层次">
              <a-select
                v-model:value="selectedSchoolLevel"
                placeholder="选择学校层次"
                allowClear
                @change="onSchoolLevelChange"
                style="width: 100%"
              >
                <a-select-option value="中9">中9</a-select-option>
                <a-select-option value="次9">次9</a-select-option>
                <a-select-option value="末9">末9</a-select-option>
                <a-select-option value="其它">其它</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="学校">
              <a-select
                v-model:value="selectedSchool"
                placeholder="选择学校"
                allowClear
                @change="onSchoolChange"
                style="width: 100%"
              >
                <a-select-option value="华东师范大学">华东师范大学</a-select-option>
                <a-select-option value="吉林大学">吉林大学</a-select-option>
                <a-select-option value="东北大学">东北大学</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="操作">
              <a-space>
                <a-button type="primary" @click="fetchAllTeachers" :loading="loading">
                  显示全部
                </a-button>
                <a-button @click="resetFilters">
                  重置筛选
                </a-button>
              </a-space>
            </a-form-item>
          </a-col>
        </a-row>
      </div>
      
      <a-spin :spinning="loading" tip="加载中...">
        <div v-if="!loading && teachers.length === 0" class="empty-state">
          <a-empty description="暂无教师信息" />
        </div>
        <a-row :gutter="[16, 16]" v-else>
          <a-col :xs="24" :sm="12" :md="8" :lg="6" v-for="teacher in teachers" :key="teacher.id">
            <a-card
              hoverable
              class="teacher-item-card"
              :title="teacher.name"
            >
              <template #extra>
                <a-tag v-if="teacher.title" color="blue">{{ teacher.title }}</a-tag>
              </template>
              
              <div class="teacher-info">
                <div class="info-item">
                  <UserOutlined class="info-icon" />
                  <span class="info-label">姓名：</span>
                  <span class="info-value">{{ teacher.name }}</span>
                </div>
                
                <div class="info-item" v-if="teacher.school_college">
                  <BankOutlined class="info-icon" />
                  <span class="info-label">学院：</span>
                  <span class="info-value">{{ teacher.school_college }}</span>
                </div>
                
                <div class="info-item" v-if="teacher.email">
                  <MailOutlined class="info-icon" />
                  <span class="info-label">邮箱：</span>
                  <a :href="`mailto:${teacher.email}`" class="info-value email-link">
                    {{ teacher.email }}
                  </a>
                </div>
                
                <div class="info-item" v-if="teacher.url">
                  <LinkOutlined class="info-icon" />
                  <span class="info-label">主页：</span>
                  <a :href="getFullUrl(teacher.url)" target="_blank" class="info-value url-link">
                    个人主页
                  </a>
                </div>
                
                <div class="research-section" v-if="teacher.resh_dict">
                  <div class="research-title">
                    <ExperimentOutlined class="info-icon" />
                    <span class="info-label">研究方向：</span>
                  </div>
                  <div class="research-content">
                    {{ formatResearchDict(teacher.resh_dict) }}
                  </div>
                </div>
              </div>
              
              <template #actions>
                <a-space>
                  <a-button type="primary" size="small" @click="viewDetails(teacher)">
                    查看详情
                  </a-button>
                  <a-button 
                    v-if="!cartStore.isInCart(teacher.id)" 
                    type="default" 
                    size="small" 
                    @click="addToCart(teacher)"
                  >
                    <PlusOutlined /> 加入购物车
                  </a-button>
                  <a-button 
                    v-else 
                    type="default" 
                    size="small" 
                    danger
                    @click="removeFromCart(teacher.id)"
                  >
                    <MinusOutlined /> 移出购物车
                  </a-button>
                </a-space>
              </template>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>
    </a-card>
    
    <!-- 详情模态框 -->
    <a-modal
      v-model:open="detailModalVisible"
      :title="selectedTeacher?.name + ' - 详细信息'"
      width="800px"
      :footer="null"
    >
      <div v-if="selectedTeacher" class="teacher-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="姓名">
            {{ selectedTeacher.name }}
          </a-descriptions-item>
          <a-descriptions-item label="职称" v-if="selectedTeacher.title">
            <a-tag color="blue">{{ selectedTeacher.title }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="学院" v-if="selectedTeacher.school_college">
            {{ selectedTeacher.school_college }}
          </a-descriptions-item>
          <a-descriptions-item label="邮箱" v-if="selectedTeacher.email">
            <a :href="`mailto:${selectedTeacher.email}`" class="email-link">
              {{ selectedTeacher.email }}
            </a>
          </a-descriptions-item>
          <a-descriptions-item label="个人主页" v-if="selectedTeacher.url">
            <a :href="getFullUrl(selectedTeacher.url)" target="_blank" class="url-link">
              {{ getFullUrl(selectedTeacher.url) }}
            </a>
          </a-descriptions-item>
          <a-descriptions-item label="研究方向" v-if="selectedTeacher.resh_dict">
            <div class="research-detail">
              {{ formatResearchDict(selectedTeacher.resh_dict) }}
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

    <!-- 购物车模态框 -->
    <a-modal
      v-model:open="cartModalVisible"
      title="教师购物车"
      width="800px"
      :footer="null"
    >
      <div class="cart-content">
        <div class="cart-header">
          <a-space>
            <span>已选择 {{ cartStore.cartCount }} 位教师</span>
            <a-button size="small" @click="clearCart" v-if="cartStore.cartCount > 0">
              清空购物车
            </a-button>
          </a-space>
        </div>
        
        <div v-if="cartStore.cartCount === 0" class="empty-cart">
          <a-empty description="购物车为空" />
        </div>
        
        <div v-else class="cart-list">
          <a-list :data-source="cartStore.cartTeachers" item-layout="horizontal">
            <template #renderItem="{ item }">
              <a-list-item>
                <template #actions>
                  <a-button size="small" danger @click="removeFromCart(item.id)">
                    <MinusOutlined /> 移除
                  </a-button>
                </template>
                <a-list-item-meta>
                  <template #title>
                    <span>{{ item.name }}</span>
                    <a-tag v-if="item.title" color="blue" style="margin-left: 8px">
                      {{ item.title }}
                    </a-tag>
                  </template>
                  <template #description>
                    <div>
                      <div v-if="item.school_college">
                        <BankOutlined /> {{ item.school_college }}
                      </div>
                      <div v-if="item.email">
                        <MailOutlined /> {{ item.email }}
                      </div>
                    </div>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </div>
        
        <div class="cart-footer" v-if="cartStore.cartCount > 0">
          <a-space>
            <a-button type="primary" size="large" @click="goToSMTP">
              去发送邮件 ({{ cartStore.cartCount }})
            </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { teacherApi } from '../api/teacher'
import { useTeacherCartStore } from '../stores/teacherCart'
import {
  UserOutlined,
  BankOutlined,
  MailOutlined,
  LinkOutlined,
  ExperimentOutlined,
  ShoppingCartOutlined,
  PlusOutlined,
  MinusOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const teachers = ref([])
const loading = ref(false)
const detailModalVisible = ref(false)
const selectedTeacher = ref(null)
const selectedSchoolLevel = ref(undefined)
const selectedSchool = ref(undefined)
const cartModalVisible = ref(false)

// 路由和store
const router = useRouter()
const cartStore = useTeacherCartStore()

// 获取所有教师列表
const fetchAllTeachers = async () => {
  loading.value = true
  try {
    const response = await teacherApi.getAllTeachers()
    
    if (response.code === 200 && response.data) {
      // 处理嵌套数组结构：data: [[{...}, {...}]]
      const teacherData = response.data
      if (Array.isArray(teacherData) && teacherData.length > 0 && Array.isArray(teacherData[0])) {
        teachers.value = teacherData[0] // 取第一个数组中的教师数据
      } else if (Array.isArray(teacherData)) {
        teachers.value = teacherData // 如果是普通数组格式
      } else {
        teachers.value = []
      }
      message.success(`成功加载 ${teachers.value.length} 位教师信息`)
    } else {
      teachers.value = []
      message.warning('未获取到教师信息')
    }
  } catch (error) {
    console.error('获取教师信息失败:', error)
    message.error('获取教师信息失败，请检查网络连接或后端服务')
    teachers.value = []
  } finally {
    loading.value = false
  }
}

// 按学校层次筛选教师
const fetchTeachersBySchoolLevel = async (schoolLevel) => {
  loading.value = true
  try {
    const response = await teacherApi.getTeachersBySchoolLevel(schoolLevel)
    
    if (response.code === 200 && response.data) {
      // 处理嵌套数组结构：data: [[{...}, {...}]]
      const teacherData = response.data
      if (Array.isArray(teacherData) && teacherData.length > 0 && Array.isArray(teacherData[0])) {
        teachers.value = teacherData[0] // 取第一个数组中的教师数据
      } else if (Array.isArray(teacherData)) {
        teachers.value = teacherData // 如果是普通数组格式
      } else {
        teachers.value = []
      }
      message.success(`找到 ${teachers.value.length} 位 "${schoolLevel}" 层次的教师`)
    } else {
      teachers.value = []
      message.warning(`未找到 "${schoolLevel}" 层次的教师`)
    }
  } catch (error) {
    console.error('筛选教师失败:', error)
    message.error('筛选教师失败，请检查网络连接或后端服务')
    teachers.value = []
  } finally {
    loading.value = false
  }
}

// 按学校筛选教师
const fetchTeachersBySchool = async (school) => {
  loading.value = true
  try {
    const response = await teacherApi.getTeachersBySchool(school)
    
    if (response.code === 200 && response.data) {
      // 处理嵌套数组结构：data: [[{...}, {...}]]
      const teacherData = response.data
      if (Array.isArray(teacherData) && teacherData.length > 0 && Array.isArray(teacherData[0])) {
        teachers.value = teacherData[0] // 取第一个数组中的教师数据
      } else if (Array.isArray(teacherData)) {
        teachers.value = teacherData // 如果是普通数组格式
      } else {
        teachers.value = []
      }
      message.success(`找到 ${teachers.value.length} 位来自 "${school}" 的教师`)
    } else {
      teachers.value = []
      message.warning(`未找到来自 "${school}" 的教师`)
    }
  } catch (error) {
    console.error('筛选教师失败:', error)
    message.error('筛选教师失败，请检查网络连接或后端服务')
    teachers.value = []
  } finally {
    loading.value = false
  }
}

// 学校层次改变事件
const onSchoolLevelChange = (value) => {
  if (value) {
    selectedSchool.value = undefined // 清空学校选择
    fetchTeachersBySchoolLevel(value)
  } else {
    fetchAllTeachers()
  }
}

// 学校改变事件
const onSchoolChange = (value) => {
  if (value) {
    selectedSchoolLevel.value = undefined // 清空学校层次选择
    fetchTeachersBySchool(value)
  } else {
    fetchAllTeachers()
  }
}

// 重置筛选条件
const resetFilters = () => {
  selectedSchoolLevel.value = undefined
  selectedSchool.value = undefined
  fetchAllTeachers()
}

// 查看详情
const viewDetails = (teacher) => {
  selectedTeacher.value = teacher
  detailModalVisible.value = true
}

// 格式化研究方向
const formatResearchDict = (reshDict) => {
  if (!reshDict) return ''
  // 移除HTML标签和多余的符号
  return reshDict
    .replace(/>/g, '')
    .replace(/`/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

// 获取完整URL
const getFullUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) {
    return url
  }
  // 如果是相对路径，拼接华师大的域名
  return `https://faculty.ecnu.edu.cn${url}`
}

// 购物车相关方法
const addToCart = (teacher) => {
  const success = cartStore.addTeacher(teacher)
  if (success) {
    message.success(`已将 ${teacher.name} 添加到购物车`)
  } else {
    message.warning(`${teacher.name} 已在购物车中`)
  }
}

const removeFromCart = (teacherId) => {
  const teacher = cartStore.cartTeachers.find(t => t.id === teacherId)
  const success = cartStore.removeTeacher(teacherId)
  if (success && teacher) {
    message.success(`已将 ${teacher.name} 从购物车移除`)
  }
}

const showCart = () => {
  cartModalVisible.value = true
}

const goToSMTP = () => {
  if (cartStore.cartCount === 0) {
    message.warning('购物车为空，请先选择教师')
    return
  }
  router.push('/smtp')
  message.success(`已选择 ${cartStore.cartCount} 位教师，跳转到邮件发送页面`)
}

const clearCart = () => {
  cartStore.clearCart()
  message.success('购物车已清空')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAllTeachers()
})
</script>

<style scoped>
.teacher-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.teacher-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-section {
  background: #fafafa;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.filter-section .ant-form-item {
  margin-bottom: 0;
}

.filter-section .ant-form-item-label {
  font-weight: 500;
  color: #333;
}

.teacher-item-card {
  height: 100%;
  transition: all 0.3s ease;
}

.teacher-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.teacher-info {
  padding: 8px 0;
}

.info-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-icon {
  color: #1890ff;
  margin-right: 8px;
  margin-top: 2px;
  flex-shrink: 0;
}

.info-label {
  font-weight: 500;
  color: #666;
  min-width: 50px;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  flex: 1;
  word-break: break-all;
}

.email-link {
  color: #1890ff;
  text-decoration: none;
}

.email-link:hover {
  text-decoration: underline;
}

.url-link {
  color: #1890ff;
  text-decoration: none;
}

.url-link:hover {
  text-decoration: underline;
}

.research-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.research-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.research-content {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  padding-left: 24px;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.research-detail {
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

/* 购物车样式 */
.cart-content {
  padding: 16px 0;
}

.cart-header {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-cart {
  text-align: center;
  padding: 40px 0;
}

.cart-list {
  max-height: 400px;
  overflow-y: auto;
}

.cart-footer {
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
  margin-top: 16px;
  text-align: center;
}

@media (max-width: 768px) {
  .teacher-container {
    padding: 10px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-label {
    margin-bottom: 4px;
  }
  
  .research-content {
    padding-left: 0;
  }
}
</style>