<template>
  <a-card title="邮件发送" class="email-sender-card">
    <template #extra>
      <a-space>
        <a-button 
          type="primary" 
          :loading="sendLoading" 
          @click="sendEmail"
          :disabled="!smtpConfigured || !isFormValid"
        >
          发送邮件
        </a-button>
        <a-button 
          type="default" 
          @click="resetForm"
        >
          重置
        </a-button>
      </a-space>
    </template>
    
    <a-alert
      v-if="!smtpConfigured"
      message="请先配置SMTP服务器"
      type="warning"
      show-icon
      style="margin-bottom: 16px"
    />
    
    <a-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      layout="vertical"
      @finish="onFinish"
    >
      <!-- 发送模式选择 -->
      <a-form-item label="发送模式">
        <a-radio-group v-model:value="sendMode" @change="onSendModeChange">
          <a-radio value="custom">自定义收件人</a-radio>
          <a-radio value="teachers">发送给教师</a-radio>
        </a-radio-group>
      </a-form-item>
      
      <!-- 自定义收件人模式 -->
      <div v-if="sendMode === 'custom'">
        <a-form-item label="收件人" name="to_emails">
          <a-select
            v-model:value="formData.to_emails"
            mode="tags"
            placeholder="输入邮箱地址，按回车添加"
            :token-separators="[',', ';']"
            style="width: 100%"
          >
          </a-select>
        </a-form-item>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="抄送 (可选)" name="cc_emails">
              <a-select
                v-model:value="formData.cc_emails"
                mode="tags"
                placeholder="输入抄送邮箱"
                :token-separators="[',', ';']"
                style="width: 100%"
              >
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="密送 (可选)" name="bcc_emails">
              <a-select
                v-model:value="formData.bcc_emails"
                mode="tags"
                placeholder="输入密送邮箱"
                :token-separators="[',', ';']"
                style="width: 100%"
              >
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
      </div>
      
      <!-- 教师选择模式 -->
      <div v-if="sendMode === 'teachers'">
        <!-- 购物车状态提示 -->
        <div v-if="cartStore.cartCount > 0" style="margin-bottom: 16px;">
          <a-alert
            :message="`购物车中有 ${cartStore.cartCount} 位教师`"
            type="info"
            show-icon
            closable
          >
            <template #action>
              <a-button size="small" type="link" @click="loadFromCart">
                加载到选择列表
              </a-button>
            </template>
          </a-alert>
        </div>
        
        <a-form-item label="选择教师" name="teacher_ids">
          <a-spin :spinning="teachersLoading">
            <a-select
              v-model:value="formData.teacher_ids"
              mode="multiple"
              placeholder="选择要发送邮件的教师"
              style="width: 100%"
              :filter-option="filterTeacher"
              show-search
            >
              <a-select-option 
                v-for="teacher in teachers" 
                :key="teacher.id" 
                :value="teacher.id"
              >
                {{ teacher.name }} ({{ teacher.email }})
              </a-select-option>
            </a-select>
          </a-spin>
        </a-form-item>
      </div>
      
      <a-form-item label="邮件主题" name="subject">
        <a-input 
          v-model:value="formData.subject" 
          placeholder="请输入邮件主题"
        />
      </a-form-item>
      
      <a-form-item label="邮件内容" name="body">
        <a-textarea 
          v-model:value="formData.body" 
          placeholder="请输入邮件内容，可使用 {{姓名}} 作为占位符进行个性化替换"
          :rows="6"
          show-count
          :maxlength="5000"
        />
        <div v-if="sendMode === 'teachers'" style="margin-top: 8px;">
          <a-tag color="blue">提示：使用 {{姓名}} 可在群发时自动替换为教师姓名</a-tag>
        </div>
      </a-form-item>
      
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item>
            <a-checkbox v-model:checked="formData.is_html">
              HTML格式
            </a-checkbox>
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item>
            <a-button 
              type="link" 
              size="small"
              @click="insertNamePlaceholder"
              v-if="sendMode === 'teachers'"
            >
              插入姓名占位符
            </a-button>
          </a-form-item>
        </a-col>
      </a-row>
      
      <!-- 附件管理 -->
      <a-form-item label="附件管理">
        <!-- 文件上传 -->
        <div style="margin-bottom: 16px;">
          <a-upload
            v-model:file-list="fileList"
            :before-upload="beforeUpload"
            :on-remove="handleRemove"
            multiple
            :show-upload-list="false"
          >
            <a-button>
              <upload-outlined />
              上传文件
            </a-button>
          </a-upload>
          <div class="upload-hint">单个文件不超过10MB</div>
        </div>
        
        <!-- 已上传文件列表 -->
        <div v-if="uploadedFiles.length > 0">
          <a-divider orientation="left" style="margin: 16px 0;">选择附件</a-divider>
          <div class="file-list">
            <a-card 
              v-for="file in uploadedFiles" 
              :key="file.id"
              size="small"
              :class="['file-item', { 'selected': isFileSelected(file) }]"
              @click="selectAttachment(file)"
            >
              <div class="file-info">
                <div class="file-name">{{ file.filename }}</div>
                <div class="file-meta">
                  <span>{{ (file.size / 1024).toFixed(1) }} KB</span>
                  <span>{{ new Date(file.upload_time).toLocaleString() }}</span>
                </div>
              </div>
              <div class="file-actions">
                <a-checkbox :checked="isFileSelected(file)" />
              </div>
            </a-card>
          </div>
        </div>
        
        <!-- 已选择的附件 -->
        <div v-if="selectedAttachments.length > 0">
          <a-divider orientation="left" style="margin: 16px 0;">已选择附件 ({{ selectedAttachments.length }})</a-divider>
          <a-tag 
            v-for="file in selectedAttachments" 
            :key="file.id"
            closable
            @close="selectAttachment(file)"
            style="margin: 4px;"
          >
            {{ file.filename }}
          </a-tag>
        </div>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<style scoped>
