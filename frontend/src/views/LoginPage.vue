<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="card-header">
        <div class="card-logo">📘</div>
        <div class="card-title">职学导航</div>
        <div class="card-subtitle">面向职业学习者的能力诊断与资源生成系统</div>
      </div>

      <!-- Tab 切换 -->
      <div class="tab-bar">
        <button
          :class="['tab-btn', { active: activeTab === 'login' }]"
          @click="switchTab('login')"
        >登录</button>
        <button
          :class="['tab-btn', { active: activeTab === 'register' }]"
          @click="switchTab('register')"
        >注册</button>
      </div>

      <!-- ===== 登录表单 ===== -->
      <form v-if="activeTab === 'login'" class="form" @submit.prevent="handleLogin">
        <div class="form-item">
          <label class="form-label">用户名</label>
          <input
            v-model="loginForm.username"
            class="form-input"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
            @input="loginError = ''"
          />
        </div>
        <div class="form-item">
          <label class="form-label">密码</label>
          <div class="pwd-wrap">
            <input
              v-model="loginForm.password"
              class="form-input pwd-input"
              :type="showLoginPwd ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              @input="loginError = ''"
            />
            <button
              type="button"
              class="pwd-toggle"
              @click="showLoginPwd = !showLoginPwd"
              :title="showLoginPwd ? '隐藏密码' : '显示密码'"
            >{{ showLoginPwd ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <p v-if="loginError" class="form-error">{{ loginError }}</p>
        <button
          class="app-btn-submit"
          type="submit"
          :disabled="loginLoading || !canLogin"
        >
          <span v-if="loginLoading" class="app-spinner"></span>
          {{ loginLoading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- ===== 注册表单 ===== -->
      <form v-if="activeTab === 'register'" class="form" @submit.prevent="handleRegister">
        <div class="form-item">
          <label class="form-label">用户名</label>
          <input
            v-model="registerForm.username"
            class="form-input"
            type="text"
            placeholder="请输入用户名"
            autocomplete="off"
            @input="registerError = ''"
          />
        </div>
        <div class="form-item">
          <label class="form-label">密码</label>
          <div class="pwd-wrap">
            <input
              v-model="registerForm.password"
              class="form-input pwd-input"
              :type="showRegisterPwd ? 'text' : 'password'"
              placeholder="请输入密码（至少6位）"
              autocomplete="new-password"
              @input="registerError = ''"
            />
            <button
              type="button"
              class="pwd-toggle"
              @click="showRegisterPwd = !showRegisterPwd"
              :title="showRegisterPwd ? '隐藏密码' : '显示密码'"
            >{{ showRegisterPwd ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <p v-if="registerError" class="form-error">{{ registerError }}</p>
        <button
          class="app-btn-submit"
          type="submit"
          :disabled="registerLoading || !canRegister"
        >
          <span v-if="registerLoading" class="app-spinner"></span>
          {{ registerLoading ? '注册中...' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

// 已登录用户直接跳转首页
onMounted(() => {
  if (store.isLoggedIn) {
    router.replace('/')
  }
})

// ---- Tab 状态 ----
function getTabFromQuery(): 'login' | 'register' {
  return route.query.tab === 'register' ? 'register' : 'login'
}

const activeTab = ref<'login' | 'register'>(getTabFromQuery())

// 监听 URL query 变化（导航栏按钮点击时），自动切换 Tab
watch(() => route.query.tab, () => {
  activeTab.value = getTabFromQuery()
})

function switchTab(tab: 'login' | 'register') {
  activeTab.value = tab
  loginError.value = ''
  registerError.value = ''
}

// ---- 登录 ----
const loginLoading = ref(false)
const loginError = ref('')
const showLoginPwd = ref(false)
const loginForm = ref({ username: '', password: '' })

const canLogin = computed(
  () => loginForm.value.username.trim() !== '' && loginForm.value.password !== '',
)

async function handleLogin() {
  if (!canLogin.value) return
  loginLoading.value = true
  loginError.value = ''
  try {
    await store.login(loginForm.value.username, loginForm.value.password)
    ElMessage.success('登录成功')
    router.replace('/')
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    loginError.value = typeof detail === 'string' ? detail : '用户名或密码错误'
  } finally {
    loginLoading.value = false
  }
}

// ---- 注册 ----
const registerLoading = ref(false)
const registerError = ref('')
const showRegisterPwd = ref(false)
const registerForm = ref({ username: '', password: '' })

const canRegister = computed(
  () => registerForm.value.username.trim() !== '' && registerForm.value.password.length >= 6,
)

async function handleRegister() {
  if (!canRegister.value) return
  registerLoading.value = true
  registerError.value = ''
  try {
    await store.register(registerForm.value.username, registerForm.value.password)
    // 注册成功后直接登录，跳过登录页面
    await store.login(registerForm.value.username, registerForm.value.password)
    ElMessage.success('注册成功，欢迎！')
    router.replace('/')
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    registerError.value = typeof detail === 'string' ? detail : '注册失败，请稍后重试'
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
/* ---- 页面容器 ---- */
.login-wrapper {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 40px 20px;
}

.login-card {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 40px 36px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

/* ---- 卡片头部 ---- */
.card-header {
  text-align: center;
  margin-bottom: 28px;
}

.card-logo {
  font-size: 40px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 6px;
}

.card-subtitle {
  font-size: 13px;
  color: #999;
}

/* ---- Tab ---- */
.tab-bar {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: none;
  font-size: 15px;
  color: #999;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  font-family: inherit;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  font-weight: 600;
}

/* ---- 表单 ---- */
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.form-input {
  height: 42px;
  padding: 0 14px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  font-size: 14px;
  color: #111827;
  outline: none;
  transition: border-color 0.3s;
  font-family: inherit;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.form-input::placeholder {
  color: #c0c4cc;
}

/* ---- 密码框 + 小眼睛 ---- */
.pwd-wrap {
  position: relative;
  display: flex;
}

.pwd-input {
  width: 100%;
  padding-right: 42px;  /* 给小眼睛留空间 */
}

/* 隐藏 Edge/IE 浏览器自带的密码显示按钮 */
.pwd-input::-ms-reveal,
.pwd-input::-ms-clear {
  display: none;
}

/* 隐藏 Chrome/Safari 自动填充后的 eye icon */
.pwd-input::-webkit-credentials-auto-fill-button {
  display: none !important;
}

.pwd-toggle {
  position: absolute;
  right: 0;
  top: 0;
  height: 42px;
  width: 42px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #999;
  transition: color 0.2s;
}

.pwd-toggle:hover {
  color: #555;
}

.form-error {
  color: #f56c6c;
  font-size: 13px;
  margin: 0;
}

/* ---- 提交按钮（尺寸微调） ---- */
.app-btn-submit {
  width: 100%;
  height: 44px;
  margin-top: 4px;
  justify-content: center;
}

</style>
