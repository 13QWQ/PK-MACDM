<template>
  <div class="input-page">
    <!-- 顶部渐变区域（与首页 Hero 一致） -->
    <section class="input-hero">
      <h2 class="page-title">选择目标职业</h2>
      <p class="page-desc">请选择您希望评估的目标岗位，我们将对照该岗位的能力模型进行分析</p>
    </section>

    <div class="page-content">
      <!-- 职业卡片加载中 -->
      <div v-if="jobLoading" class="job-grid">
        <div v-for="i in 4" :key="i" class="job-card skeleton"></div>
      </div>

      <!-- 职业卡片加载失败 -->
      <el-alert
        v-else-if="jobError"
        title="职业列表加载失败"
        type="error"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #default>
          <el-button type="primary" size="small" @click="loadJobs">重试</el-button>
        </template>
      </el-alert>

      <!-- 职业卡片 -->
      <div v-else class="job-grid">
        <div
          v-for="job in jobList"
          :key="job.id"
          class="job-card"
          :class="{ selected: selectedJobId === job.id }"
          @click="selectJob(job.id)"
        >
          <div class="job-icon">{{ jobIcons[job.job_title] || '💼' }}</div>
          <div class="job-title">{{ job.job_title }}</div>
          <div class="job-desc">{{ job.description }}</div>
          <div class="job-tags">
            <span v-for="skill in job.required_skills" :key="skill" class="job-tag">{{ skill }}</span>
          </div>
        </div>
      </div>

      <!-- 输入区域（选了职业后才显示） -->
      <div v-if="selectedJobId" class="input-section">
        <h3 class="section-title">描述你的经历</h3>
        <p class="section-desc">自由描述你的技能、项目经验、学习经历等，AI 将全面分析你的能力水平（最少 10 字）</p>
        <div class="textarea-wrap">
          <textarea
            v-model="userInput"
            class="user-textarea"
            :class="{ error: userInput.length > 0 && userInput.length < 10 }"
            placeholder="例如：我会 HTML、CSS、JavaScript，熟悉 Vue 框架，做过一个电商网站的前端开发，主要负责页面布局和组件封装..."
            rows="6"
            @input="submitError = ''"
          ></textarea>
          <div class="char-count" :class="{ warn: userInput.length > 0 && userInput.length < 10 }">
            {{ userInput.length }} / 10 字
          </div>
        </div>
      </div>

      <!-- 提交错误 -->
      <el-alert
        v-if="submitError"
        :title="submitError"
        type="error"
        show-icon
        :closable="false"
        style="margin-top: 16px; max-width: 600px; margin-left: auto; margin-right: auto"
      />

      <!-- 提交按钮 -->
      <div v-if="selectedJobId" class="submit-area">
        <button
          class="app-btn-submit"
          :disabled="submitting || !canSubmit"
          @click="handleSubmit"
        >
          <span v-if="submitting" class="app-spinner"></span>
          {{ submitting ? 'AI 诊断中，请稍候...' : '开始 AI 诊断' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getJobList, type JobInfo } from '@/api/jobs'
import { createAssessment, submitAssessment } from '@/api/assessment'
import { createSession } from '@/api/session'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()

// ---- 职业卡片 ----
const jobList = ref<JobInfo[]>([])
const jobLoading = ref(true)
const jobError = ref(false)
const selectedJobId = ref<string | null>(null)

const jobIcons: Record<string, string> = {
  '前端开发工程师': '🎨',
  '后端开发工程师': '⚙️',
  '运维工程师': '🖥',
  '产品经理': '📋',
}

async function loadJobs() {
  jobLoading.value = true
  jobError.value = false
  try {
    jobList.value = await getJobList()
  } catch {
    jobError.value = true
  } finally {
    jobLoading.value = false
  }
}

function selectJob(id: string) {
  selectedJobId.value = id
  submitError.value = ''
}

// ---- 用户输入 ----
const userInput = ref('')
const canSubmit = computed(
  () => selectedJobId.value !== null && userInput.value.length >= 10,
)

// ---- 提交流程 ----
const submitting = ref(false)
const submitError = ref('')

async function handleSubmit() {
  if (!canSubmit.value || !selectedJobId.value) return

  submitting.value = true
  submitError.value = ''

  try {
    // ①② 创建评估 + 会话并行（互不依赖，减少一次网络往返）
    const [assessment, session] = await Promise.all([
      createAssessment({ job_id: selectedJobId.value }),
      createSession({ job_id: selectedJobId.value }),
    ])
    store.setCurrentSession(session.id)
    // 更新最新的评估 ID，导航栏"能力诊断"链接会指向这次诊断
    if (store.userInfo) {
      store.userInfo.latest_assessment_id = assessment.id
    }
    // ③ 提交用户输入，触发 AI 诊断
    await submitAssessment(assessment.id, { user_input: userInput.value })
    router.push(`/diagnosis/${assessment.id}`)
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    submitError.value = typeof detail === 'string' ? detail : '诊断请求失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadJobs()
})
</script>

<style scoped>
.input-page {
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
}

/* ---- 顶部渐变（与首页 Hero 一致） ---- */
.input-hero {
  padding: 48px 80px 36px;
  background: var(--hero-gradient);
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  margin-bottom: 8px;
}

.page-desc {
  font-size: 15px;
  color: #666;
  line-height: 1.8;
}

/* ---- 内容区 ---- */
.page-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 80px 60px;
}

/* ---- 职业卡片网格：2×2 ---- */
.job-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.job-card {
  background: #fff;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 32px 28px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.job-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.job-card.selected {
  border-color: #2563eb;
  background: #eef2ff;
}

.job-card.skeleton {
  height: 220px;
  cursor: default;
  animation: none;
}

.job-card.skeleton:hover {
  transform: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.job-icon {
  font-size: 44px;
  margin-bottom: 14px;
}

.job-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.job-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.job-tag {
  padding: 4px 12px;
  background: #f0f0f0;
  color: #666;
  border-radius: 4px;
  font-size: 13px;
}

/* ---- 输入区域 ---- */
.input-section {
  margin-top: 40px;
  text-align: center;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.section-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.textarea-wrap {
  position: relative;
  max-width: 700px;
  margin: 0 auto;
}

.user-textarea {
  width: 100%;
  padding: 16px 18px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  font-size: 15px;
  color: #111827;
  line-height: 1.7;
  resize: vertical;
  outline: none;
  transition: border-color 0.3s;
  font-family: inherit;
  background: #fff;
}

.user-textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.user-textarea.error {
  border-color: #f56c6c;
}

.user-textarea::placeholder {
  color: #c0c4cc;
}

.char-count {
  text-align: right;
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.char-count.warn {
  color: #f56c6c;
}

.submit-area {
  text-align: center;
  margin-top: 28px;
}

</style>
