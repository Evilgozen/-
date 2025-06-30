<template>
  <a-card title="SMTP配置" class="smtp-config-card">
    <template #extra>
      <a-space>
        <a-button 
          type="primary" 
          :loading="testLoading" 
          @click="testConnection"
          :disabled="!isFormValid"
        >
          测试连接
        </a-button>
        <a-button 
          type="primary" 
          :loading="saveLoading" 
          @click="saveConfig"
          :disabled="!isFormValid"
        >
          保存配置
        </a-button>
      </a-space>
    </template>
    
    <a-spin :spinning="loading" tip="加载配置中...">
      <a-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        layout="vertical"
        @finish="onFinish"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="SMTP服务器" name="smtp_server">
              <a-input 
                v-model:value="formData.smtp_server" 
                placeholder="例如: smtp.gmail.com"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="端口" name="smtp_port">
              <a-input-number 
                v-model:value="formData.smtp_port" 
                :min="1" 
                :max="65535"
                style="width: 100%"
                placeholder="587"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用户名" name="username">
              <a-input 
                v-model:value="formData.username" 
                placeholder="邮箱用户名"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="密码/授权码" name="password">
              <a-input-password 
                v-model:value="formData.password" 
                placeholder="邮箱密码或应用授权码"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="发送者名称" name="sender_name">
              <a-input 
                v-model:value="formData.sender_name" 
                placeholder="例如: 教师信息系统"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发送者邮箱" name="sender_email">
              <a-input 
                v-model:value="formData.sender_email" 
                placeholder="发送者邮箱地址"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item name="use_tls">
          <a-checkbox v-model:checked="formData.use_tls">
            使用TLS加密
          </a-checkbox>
        </a-form-item>
      </a-form>
    </a-spin>
    
    <!-- 配置状态显示 -->
    <a-alert
      v-if="configStatus"
      :message="configStatus.message"
      :type="configStatus.type"
      show-icon
      style="margin-top: 16px"
    />
  </a-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { smtpApi } from '../../api/smtp'

const emit = defineEmits(['config-updated'])

const formRef = ref()
const loading = ref(false)
const saveLoading = ref(false)
const testLoading = ref(false)
const configStatus = ref(null)
const currentConfigId = ref(null)

const formData = reactive({
  smtp_server: '',
  smtp_port: 587,
  username: '',
  password: '',
  use_tls: true,
  sender_name: '',
  sender_email: ''
})

const rules = {
  smtp_server: [
    { required: true, message: '请输入SMTP服务器地址', trigger: 'blur' }
  ],
  smtp_port: [
    { required: true, message: '请输入端口号', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: '端口号必须在1-65535之间', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  sender_name: [
    { required: true, message: '请输入发送者名称', trigger: 'blur' }
  ],
  sender_email: [
    { required: true, message: '请输入发送者邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const isFormValid = computed(() => {
  return formData.smtp_server && 
         formData.smtp_port && 
         formData.username && 
         formData.password && 
         formData.sender_name && 
         formData.sender_email
})

// 加载现有配置
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await smtpApi.getConfig()
    if (response.code === 200 && response.data && response.data.length > 0) {
      const config = response.data[0]
      currentConfigId.value = config.id
      Object.assign(formData, {
        smtp_server: config.smtp_server,
        smtp_port: config.smtp_port,
        username: config.username,
        password: '', // 不显示密码
        use_tls: config.use_tls,
        sender_name: config.sender_name,
        sender_email: config.sender_email
      })
      configStatus.value = {
        type: 'success',
        message: 'SMTP配置已加载'
      }
    } else {
      configStatus.value = {
        type: 'info',
        message: '暂无SMTP配置，请添加新配置'
      }
    }
  } catch (error) {
    configStatus.value = {
      type: 'warning',
      message: '加载配置失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}

// 测试连接
const testConnection = async () => {
  try {
    await formRef.value.validate()
    testLoading.value = true
    
    const response = await smtpApi.testConnection(formData)
    if (response.code === 200) {
      message.success('SMTP连接测试成功')
      configStatus.value = {
        type: 'success',
        message: 'SMTP连接测试成功'
      }
    } else {
      message.error(response.message || '连接测试失败')
      configStatus.value = {
        type: 'error',
        message: response.message || '连接测试失败'
      }
    }
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写完整的配置信息')
    } else {
      message.error('连接测试失败: ' + (error.response?.data?.message || error.message))
      configStatus.value = {
        type: 'error',
        message: '连接测试失败: ' + (error.response?.data?.message || error.message)
      }
    }
  } finally {
    testLoading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  try {
    await formRef.value.validate()
    saveLoading.value = true
    
    let response
    if (currentConfigId.value) {
      // 更新现有配置
      response = await smtpApi.updateConfig(currentConfigId.value, formData)
    } else {
      // 添加新配置
      response = await smtpApi.addConfig(formData)
    }
    
    if (response.code === 200) {
      message.success('SMTP配置保存成功')
      configStatus.value = {
        type: 'success',
        message: 'SMTP配置保存成功'
      }
      emit('config-updated', true)
      // 重新加载配置以获取ID
      await loadConfig()
    } else {
      message.error(response.message || '配置保存失败')
      configStatus.value = {
        type: 'error',
        message: response.message || '配置保存失败'
      }
      emit('config-updated', false)
    }
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写完整的配置信息')
    } else {
      message.error('保存失败: ' + (error.response?.data?.message || error.message))
      configStatus.value = {
        type: 'error',
        message: '保存失败: ' + (error.response?.data?.message || error.message)
      }
      emit('config-updated', false)
    }
  } finally {
    saveLoading.value = false
  }
}

const onFinish = () => {
  saveConfig()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.smtp-config-card {
  height: 100%;
}

.smtp-config-card :deep(.ant-card-body) {
  padding: 24px;
}

@media (max-width: 768px) {
  .smtp-config-card :deep(.ant-card-body) {
    padding: 16px;
  }
}
</style>