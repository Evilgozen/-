<template>
  <div class="smtp-container">
    <a-row :gutter="[24, 24]">
      <!-- SMTP配置卡片 -->
      <a-col :xs="24" :lg="12">
        <SMTPConfig @config-updated="handleConfigUpdated" />
      </a-col>
      
      <!-- 邮件发送卡片 -->
      <a-col :xs="24" :lg="12">
        <EmailSender :smtp-configured="smtpConfigured" @email-sent="handleEmailSent" />
      </a-col>
    </a-row>
    
    <!-- 邮件发送记录 -->
    <a-row :gutter="[24, 24]" style="margin-top: 24px;">
      <a-col :span="24">
        <EmailLogs ref="emailLogsRef" />
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import SMTPConfig from '../components/smtp/SMTPConfig.vue'
import EmailSender from '../components/smtp/EmailSender.vue'
import EmailLogs from '../components/smtp/EmailLogs.vue'
import { smtpApi } from '../api/smtp'

const smtpConfigured = ref(false)
const emailLogsRef = ref(null)

// 检查SMTP配置状态
const checkSMTPConfig = async () => {
  try {
    const response = await smtpApi.getConfig()
    smtpConfigured.value = response.code === 200
  } catch (error) {
    smtpConfigured.value = false
  }
}

// 处理配置更新
const handleConfigUpdated = (success) => {
  if (success) {
    smtpConfigured.value = true
    message.success('SMTP配置更新成功')
  }
}

// 处理邮件发送
const handleEmailSent = (success) => {
  if (success) {
    message.success('邮件发送成功')
    // 刷新邮件记录
    if (emailLogsRef.value) {
      emailLogsRef.value.refreshLogs()
    }
  }
}

onMounted(() => {
  checkSMTPConfig()
})
</script>

<style scoped>
.smtp-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px - 70px);
}

@media (max-width: 768px) {
  .smtp-container {
    padding: 16px;
  }
}
</style>