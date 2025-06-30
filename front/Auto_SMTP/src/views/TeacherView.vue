<template>
  <div class="teacher-container">
    <a-card title="教师信息" class="teacher-card">
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
                <a-button type="primary" size="small" @click="viewDetails(teacher)">
                  查看详情
                </a-button>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import {
  UserOutlined,
  BankOutlined,
  MailOutlined,
  LinkOutlined,
  ExperimentOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const teachers = ref([])
const loading = ref(false)
const detailModalVisible = ref(false)
const selectedTeacher = ref(null)

// API基础URL
const API_BASE_URL = 'http://127.0.0.1:8000'

// 获取教师列表
const fetchTeachers = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/teacher/`, {
      headers: {
        'accept': 'application/json'
      }
    })
    
    if (response.data && response.data.data) {
      // 处理嵌套数组结构：data: [[{...}, {...}]]
      const teacherData = response.data.data
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

// 组件挂载时获取数据
onMounted(() => {
  fetchTeachers()
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