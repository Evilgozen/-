<template>
  <a-card title="邮件发送记录" class="email-logs-card">
    <template #extra>
      <a-space>
        <a-select
          v-model:value="statusFilter"
          placeholder="筛选状态"
          style="width: 120px"
          @change="onFilterChange"
          allowClear
        >
          <a-select-option value="success">成功</a-select-option>
          <a-select-option value="failed">失败</a-select-option>
        </a-select>
        <a-button @click="refreshLogs" :loading="loading">
          <ReloadOutlined /> 刷新
        </a-button>
      </a-space>
    </template>
    
    <a-spin :spinning="loading" tip="加载记录中...">
      <div v-if="!loading && logs.length === 0" class="empty-state">
        <a-empty description="暂无邮件发送记录" />
      </div>
      
      <a-table
        v-else
        :columns="columns"
        :data-source="logs"
        :pagination="pagination"
        :scroll="{ x: 800 }"
        row-key="id"
        size="middle"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'to_emails'">
            <a-tooltip :title="record.to_emails.join(', ')">
              <a-tag v-for="(email, index) in record.to_emails.slice(0, 2)" :key="index" color="blue">
                {{ email }}
              </a-tag>
              <a-tag v-if="record.to_emails.length > 2" color="default">
                +{{ record.to_emails.length - 2 }}
              </a-tag>
            </a-tooltip>
          </template>
          
          <template v-if="column.key === 'subject'">
            <a-tooltip :title="record.subject">
              <span class="subject-text">{{ record.subject }}</span>
            </a-tooltip>
          </template>
          
          <template v-if="column.key === 'body'">
            <a-tooltip :title="record.body">
              <span class="body-text">{{ truncateText(record.body, 50) }}</span>
            </a-tooltip>
          </template>
          
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'success' ? 'green' : 'red'">
              {{ record.status === 'success' ? '成功' : '失败' }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'send_time'">
            <span>{{ formatDateTime(record.send_time) }}</span>
          </template>
          
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="viewDetails(record)">
                查看详情
              </a-button>
              <a-button 
                v-if="record.status === 'failed'"
                type="link" 
                size="small" 
                @click="resendEmail(record)"
              >
                重新发送
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-spin>
    
    <!-- 详情模态框 -->
    <a-modal
      v-model:open="detailModalVisible"
      :title="'邮件详情 - ' + (selectedLog?.subject || '')"
      width="800px"
      :footer="null"
    >
      <div v-if="selectedLog" class="email-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="发送状态">
            <a-tag :color="selectedLog.status === 'success' ? 'green' : 'red'">
              {{ selectedLog.status === 'success' ? '成功' : '失败' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="发送时间">
            {{ formatDateTime(selectedLog.send_time) }}
          </a-descriptions-item>
          <a-descriptions-item label="发送者">
            {{ selectedLog.sender_email }}
          </a-descriptions-item>
          <a-descriptions-item label="收件人">
            <div class="email-list">
              <a-tag v-for="email in selectedLog.to_emails" :key="email" color="blue">
                {{ email }}
              </a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="抄送" v-if="selectedLog.cc_emails && selectedLog.cc_emails.length > 0">
            <div class="email-list">
              <a-tag v-for="email in selectedLog.cc_emails" :key="email" color="cyan">
                {{ email }}
              </a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="密送" v-if="selectedLog.bcc_emails && selectedLog.bcc_emails.length > 0">
            <div class="email-list">
              <a-tag v-for="email in selectedLog.bcc_emails" :key="email" color="purple">
                {{ email }}
              </a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="邮件主题">
            {{ selectedLog.subject }}
          </a-descriptions-item>
          <a-descriptions-item label="邮件内容">
            <div class="email-body" v-html="selectedLog.body"></div>
          </a-descriptions-item>
          <a-descriptions-item label="错误信息" v-if="selectedLog.error_message">
            <a-alert :message="selectedLog.error_message" type="error" show-icon />
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
  </a-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { smtpApi } from '../../api/smtp'

const loading = ref(false)
const logs = ref([])
const statusFilter = ref(undefined)
const detailModalVisible = ref(false)
const selectedLog = ref(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
})

const columns = [
  {
    title: '收件人',
    key: 'to_emails',
    width: 200,
    ellipsis: true
  },
  {
    title: '主题',
    key: 'subject',
    width: 200,
    ellipsis: true
  },
  {
    title: '内容',
    key: 'body',
    width: 200,
    ellipsis: true
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    align: 'center'
  },
  {
    title: '发送时间',
    key: 'send_time',
    width: 160,
    sorter: (a, b) => new Date(a.send_time) - new Date(b.send_time)
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    align: 'center'
  }
]

// 加载邮件记录
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      limit: pagination.pageSize * pagination.current
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await smtpApi.getEmailLogs(params)
    if (response.code === 200 && response.data) {
      logs.value = response.data
      pagination.total = response.data.length
    } else {
      logs.value = []
      pagination.total = 0
    }
  } catch (error) {
    message.error('加载邮件记录失败')
    logs.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 刷新记录
const refreshLogs = () => {
  loadLogs()
}

// 筛选状态改变
const onFilterChange = () => {
  pagination.current = 1
  loadLogs()
}

// 查看详情
const viewDetails = (record) => {
  selectedLog.value = record
  detailModalVisible.value = true
}

// 重新发送邮件
const resendEmail = (record) => {
  // 这里可以触发重新发送逻辑
  // 可以通过emit事件通知父组件
  message.info('重新发送功能待实现')
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text) return '-'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 暴露刷新方法给父组件
defineExpose({
  refreshLogs
})

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.email-logs-card {
  margin-top: 24px;
}

.email-logs-card :deep(.ant-card-body) {
  padding: 24px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.subject-text,
.body-text {
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.email-detail .email-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.email-detail .email-body {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 768px) {
  .email-logs-card {
    margin-top: 16px;
  }
  
  .email-logs-card :deep(.ant-card-body) {
    padding: 16px;
  }
  
  .subject-text,
  .body-text {
    max-width: 120px;
  }
}
</style>