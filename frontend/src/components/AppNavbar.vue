<template>
  <nav class="navbar">
    <div class="logo" @click="$router.push('/')">
      <div class="logo-icon">📘</div>
      职学导航
    </div>
    <div class="nav-menu">
      <router-link to="/" :class="{ active: $route.path === '/' }">首页</router-link>
      <router-link to="/input" :class="{ active: $route.path === '/input' }">资料审查</router-link>
      <router-link :to="diagnosisLink" :class="{ active: $route.path.startsWith('/diagnosis') }">能力诊断</router-link>
    </div>
    <div class="nav-right">
      <!-- 已登录 -->
      <template v-if="store.isLoggedIn">
        <span class="nav-avatar" @click="$router.push('/profile')"></span>
        <span class="nav-username" @click="$router.push('/profile')">{{ store.username }}</span>
        <button class="app-btn app-btn-outline" @click="store.logout()">退出</button>
      </template>

      <!-- 未登录 -->
      <template v-else>
        <button class="app-btn app-btn-outline" @click="$router.push('/login')">登录</button>
        <button class="app-btn app-btn-primary" @click="$router.push('/login?tab=register')">注册</button>
      </template>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const store = useUserStore()

const diagnosisLink = computed(() => {
  const id = store.userInfo?.latest_assessment_id
  return id ? `/diagnosis/${id}` : '/diagnosis'
})
</script>

<style scoped>
/* 导航栏 */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #2563eb;
  cursor: pointer;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
}

.nav-menu {
  display: flex;
  gap: 32px;
}

.nav-menu a {
  text-decoration: none;
  color: #555;
  font-size: 15px;
  padding: 20px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-menu a:hover,
.nav-menu a.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-username {
  font-size: 14px;
  color: #555;
  cursor: pointer;
}
</style>
