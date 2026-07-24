<template>
  <div class="diagnosis-page">
    <!-- 顶部渐变区 -->
    <section class="diagnosis-hero">
      <h2 class="page-title">能力诊断</h2>
      <p class="page-desc">AI 对照目标岗位能力模型，多维度分析你的能力水平</p>
    </section>

    <div class="page-content">
      <!-- ===== 无评估 ID：引导卡片 ===== -->
      <div v-if="!assessmentId" class="guide-card">
        <div class="guide-icon">📊</div>
        <h3 class="guide-title">还没有诊断记录</h3>
        <p class="guide-desc">请先选择目标职业并提交你的技能与项目经历，AI 将为你生成详细的能力诊断报告。</p>
        <button class="app-btn app-btn-primary app-btn-large" @click="$router.push('/input')">
          🚀 开始资料审查
        </button>
      </div>

      <!-- ===== 有评估 ID：加载/错误/结果 ===== -->
      <template v-else>
        <!-- 加载中 -->
        <div v-if="loading" class="loading-area">
          <div class="loading-spinner"></div>
          <p>正在加载诊断结果...</p>
        </div>

        <!-- 加载失败 -->
        <el-alert
          v-else-if="loadError"
          :title="loadError"
          type="error"
          show-icon
          :closable="false"
          style="margin-bottom: 16px"
        >
          <template #default>
            <el-button type="primary" size="small" @click="loadAssessment">重试</el-button>
          </template>
        </el-alert>

        <!-- 诊断中（已提交但 AI 尚未完成） -->
        <div v-else-if="assessment && assessment.overall_mastery === null" class="pending-card">
          <div class="pending-icon">⏳</div>
          <h3 class="pending-title">AI 诊断进行中</h3>
          <p class="pending-desc">您的资料已提交，AI 正在分析中，预计需要 1-2 分钟。请稍后刷新页面查看结果。</p>
          <button class="app-btn app-btn-outline" @click="loadAssessment">刷新</button>
        </div>

        <!-- 诊断结果已就绪 -->
        <template v-else-if="assessment">
          <!-- Tab 栏 -->
          <div class="tab-bar">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              :class="['tab-btn', { active: activeTab === tab.key }]"
              @click="activeTab = tab.key"
            >{{ tab.label }}</button>
          </div>

          <!-- ===== Tab 1: 诊断结果 ===== -->
          <div v-show="activeTab === 'diagnosis'" class="tab-content">
            <!-- 概览卡片：掌握度 + 置信度 -->
            <div class="overview-row">
              <div class="overview-card mastery-card">
                <div class="overview-label">综合掌握度</div>
                <div class="mastery-ring" :style="{ '--pct': assessment.overall_mastery }">
                  <span class="mastery-value">{{ Math.round(assessment.overall_mastery * 100) }}</span>
                  <span class="mastery-unit">分</span>
                </div>
                <div class="mastery-tag" :class="masteryLevelClass">{{ masteryLevelText }}</div>
              </div>
              <div class="overview-card meta-card">
                <div class="meta-item">
                  <span class="meta-label">置信度</span>
                  <span class="meta-value">{{ assessment.confidence !== null ? Math.round(assessment.confidence * 100) + '%' : '—' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">能力维度</span>
                  <span class="meta-value">{{ assessment.ability_vector.length }} 项</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">知识缺口</span>
                  <span class="meta-value" :class="{ warn: assessment.knowledge_gaps.length > 0 }">{{ assessment.knowledge_gaps.length }} 项</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">诊断时间</span>
                  <span class="meta-value">{{ formatTime(assessment.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- 雷达图 -->
            <div class="chart-card">
              <h3 class="card-title">能力雷达图</h3>
              <div ref="chartRef" class="radar-chart"></div>
            </div>

            <!-- 知识缺口列表 -->
            <div v-if="assessment.knowledge_gaps.length > 0" class="gaps-card">
              <h3 class="card-title">知识缺口</h3>
              <p class="card-subtitle">以下能力领域尚未达标或证据不足，建议重点关注</p>
              <div class="gaps-grid">
                <div v-for="(gap, i) in assessment.knowledge_gaps" :key="i" class="gap-item">
                  <span class="gap-index">{{ i + 1 }}</span>
                  <span class="gap-text">{{ gap }}</span>
                </div>
              </div>
            </div>

            <!-- 底部操作 -->
            <div class="actions">
              <button class="app-btn app-btn-outline app-btn-large" @click="$router.push('/input')">
                🔄 重新诊断
              </button>
            </div>
          </div>

          <!-- ===== Tab 2: 资料库 ===== -->
          <div v-show="activeTab === 'library'" class="tab-content">
            <!-- 资源加载中 -->
            <div v-if="resourceLoading" class="loading-area" style="padding:60px 0">
              <div class="loading-spinner"></div>
              <p>加载学习资料...</p>
            </div>

            <!-- 资源为空 -->
            <div v-else-if="resources.length === 0" class="tab-placeholder">
              <div class="placeholder-icon">📚</div>
              <h3>暂无学习资料</h3>
              <p>诊断完成后 AI 将根据你的知识缺口自动生成学习资料。</p>
            </div>

            <!-- 资源卡片列表 -->
            <div v-else class="resource-grid">
              <div
                v-for="r in resources"
                :key="r.id"
                class="resource-card"
                @click="$router.push(`/resource/${r.id}`)"
              >
                <div class="rc-header">
                  <span class="rc-type-icon">{{ typeIcon(r.content_type) }}</span>
                  <span class="rc-type-tag">{{ r.content_type }}</span>
                  <span class="rc-difficulty" v-if="r.difficulty">
                    <span v-for="s in 5" :key="s" class="star" :class="{ on: s <= r.difficulty }">★</span>
                  </span>
                </div>
                <h4 class="rc-title">{{ r.title }}</h4>
                <div class="rc-footer">
                  <span class="rc-point">{{ r.knowledge_point }}</span>
                  <span class="rc-arrow">查看 →</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ===== Tab 3: 个性化学习 ===== -->
          <div v-show="activeTab === 'learning'" class="tab-content">
            <!-- 路径加载中 -->
            <div v-if="pathLoading" class="loading-area" style="padding:60px 0">
              <div class="loading-spinner"></div>
              <p>加载学习路径...</p>
            </div>

            <!-- 路径为空 -->
            <div v-else-if="!currentPath" class="tab-placeholder">
              <div class="placeholder-icon">🗺️</div>
              <h3>暂无学习路径</h3>
              <p>诊断完成后 AI 将自动生成个性化学习路径，请稍后刷新查看。</p>
            </div>

            <!-- 路径时间线 -->
            <div v-else class="path-timeline-card">
              <div class="path-status-row">
                <span class="path-status-badge" :class="currentPath.status">
                  {{ currentPath.status === 'active' ? '进行中' : currentPath.status === 'completed' ? '已完成' : '已放弃' }}
                </span>
                <span class="path-date">创建于 {{ formatPathTime(currentPath.created_at) }}</span>
              </div>

              <div class="timeline">
                <div
                  v-for="(step, i) in currentPath.steps"
                  :key="step.step"
                  class="timeline-step"
                  :class="{ last: i === currentPath.steps.length - 1 }"
                  @click="goToResource(step)"
                >
                  <div class="tl-left">
                    <div class="tl-node" :class="step.status">
                      <span v-if="step.status === 'completed'">✓</span>
                      <span v-else>{{ step.step }}</span>
                    </div>
                    <div v-if="i < currentPath.steps.length - 1" class="tl-line" :class="{ filled: step.status === 'completed' }"></div>
                  </div>
                  <div class="tl-content">
                    <div class="tl-title-row">
                      <span class="tl-type-icon">{{ typeIcon(step.resource_type) }}</span>
                      <span class="tl-point">{{ step.knowledge_point }}</span>
                      <span class="tl-type-tag">{{ step.resource_type }}</span>
                      <span v-if="step.weight === 'high'" class="tl-weight high">核心</span>
                      <span v-else-if="step.weight === 'mid'" class="tl-weight mid">支撑</span>
                    </div>
                    <div class="tl-meta">
                      <span>⏱ {{ step.estimated_time }} 分钟</span>
                      <span v-if="step.prerequisite">📎 前置：{{ step.prerequisite }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getAssessment, type AssessmentResponse } from '@/api/assessment'
import { getLearningPaths, type LearningPathInfo, type PathStep } from '@/api/path'
import { getResourceList, type ResourceInfo } from '@/api/resource'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

// ---- 评估 ID ----
const assessmentId = computed(() => (route.params.id as string) || null)

// ---- 加载评估 ----
const assessment = ref<AssessmentResponse | null>(null)
const loading = ref(false)
const loadError = ref('')

async function loadAssessment() {
  if (!assessmentId.value) return
  loading.value = true
  loadError.value = ''
  try {
    assessment.value = await getAssessment(assessmentId.value)
    loadPath()      // 拉取学习路径
    loadResources() // 拉取学习资料
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    loadError.value = typeof detail === 'string' ? detail : '加载诊断结果失败'
  } finally {
    loading.value = false
  }
}

// 路由参数变化时重新加载；无 ID 时自动跳转到最近诊断
watch(assessmentId, async () => {
  if (assessmentId.value) {
    loadAssessment()
  } else {
    // 确保 userInfo 已加载（登录时可能未成功写入 store）
    if (!store.userInfo && store.isLoggedIn) {
      try { await store.fetchUserInfo() } catch {}
    }
    const latestId = store.userInfo?.latest_assessment_id
    if (latestId) {
      router.replace(`/diagnosis/${latestId}`)
    } else {
      assessment.value = null
    }
  }
}, { immediate: true })

// ---- 学习路径 ----
const currentPath = ref<LearningPathInfo | null>(null)
const pathLoading = ref(false)

async function loadPath() {
  if (!assessment.value) return
  // 确保 userInfo 已加载
  if (!store.userInfo && store.isLoggedIn) {
    try { await store.fetchUserInfo() } catch {}
  }
  if (!store.userInfo) return
  pathLoading.value = true
  try {
    const paths = await getLearningPaths(store.userInfo.id)
    // 匹配当前诊断对应岗位的路径
    currentPath.value = paths.find(p => p.job_id === assessment.value!.job_id) || null
  } catch {
    currentPath.value = null
  } finally {
    pathLoading.value = false
  }
}

// ---- 学习资料 ----
const resources = ref<ResourceInfo[]>([])
const resourceLoading = ref(false)

async function loadResources() {
  if (!assessment.value) return
  resourceLoading.value = true
  try {
    const all = await getResourceList()
    // 只展示当前诊断知识缺口相关的资源，按 (知识点+类型) 去重保留最新
    const gaps = new Set(assessment.value.knowledge_gaps || [])
    const seen = new Map<string, ResourceInfo>()
    all
      .filter(r => gaps.has(r.knowledge_point))
      .forEach(r => {
        const key = `${r.knowledge_point}:${r.content_type}`
        if (!seen.has(key)) seen.set(key, r)
      })
    resources.value = [...seen.values()]
  } catch {
    resources.value = []
  } finally {
    resourceLoading.value = false
  }
}

function formatPathTime(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function typeIcon(t: string): string {
  return { '讲义': '📖', '练习': '✏️', '案例': '📋', '视频脚本': '🎬' }[t] || '📄'
}

function goToResource(step: PathStep) {
  if (step.resource_id) {
    router.push(`/resource/${step.resource_id}`)
  }
}

// ---- 掌握度分级 ----
const masteryLevelClass = computed(() => {
  if (!assessment.value) return ''
  const s = assessment.value.overall_mastery
  if (s >= 0.8) return 'high'
  if (s >= 0.6) return 'mid'
  return 'low'
})

const masteryLevelText = computed(() => {
  if (!assessment.value) return ''
  const s = assessment.value.overall_mastery
  if (s >= 0.8) return '已达标'
  if (s >= 0.6) return '部分达标'
  return '未达标'
})

// ---- 时间格式化 ----
function formatTime(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ---- Tab 切换 ----
const tabs = [
  { key: 'diagnosis', label: '诊断结果' },
  { key: 'library', label: '资料库' },
  { key: 'learning', label: '个性化学习' },
] as const
const activeTab = ref<string>('diagnosis')

// ---- 雷达图 ----
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value || !assessment.value) return

  const dims = assessment.value.ability_vector
  if (dims.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  // 按权重给每条轴着色
  const weightColors = { high: '#dc2626', mid: '#f59e0b', low: '#2563eb' }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const dim = dims[params.dataIndex]
        if (!dim) return params.name
        const weightLabel = { high: '高权重', mid: '中权重', low: '低权重' }[dim.weight]
        return `<b>${params.name}</b><br/>得分：${(dim.value * 100).toFixed(0)}<br/>权重：${weightLabel}<br/>类别：${dim.category}`
      },
    },
    radar: {
      center: ['50%', '55%'],
      radius: '65%',
      axisName: { fontSize: 12, color: '#555' },
      indicator: dims.map(d => ({
        name: d.name,
        max: 1,
        color: weightColors[d.weight] || '#555',
      })),
    },
    series: [
      {
        type: 'radar',
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#2563eb' },
        areaStyle: { color: 'rgba(37, 99, 235, 0.12)' },
        itemStyle: { color: '#2563eb' },
        data: [{ value: dims.map(d => d.value), name: '能力值' }],
      },
    ],
  }

  chartInstance.setOption(option)
}

// 数据就绪后渲染图表
watch(() => assessment.value?.ability_vector, () => {
  nextTick(() => renderChart())
})

// 窗口大小变化时重绘
function handleResize() {
  chartInstance?.resize()
}
window.addEventListener('resize', handleResize)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.diagnosis-page {
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
}

/* ---- 顶部渐变 ---- */
.diagnosis-hero {
  padding: 36px 80px 0;
  background: var(--hero-gradient);
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  margin-bottom: 6px;
}

.page-desc {
  font-size: 15px;
  color: #666;
}

/* ---- 内容区 ---- */
.page-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 80px 60px;
}

/* ---- 引导卡片（无 ID） ---- */
.guide-card {
  margin-top: 60px;
  text-align: center;
  background: #fff;
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.guide-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.guide-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
}

.guide-desc {
  font-size: 15px;
  color: #666;
  line-height: 1.7;
  max-width: 480px;
  margin: 0 auto 28px;
}

/* ---- 加载中 ---- */
.loading-area {
  margin-top: 60px;
  text-align: center;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: app-spin 0.7s linear infinite;
  margin: 0 auto 16px;
}

/* ---- 诊断中（未出结果） ---- */
.pending-card {
  margin-top: 40px;
  text-align: center;
  background: #fff;
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.pending-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.pending-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.pending-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.7;
  margin-bottom: 24px;
}

/* ---- Tab 栏 ---- */
.tab-bar {
  display: flex;
  gap: 0;
  background: #fff;
  border-radius: 12px;
  padding: 4px;
  margin-top: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: none;
  font-size: 15px;
  color: #888;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
  font-family: inherit;
}

.tab-btn.active {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
}

.tab-btn:hover:not(.active) {
  color: #555;
}

/* ---- Tab 内容 ---- */
.tab-content {
  margin-top: 24px;
}

/* ---- 概览行 ---- */
.overview-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.overview-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.overview-label {
  font-size: 15px;
  color: #888;
  margin-bottom: 20px;
  text-align: center;
}

/* ---- 掌握度圆环（CSS only） ---- */
.mastery-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  /* conic-gradient 做环形进度 */
  --pct: 0;
  background: conic-gradient(#2563eb calc(var(--pct) * 360deg), #e5e7eb 0deg);
}

.mastery-ring::after {
  content: '';
  position: absolute;
  width: 104px;
  height: 104px;
  border-radius: 50%;
  background: #fff;
}

.mastery-value {
  position: relative;
  z-index: 1;
  font-size: 36px;
  font-weight: 800;
  color: #111827;
  line-height: 1;
}

.mastery-unit {
  position: relative;
  z-index: 1;
  font-size: 14px;
  color: #888;
}

.mastery-tag {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  padding: 4px 16px;
  border-radius: 20px;
  display: inline-block;
  margin: 0 auto;
  width: fit-content;
}

.mastery-tag.high {
  background: #dcfce7;
  color: #16a34a;
}

.mastery-tag.mid {
  background: #fef3c7;
  color: #d97706;
}

.mastery-tag.low {
  background: #fee2e2;
  color: #dc2626;
}

.mastery-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ---- 元数据卡片 ---- */
.meta-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  justify-content: center;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
}

.meta-label {
  font-size: 14px;
  color: #888;
}

.meta-value {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.meta-value.warn {
  color: #dc2626;
}

/* ---- 图表卡片 ---- */
.chart-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.card-subtitle {
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
}

.radar-chart {
  width: 100%;
  height: 420px;
}

/* ---- 知识缺口 ---- */
.gaps-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.gaps-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gap-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: 8px;
  border-left: 3px solid #fca5a5;
}

.gap-index {
  width: 24px;
  height: 24px;
  background: #fca5a5;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.gap-text {
  font-size: 14px;
  color: #991b1b;
  line-height: 1.7;
}

/* ---- 底部操作 ---- */
.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 8px;
}

