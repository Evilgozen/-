<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home-container {
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 64px - 70px);
  display: flex;
  align-items: center;
}

.welcome-section {
  width: 100%;
}

.welcome-card {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: none;
}

.welcome-content {
  text-align: center;
  padding: 20px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.feature-list {
  margin: 40px 0;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  text-align: left;
  padding: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: #f8f9fa;
  height: 100%;
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  background: #fff;
}

.feature-icon {
  font-size: 2rem;
  color: #1890ff;
  margin-right: 16px;
  margin-top: 4px;
  flex-shrink: 0;
}

.feature-text h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.feature-text p {
  font-size: 0.95rem;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.action-buttons {
  margin-top: 40px;
}

.start-button {
  height: 48px;
  padding: 0 32px;
  font-size: 1.1rem;
  font-weight: 500;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .home-container {
    padding: 20px 10px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .welcome-description {
    font-size: 1rem;
  }
  
  .feature-item {
    padding: 16px;
  }
  
  .feature-icon {
    font-size: 1.5rem;
  }
  
  .feature-text h3 {
    font-size: 1.1rem;
  }
  
  .start-button {
    height: 44px;
    font-size: 1rem;
  }
}
</style>

<template>
  <div class="home-container">
    <a-row justify="center">
      <a-col :xs="24" :sm="20" :md="16" :lg="12">
        <div class="welcome-section">
          <a-card class="welcome-card">
            <div class="welcome-content">
              <h1 class="welcome-title">欢迎使用教师信息管理系统</h1>
              <p class="welcome-description">
                本系统提供华东师范大学计算机科学与技术学院教师信息的查询和展示功能。
                您可以浏览教师的基本信息、研究方向、联系方式等详细内容。
              </p>
              
              <div class="feature-list">
                <a-row :gutter="[16, 16]">
                  <a-col :xs="24" :sm="12">
                    <div class="feature-item">
                      <UserOutlined class="feature-icon" />
                      <div class="feature-text">
                        <h3>教师信息</h3>
                        <p>查看教师基本信息和联系方式</p>
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12">
                    <div class="feature-item">
                      <ExperimentOutlined class="feature-icon" />
                      <div class="feature-text">
                        <h3>研究方向</h3>
                        <p>了解教师的研究领域和专业方向</p>
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12">
                    <div class="feature-item">
                      <MailOutlined class="feature-icon" />
                      <div class="feature-text">
                        <h3>联系方式</h3>
                        <p>获取教师的邮箱和个人主页链接</p>
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12">
                    <div class="feature-item">
                      <BankOutlined class="feature-icon" />
                      <div class="feature-text">
                        <h3>学院信息</h3>
                        <p>查看教师所属学院和职称信息</p>
                      </div>
                    </div>
                  </a-col>
                </a-row>
              </div>
              
              <div class="action-buttons">
                <RouterLink to="/teachers">
                  <a-button type="primary" size="large" class="start-button">
                    开始浏览教师信息
                  </a-button>
                </RouterLink>
              </div>
            </div>
          </a-card>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import {
  UserOutlined,
  BankOutlined,
  MailOutlined,
  ExperimentOutlined
} from '@ant-design/icons-vue'

export default {
  components: {
    UserOutlined,
    BankOutlined,
    MailOutlined,
    ExperimentOutlined
  }
}
</script>