.upload-hint {
  margin-top: 8px;
  color: #666;
  font-size: 12px;
}

.file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.file-item {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.file-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}

.file-item.selected {
  border-color: #1890ff;
  background-color: #f0f8ff;
}

.file-item :deep(.ant-card-body) {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #8c8c8c;
}

.file-actions {
  margin-left: 12px;
}

@media (max-width: 768px) {
  .file-list {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { smtpApi } from '../../api/smtp'
import { teacherApi } from '../../api/teacher'
import { fileApi } from '../../api/file'
import { useTeacherCartStore } from '../../stores/teacherCart'

const props = defineProps({
  smtpConfigured: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['email-sent'])

const formRef = ref()
const cartStore = useTeacherCartStore()
const sendLoading = ref(false)
const teachersLoading = ref(false)
const sendMode = ref('custom')
const teachers = ref([])
const fileList = ref([])
const uploadedFiles = ref([])
const selectedAttachments = ref([])

const formData = reactive({
  to_emails: [],
  cc_emails: [],
  bcc_emails: [],
  teacher_ids: [],
  subject: '',
  body: '',
  is_html: false,
  attachment_ids: []
})

const rules = computed(() => {
  const baseRules = {
    subject: [
      { required: true, message: '请输入邮件主题', trigger: 'blur' }
    ],
    body: [
      { required: true, message: '请输入邮件内容', trigger: 'blur' }
    ]
  }
  
  if (sendMode.value === 'custom') {
    baseRules.to_emails = [
      { required: true, message: '请输入收件人邮箱', trigger: 'change' },
      { type: 'array', min: 1, message: '至少需要一个收件人', trigger: 'change' }
    ]
  } else {
    baseRules.teacher_ids = [
      { required: true, message: '请选择教师', trigger: 'change' },
      { type: 'array', min: 1, message: '至少需要选择一位教师', trigger: 'change' }
    ]
  }
  
  return baseRules
})

const isFormValid = computed(() => {
  if (sendMode.value === 'custom') {
    return formData.to_emails.length > 0 && formData.subject && formData.body
  } else {
    return formData.teacher_ids.length > 0 && formData.subject && formData.body
  }
})

// 加载教师列表
const loadTeachers = async () => {
  teachersLoading.value = true
  try {
    const response = await teacherApi.getAllTeachers()
    if (response.code === 200 && response.data) {
      // 处理嵌套数组结构
      let teacherData = response.data
      if (Array.isArray(teacherData) && teacherData.length > 0 && Array.isArray(teacherData[0])) {
        teacherData = teacherData[0]
      }
      teachers.value = teacherData.filter(teacher => teacher.email)
    }
  } catch (error) {
    message.error('加载教师列表失败')
  } finally {
    teachersLoading.value = false
  }
}

// 教师筛选
const filterTeacher = (input, option) => {
  const teacher = teachers.value.find(t => t.id === option.value)
  if (!teacher) return false
  
  const searchText = input.toLowerCase()
  return teacher.name.toLowerCase().includes(searchText) || 
         teacher.email.toLowerCase().includes(searchText)
}

// 发送模式改变
const onSendModeChange = () => {
  // 清空相关字段
  formData.to_emails = []
  formData.cc_emails = []
  formData.bcc_emails = []
  formData.teacher_ids = []
  
  // 如果切换到教师模式，加载教师列表
  if (sendMode.value === 'teachers') {
    if (teachers.value.length === 0) {
      loadTeachers()
    }
    // 自动从购物车加载教师ID
    loadFromCart()
  }
}

// 从购物车加载教师数据
const loadFromCart = () => {
  if (cartStore.cartCount > 0) {
    formData.teacher_ids = [...cartStore.cartTeacherIds]
    message.success(`已从购物车加载 ${cartStore.cartCount} 位教师`)
  }
}

// 附件处理
const beforeUpload = async (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('文件大小不能超过10MB!')
    return false
  }
  
  try {
    console.log('开始上传文件:', file.name)
    // 上传文件到后端
    const response = await fileApi.uploadFile(file)
    console.log('文件上传响应:', response)
    
    if (response.error === false) {
      console.log('文件上传成功，返回数据:', response.data)
      // 添加到已上传文件列表
      uploadedFiles.value.push(response.data)
      console.log('添加文件到列表后，当前uploadedFiles:', uploadedFiles.value)
      message.success(`文件 ${file.name} 上传成功`)
      // 重新加载文件列表以确保数据同步
      console.log('重新加载文件列表...')
      await loadUploadedFiles()
    } else {
      console.log('文件上传失败:', response.message)
      message.error(`文件上传失败: ${response.message}`)
    }
  } catch (error) {
    console.error('文件上传异常:', error)
    message.error(`文件上传失败: ${error.message}`)
  }
  
  return false // 阻止自动上传
}

const handleRemove = (file) => {
  // 从文件列表中移除
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
  
  // 从已上传文件中移除
  const uploadedIndex = uploadedFiles.value.findIndex(item => item.filename === file.name)
  if (uploadedIndex > -1) {
    const fileToDelete = uploadedFiles.value[uploadedIndex]
    // 删除后端文件
    fileApi.deleteFile(fileToDelete.id).catch(error => {
      console.error('删除文件失败:', error)
    })
    uploadedFiles.value.splice(uploadedIndex, 1)
  }
  
  // 从选中附件中移除
  const selectedIndex = selectedAttachments.value.findIndex(item => item.filename === file.name)
  if (selectedIndex > -1) {
    selectedAttachments.value.splice(selectedIndex, 1)
    updateAttachmentIds()
  }
}

// 插入姓名占位符
const insertNamePlaceholder = () => {
  const textarea = document.querySelector('textarea')
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = formData.body
    formData.body = text.substring(0, start) + '{{姓名}}' + text.substring(end)
    
    // 设置光标位置
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(start + 6, start + 6)
    }, 0)
  } else {
    formData.body += '{{姓名}}'
  }
}

