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
        <h3 class="section-title">
          描述你的经历
          <el-tooltip placement="top" effect="light" :show-after="150">
            <template #content>
              <div class="tip-box">
                <div class="tip-title">填写格式</div>
                <p>我的目标职业是【目标职业】。我会/熟悉【技术或知识点】，能够完成【具体任务】；我做过【项目或实践】，主要负责【具体工作】；我了解但不熟练的是【知识点】；我目前不会或没做过的是【知识点或任务】；我希望优先提升【学习方向】。</p>
                <div class="tip-title" style="margin-top: 8px">填写示例</div>
                <p>我的目标职业是后端开发工程师。我会 Java、MySQL 和 Git，能够完成基础接口开发；我做过校园订单管理项目，主要负责用户登录和订单模块；我了解 Spring Boot 但还不熟练；目前不会 Redis、Docker 和系统部署；我希望优先提升项目实战和后端工程化能力。</p>
              </div>
            </template>
            <span class="help-circle">?</span>
          </el-tooltip>
        </h3>
        <p class="section-desc">自由描述你的技能、项目经验、学习经历等，AI 将全面分析你的能力水平（最少 10 字）</p>
        <div class="textarea-wrap">
          <textarea
            v-model="userInput"
            class="user-textarea"
            :class="{ error: userInput.length > 0 && userInput.length < 10 }"
            placeholder="例如：我会 HTML、CSS、JavaScript，熟悉 Vue 框架，做过一个电商网站的前端开发，主要负责页面布局和组件封装..."
            rows="6"
            @input="submitError = ''; reviewHint = ''; reviewMissing = []; submitState = 'idle'"
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

      <!-- 输入审查提示 -->
      <el-alert
        v-if="reviewHint"
        :title="reviewHint"
        type="warning"
        show-icon
        :closable="false"
        style="margin-top: 16px; max-width: 600px; margin-left: auto; margin-right: auto"
      >
        <template v-if="reviewMissing.length" #default>
          <div style="margin-top: 4px">可补充：{{ reviewMissing.join('、') }}</div>
        </template>
      </el-alert>

      <!-- 提交按钮 -->
      <div v-if="selectedJobId" class="submit-area">
        <button
          class="app-btn-submit"
          :disabled="submitDisabled"
          @click="handleSubmit"
        >
          <span v-if="submitLoading" class="app-spinner"></span>
          {{ submitButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getJobList, type JobInfo } from '@/api/jobs'
import { createAssessment, submitAssessment, reviewInput } from '@/api/assessment'
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
  reviewHint.value = ''
  reviewMissing.value = []
  submitState.value = 'idle'
}

// ---- 用户输入 ----
const userInput = ref('')
const canSubmit = computed(
  () => selectedJobId.value !== null && userInput.value.length >= 10,
)

// ---- 提交流程 ----
type SubmitState = 'idle' | 'reviewing' | 'insufficient' | 'proceeding'
const submitState = ref<SubmitState>('idle')
const submitError = ref('')
const reviewHint = ref('')
const reviewMissing = ref<string[]>([])

const submitButtonText = computed(() => {
  switch (submitState.value) {
    case 'reviewing': return '正在检查资料完整性…'
    case 'insufficient': return '补充后重新检查'
    case 'proceeding': return '资料齐全，正在进入诊断…'
    default: return '检查资料是否齐全'
  }
})
const submitLoading = computed(() => submitState.value === 'reviewing' || submitState.value === 'proceeding')
const submitDisabled = computed(() => submitLoading.value || !canSubmit.value)

async function handleSubmit() {
  if (!canSubmit.value || !selectedJobId.value) return

  submitError.value = ''
  reviewHint.value = ''
  reviewMissing.value = []

  // ⓪ 提交前审查输入完整性：内容不够就留在当前页，原文不动，提示补充
  submitState.value = 'reviewing'
  try {
    const review = await reviewInput({ job_id: selectedJobId.value, user_input: userInput.value })
    if (!review.sufficient) {
      reviewMissing.value = review.missing || []
      reviewHint.value = review.hint || '内容还不够，请再补充一些技能、项目或短板描述'
      submitState.value = 'insufficient'
      return
    }
  } catch {
    // 审查接口异常：fail-open 放行，继续进入诊断
    ElMessage.info('输入审查失败，已跳过')
  }

  // ① 资料齐全：进入诊断流程
  submitState.value = 'proceeding'
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
    // ③ 立即跳转到诊断页（assessment 尚未提交，overall_mastery 为 null，显示"AI 诊断进行中"等待界面）
    router.push(`/diagnosis/${assessment.id}`)
    // ④ 后台提交用户输入，触发 AI 诊断（不阻塞跳转）
    submitAssessment(assessment.id, { user_input: userInput.value }).catch(() => {
      ElMessage.error('诊断失败，请返回资料审查重新提交')
    })
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    submitError.value = typeof detail === 'string' ? detail : '诊断请求失败，请稍后重试'
    submitState.value = 'idle'
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

/* ---- 提示问号圈 ---- */
.help-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #c0c4cc;
  color: #909399;
  font-size: 11px;
  font-weight: 700;
  cursor: help;
  margin-left: 4px;
  vertical-align: middle;
  line-height: 1;
  user-select: none;
}

.help-circle:hover {
  border-color: #2563eb;
  color: #2563eb;
  background: #eef2ff;
}

/* ---- 提示浮层内容 ---- */
.tip-box {
  max-width: 340px;
  line-height: 1.6;
  text-align: left;
}

.tip-title {
  font-weight: 700;
  margin-bottom: 6px;
  font-size: 14px;
  color: #111827;
}

.tip-box p {
  margin: 0 0 6px;
  font-size: 12.5px;
  color: #555;
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
