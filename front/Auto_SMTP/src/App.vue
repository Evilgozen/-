<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <a-layout class="layout">
      <a-layout-header class="header">
        <div class="logo">
          <h2 style="color: white; margin: 0;">教师信息管理系统</h2>
        </div>
        <a-menu
          theme="dark"
          mode="horizontal"
          :style="{ lineHeight: '64px' }"
          class="menu"
        >
          <a-menu-item key="home">
            <RouterLink to="/">首页</RouterLink>
          </a-menu-item>
          <a-menu-item key="teachers">
            <RouterLink to="/teachers">教师信息</RouterLink>
          </a-menu-item>
          <a-menu-item key="about">
            <RouterLink to="/about">关于</RouterLink>
          </a-menu-item>
          <a-menu-item key="smtp">
            <RouterLink to="/smtp">SMTP管理</RouterLink>
          </a-menu-item>
        </a-menu>
      </a-layout-header>
      <a-layout-content class="content">
        <RouterView />
      </a-layout-content>
      <a-layout-footer class="footer">
        <div style="text-align: center;">
          教师信息管理系统 ©2024 Created by Auto Ceramic
        </div>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<style scoped>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: #001529;
}

.logo {
  flex: 0 0 auto;
  margin-right: 24px;
}

.menu {
  flex: 1;
  border-bottom: none;
}

.menu a {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: color 0.3s;
}

.menu a:hover {
  color: #fff;
}

.menu .router-link-active {
  color: #1890ff;
}

.content {
  padding: 0;
  background: #f0f2f5;
  min-height: calc(100vh - 64px - 70px);
}

.footer {
  background: #f0f2f5;
  padding: 24px 0;
  color: rgba(0, 0, 0, 0.65);
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .logo h2 {
    font-size: 16px !important;
  }
  
  .menu {
    font-size: 14px;
  }
}
</style>