// 个性化内容替换
const personalizeContent = (content, teacherName) => {
  return content.replace(/{{姓名}}/g, teacherName)
}

// 更新附件ID列表
const updateAttachmentIds = () => {
  formData.attachment_ids = selectedAttachments.value.map(file => file.id)
}

// 加载已上传的文件列表
const loadUploadedFiles = async () => {
  try {
    console.log('开始加载文件列表...')
    const response = await fileApi.getFilesList()
    console.log('API响应:', response)
    
    if ((response.error === false || response.error === undefined) && response.data && response.code === 200) {
      console.log('原始数据结构:', response.data)
      // 处理嵌套数组结构
      let fileData = response.data
      if (Array.isArray(fileData) && fileData.length > 0 && Array.isArray(fileData[0])) {
        console.log('检测到嵌套数组，提取第一层数据')
        fileData = fileData[0]
      }
      console.log('处理后的文件数据:', fileData)
      uploadedFiles.value = fileData || []
      console.log('设置uploadedFiles.value完成，当前值:', uploadedFiles.value)
    } else {
      console.log('API响应错误或无数据:', { error: response.error, data: response.data, code: response.code })
    }
  } catch (error) {
    console.error('加载文件列表失败:', error)
  }
}

// 选择附件
const selectAttachment = (file) => {
  const index = selectedAttachments.value.findIndex(item => item.id === file.id)
  if (index === -1) {
    selectedAttachments.value.push(file)
  } else {
    selectedAttachments.value.splice(index, 1)
  }
  updateAttachmentIds()
}