/* ---- 占位 Tab ---- */
.tab-placeholder {
  margin-top: 24px;
  background: #fff;
  border-radius: 16px;
  padding: 80px 40px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.tab-placeholder h3 {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.tab-placeholder p {
  color: #999;
  font-size: 14px;
}

/* ---- 学习路径时间线 ---- */
.path-timeline-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.path-status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.path-status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
}

.path-status-badge.active {
  background: #dbeafe;
  color: #2563eb;
}

.path-status-badge.completed {
  background: #dcfce7;
  color: #16a34a;
}

.path-status-badge.abandoned {
  background: #f3f4f6;
  color: #888;
}

.path-date {
  font-size: 13px;
  color: #999;
}

.timeline {
  padding-left: 4px;
}

.timeline-step {
  display: flex;
  gap: 16px;
}

.timeline-step:not(.last) {
  padding-bottom: 4px;
}

.tl-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.tl-node {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  background: #f0f0f0;
  color: #999;
  transition: all 0.3s;
}

.tl-node.completed {
  background: #16a34a;
  color: #fff;
}

.tl-node.in_progress {
  background: #2563eb;
  color: #fff;
}

.tl-line {
  width: 2px;
  flex: 1;
  min-height: 28px;
  background: #e5e7eb;
  transition: background 0.3s;
}

.tl-line.filled {
  background: #16a34a;
}

.tl-content {
  flex: 1;
  padding: 6px 0 16px;
}

.tl-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tl-type-icon {
  font-size: 16px;
}

.tl-point {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.tl-type-tag {
  font-size: 12px;
  padding: 2px 8px;
  background: #f3f4f6;
  color: #666;
  border-radius: 4px;
}

.tl-weight {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.tl-weight.high {
  background: #fee2e2;
  color: #dc2626;
}

.tl-weight.mid {
  background: #fef3c7;
  color: #d97706;
}

.tl-meta {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  font-size: 13px;
  color: #999;
}

/* ---- 资源卡片网格 ---- */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.resource-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.resource-card:hover {
  border-color: #2563eb;
  box-shadow: 0 2px 12px rgba(37, 99, 235, 0.08);
  transform: translateY(-1px);
}

.rc-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.rc-type-icon {
  font-size: 20px;
}

.rc-type-tag {
  font-size: 12px;
  padding: 2px 8px;
  background: #eef2ff;
  color: #2563eb;
  border-radius: 4px;
  font-weight: 500;
}

.rc-difficulty {
  margin-left: auto;
  display: flex;
  gap: 1px;
}

.star {
  font-size: 13px;
  color: #e5e7eb;
}

.star.on {
  color: #f59e0b;
}

.rc-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 10px;
  line-height: 1.4;
}

.rc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rc-point {
  font-size: 12px;
  color: #888;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.rc-arrow {
  font-size: 13px;
  color: #2563eb;
}
</style>
