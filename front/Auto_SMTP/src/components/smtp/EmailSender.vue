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
          placeholder="请输入邮件内容"
          :rows="6"
          show-count
          :maxlength="5000"
        />
      </a-form-item>
      
      <a-form-item>
        <a-checkbox v-model:checked="formData.is_html">
          HTML格式
        </a-checkbox>
      </a-form-item>
      
      <!-- 附件上传 (暂时隐藏，可以后续实现) -->
      <!-- <a-form-item label="附件 (可选)">
        <a-upload
          v-model:file-list="fileList"
          :before-upload="beforeUpload"
          multiple
        >
          <a-button>
            <UploadOutlined /> 选择文件
          </a-button>
        </a-upload>
      </a-form-item> -->
    </a-form>
  </a-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { smtpApi } from '../../api/smtp'
import { teacherApi } from '../../api/teacher'

const props = defineProps({
  smtpConfigured: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['email-sent'])

const formRef = ref()
const sendLoading = ref(false)
const teachersLoading = ref(false)
const sendMode = ref('custom')
const teachers = ref([])

const formData = reactive({
  to_emails: [],
  cc_emails: [],
  bcc_emails: [],
  teacher_ids: [],
  subject: '',
  body: '',
  is_html: false
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
      teachers.value = response.data.filter(teacher => teacher.email)
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
  if (sendMode.value === 'teachers' && teachers.value.length === 0) {
    loadTeachers()
  }
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
        is_html: formData.is_html
      })
    } else {
      // 教师模式
      response = await smtpApi.sendToTeachers({
        teacher_ids: formData.teacher_ids,
        subject: formData.subject,
        body: formData.body,
        is_html: formData.is_html
      })
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
    is_html: false
  })
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

onMounted(() => {
  // 默认加载教师列表
  loadTeachers()
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