// 检查文件是否已选择
const isFileSelected = (file) => {
  return selectedAttachments.value.some(item => item.id === file.id)
}

// 发送邮件
const sendEmail = async () => {
  try {
    await formRef.value.validate()
    sendLoading.value = true
    
    let response
    if (sendMode.value === 'custom') {
      // 自定义收件人模式
      response = await smtpApi.sendEmail({
        to_emails: formData.to_emails,
        cc_emails: formData.cc_emails.length > 0 ? formData.cc_emails : undefined,
        bcc_emails: formData.bcc_emails.length > 0 ? formData.bcc_emails : undefined,
        subject: formData.subject,
        body: formData.body,
        is_html: formData.is_html,
        attachment_ids: formData.attachment_ids.length > 0 ? formData.attachment_ids : undefined
      })
    } else {
      // 教师模式 - 个性化群发
      if (formData.body.includes('{{姓名}}')) {
        // 需要个性化发送，逐个发送
        let successCount = 0
        let failCount = 0
        
        for (const teacherId of formData.teacher_ids) {
          const teacher = teachers.value.find(t => t.id === teacherId)
          if (teacher) {
            try {
              const personalizedSubject = personalizeContent(formData.subject, teacher.name)
              const personalizedBody = personalizeContent(formData.body, teacher.name)
              
              const result = await smtpApi.sendEmail({
                to_emails: [teacher.email],
                subject: personalizedSubject,
                body: personalizedBody,
                is_html: formData.is_html,
                attachment_ids: formData.attachment_ids.length > 0 ? formData.attachment_ids : undefined
              })
              
              if (result.code === 200) {
                successCount++
              } else {
                failCount++
              }
            } catch (error) {
              failCount++
            }
          }
        }
        
        if (successCount > 0) {
          message.success(`个性化邮件发送完成：成功 ${successCount} 封${failCount > 0 ? `，失败 ${failCount} 封` : ''}`)
          emit('email-sent', true)
          resetForm()
        } else {
          message.error('所有邮件发送失败')
          emit('email-sent', false)
        }
        return
      } else {
        // 普通群发
        response = await smtpApi.sendToTeachers(
          formData.teacher_ids,
          formData.subject,
          formData.body,
          formData.is_html,
          formData.attachment_ids
        )
      }
    }
    
    if (response.code === 200) {
      message.success('邮件发送成功')
      emit('email-sent', true)
      resetForm()
    } else {
      message.error(response.message || '邮件发送失败')
      emit('email-sent', false)
    }
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写完整的邮件信息')
    } else {
      message.error('发送失败: ' + (error.response?.data?.message || error.message))
      emit('email-sent', false)
    }
  } finally {
    sendLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    to_emails: [],
    cc_emails: [],
    bcc_emails: [],
    teacher_ids: [],
    subject: '',
    body: '',
    is_html: false,
    attachment_ids: []
  })
  fileList.value = []
  selectedAttachments.value = []
}

const onFinish = () => {
  sendEmail()
}

// 监听SMTP配置状态变化
watch(() => props.smtpConfigured, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

// 调试：监听文件列表变化
watch(() => uploadedFiles.value, (newFiles, oldFiles) => {
  console.log('文件列表变化:', {
    新文件列表: newFiles,
    旧文件列表: oldFiles,
    文件数量: newFiles?.length || 0
  })
}, { deep: true })

// 调试：监听API响应
watch(() => uploadedFiles.value.length, (newLength) => {
  console.log('文件列表长度变化:', newLength)
  if (newLength > 0) {
    console.log('当前文件列表:', uploadedFiles.value)
  }
})

onMounted(() => {
  // 默认加载教师列表
  loadTeachers()
  // 加载已上传文件列表
  loadUploadedFiles()
  
  // 检查购物车是否有数据，如果有则自动切换到教师模式
  if (cartStore.cartCount > 0) {
    sendMode.value = 'teachers'
    loadFromCart()
  }
})
</script>

<style scoped>
.email-sender-card {
  height: 100%;
}

.email-sender-card :deep(.ant-card-body) {
  padding: 24px;
}

@media (max-width: 768px) {
  .email-sender-card :deep(.ant-card-body) {
    padding: 16px;
  }
}
</style>