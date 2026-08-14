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
          <p class="pending-label">{{ progress.label }}</p>
          <div class="pending-progress-wrap">
            <el-progress :percentage="progress.percent" :stroke-width="10" />
          </div>
          <p class="pending-percent">{{ progress.percent }}%</p>
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
                <div class="overview-label">
                  综合掌握度
                  <el-tooltip placement="top" effect="light" :show-after="150">
                    <template #content>
                      <div class="tip-box">
                        <div class="tip-title">综合掌握度</div>
                        <p><b>是什么：</b>对照目标岗位能力模型，对你当前能力水平的整体打分（0–100 分），由各能力维度按权重加权汇总得出，反映你相对该岗位的「整体胜任程度」。</p>
                        <p><b>怎么读：</b>分数越高越接近岗位要求；60 分以下说明仍有明显能力缺口。</p>
                        <p class="tip-diff"><b>与置信度的区别：</b>掌握度回答「你水平有多高」，置信度回答「这个结论有多可信」。</p>
                      </div>
                    </template>
                    <span class="help-circle">?</span>
                  </el-tooltip>
                </div>
                <div class="mastery-ring" :style="{ '--pct': assessment.overall_mastery }">
                  <span class="mastery-value">{{ Math.round(assessment.overall_mastery * 100) }}</span>
                  <span class="mastery-unit">分</span>
                </div>
                <div class="mastery-tag" :class="masteryLevelClass">{{ masteryLevelText }}</div>
              </div>
              <div class="overview-card meta-card">
                <div class="meta-item">
                  <span class="meta-label">
                    置信度
                    <el-tooltip placement="top" effect="light" :show-after="150">
                      <template #content>
                        <div class="tip-box">
                          <div class="tip-title">置信度</div>
                          <p><b>是什么：</b>AI 对本次诊断结论「可信程度」的估计（0–100%）。</p>
                          <p><b>取决于：</b>你提供的信息量——经历描述越具体、证据越充分，置信度越高；信息越模糊或不足，置信度越低。</p>
                          <p><b>怎么读：</b>置信度高 = 结果可靠，可放心参考；置信度低 = 输入信息有限，结果仅供参考，建议补充经历后重新诊断。</p>
                          <p class="tip-diff"><b>与掌握度的区别：</b>置信度回答「这个结论有多可信」，掌握度回答「你水平有多高」。</p>
                        </div>
                      </template>
                      <span class="help-circle">?</span>
                    </el-tooltip>
                  </span>
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

            <!-- 用户输入原文（可折叠） -->
            <div v-if="assessment.user_input" class="input-review-card">
              <div class="irc-header" @click="showInput = !showInput">
                <span class="irc-title">📝 我的输入</span>
                <span class="irc-toggle">{{ showInput ? '收起 ▲' : '展开 ▼' }}</span>
              </div>
              <div v-show="showInput" class="irc-body">{{ assessment.user_input }}</div>
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

            <!-- 防幻觉校验汇总 -->
            <div class="anti-hallucination-card">
              <h3 class="card-title">
                🛡️ 防幻觉校验
                <el-tooltip placement="top" effect="light" :show-after="150">
                  <template #content>
                    <div class="tip-box tip-box-wide">
                      <div class="tip-title">资源校验状态说明</div>
                      <p><b>有依据</b>：有知识库原文，且已比对，确认内容忠实于原文、没有编造。</p>
                      <p><b>部分匹配</b>：有知识库原文，比对后大部分有依据、小部分存疑。</p>
                      <p><b>无依据</b>：有知识库原文，但比对后发现编造或偏离，已过滤。</p>
                      <p><b>未知</b>：没有知识库原文可比，跳过校验，无结论。</p>
                      <p class="tip-diff">补充：知识缺口与学习资源均由 AI 生成，受当前知识库收录范围所限，部分正确知识尚未入库，可能被误判为「无依据」。后续可继续扩充知识库，逐步提升防幻觉校验的准确度与输出质量。</p>
                    </div>
                  </template>
                  <span class="help-circle">?</span>
                </el-tooltip>
              </h3>
              <p class="card-subtitle">AI 诊断结论与生成内容均已对照岗位能力模型 / 知识库比对校验</p>

              <!-- 层1：知识缺口校验 -->
              <div class="ah-layer">
                <div class="ah-layer-header" @click="showGapDetail = !showGapDetail">
                  <div class="ah-layer-summary">
                    <span class="ah-layer-tag">层1 知识缺口</span>
                    <span class="ah-summary-text">
                      诊断发现 {{ gapValidationStats.total }} 个缺口 →
                      有依据 <b class="c-ok">{{ gapValidationStats.grounded }}</b> ·
                      部分匹配 <b class="c-warn">{{ gapValidationStats.partial }}</b> ·
                      无依据 <b class="c-bad">{{ gapValidationStats.ungrounded }}</b>
                      <span class="ah-blocked">（拦截 {{ gapValidationStats.ungrounded }}）</span>
                    </span>
                  </div>
                  <span class="ah-toggle">{{ showGapDetail ? '收起 ▲' : '展开 ▼' }}</span>
                </div>
                <div v-show="showGapDetail" class="ah-detail">
                  <div v-for="(g, i) in (assessment.gap_validation || [])" :key="i" class="ah-detail-item">
                    <span class="ah-detail-gap">{{ g.gap }}</span>
                    <span class="ah-badge" :class="validationBadge(g.status).cls">
                      {{ validationBadge(g.status).text }}{{ g.status === 'ungrounded' ? '·已拦截' : '' }}
                    </span>
                    <span class="ah-detail-reason">{{ g.reason }}</span>
                  </div>
                  <div v-if="!assessment.gap_validation || assessment.gap_validation.length === 0" class="ah-detail-empty">
                    暂无缺口校验明细
                  </div>
                </div>
              </div>

              <!-- 层2：学习资源校验 -->
              <div class="ah-layer">
                <div class="ah-layer-header" @click="showResourceDetail = !showResourceDetail">
                  <div class="ah-layer-summary">
                    <span class="ah-layer-tag">层2 学习资源</span>
                    <span class="ah-summary-text">
                      共生成 {{ resourceValidationStats.total }} 条资源 →
                      有依据 <b class="c-ok">{{ resourceValidationStats.passed }}</b> ·
                      部分匹配 <b class="c-warn">{{ resourceValidationStats.partial }}</b> ·
                      无依据 <b class="c-bad">{{ resourceValidationStats.blocked }}</b> ·
                      未知 <b class="c-skip">{{ resourceValidationStats.unknown }}</b>
                      <span class="ah-blocked">（过滤 {{ resourceValidationStats.blocked }}）</span>
                      <span v-if="resourceValidationStats.skipped > 0" class="ah-skipped">· 跳过校验 {{ resourceValidationStats.skipped }}</span>
                    </span>
                  </div>
                  <span class="ah-toggle">{{ showResourceDetail ? '收起 ▲' : '展开 ▼' }}</span>
                </div>
                <div v-show="showResourceDetail" class="ah-detail">
                  <div v-for="r in resources" :key="r.id" class="ah-detail-item">
                    <span class="ah-detail-gap">{{ r.title }}</span>
                    <span class="ah-badge" :class="validationBadge(r.review_status).cls">
                      {{ validationBadge(r.review_status).text }}{{ r.review_status === 'blocked' ? '·已过滤' : '' }}
                    </span>
                    <span class="ah-detail-reason">{{ r.review_reason || '—' }}</span>
                  </div>
                  <div v-if="resources.length === 0" class="ah-detail-empty">暂无资源校验明细</div>
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
            <div v-else-if="visibleResources.length === 0" class="tab-placeholder">
              <div class="placeholder-icon">📚</div>
              <h3>暂无学习资料</h3>
              <p>诊断完成后 AI 将根据你的知识缺口自动生成学习资料。</p>
            </div>

            <!-- 资源卡片列表 -->
            <div v-else class="resource-grid">
              <div
                v-for="r in visibleResources"
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
import { getAssessment, getAssessmentProgress, type AssessmentResponse } from '@/api/assessment'
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

// ---- 诊断进度轮询 ----
const progress = ref<{ label: string; percent: number }>({ label: '正在解析学习情况', percent: 0 })
let progressTimer: number | null = null

function stopProgressPolling() {
  if (progressTimer !== null) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

function startProgressPolling() {
  stopProgressPolling()
  progressTimer = window.setInterval(async () => {
    if (!assessmentId.value) return
    try {
      const p = await getAssessmentProgress(assessmentId.value)
      progress.value = p
      if (p.percent >= 100) {
        stopProgressPolling()
        loadAssessment()   // 诊断完成，拉取最终结果
      }
    } catch {
      // 单次失败忽略，下个周期继续
    }
  }, 10_000)
}

async function loadAssessment() {
  if (!assessmentId.value) return
  loading.value = true
  loadError.value = ''
  try {
    assessment.value = await getAssessment(assessmentId.value)
    // 诊断未完成 → 轮询进度；已完成 → 停轮询
    if (assessment.value.overall_mastery === null) {
      startProgressPolling()
    } else {
      stopProgressPolling()
    }
    nextTick(() => renderChart())  // 雷达图立即渲染
    loading.value = false          // 立即显示结果区（含雷达图）
    loadPath()                     // 路径、资料后台异步加载，互不阻塞
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    loadError.value = typeof detail === 'string' ? detail : '加载诊断结果失败'
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

// 切换诊断记录时销毁旧图表实例，避免指向已销毁的 DOM 容器
watch(assessmentId, () => {
  stopProgressPolling()
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  // 清空上一记录的数据，避免闪现旧内容
  currentPath.value = null
  resources.value = []
})

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
  loadResources()  // 路径就绪后再加载资源（资源过滤依赖路径知识点）
}

// ---- 学习资料 ----
const resources = ref<ResourceInfo[]>([])
const resourceLoading = ref(false)

async function loadResources() {
  if (!assessment.value) return
  resourceLoading.value = true
  try {
    const all = await getResourceList()
    // 用路径的知识点过滤资源（资源是按路径知识点生成的，两者天然对齐）
    const pathPoints = new Set(
      currentPath.value?.steps?.map(s => s.knowledge_point) || []
    )
    const gaps = new Set(assessment.value.knowledge_gaps || [])
    const seen = new Map<string, ResourceInfo>()
    // 优先匹配路径知识点，其次匹配 knowledge_gaps
    all
      .filter(r => pathPoints.has(r.knowledge_point) || gaps.has(r.knowledge_point))
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

// ---- 防幻觉校验 ----
const VALIDATION_STATUS: Record<string, { text: string; cls: string }> = {
  grounded: { text: '有依据', cls: 'ok' },
  passed: { text: '有依据', cls: 'ok' },
  partial: { text: '部分匹配', cls: 'warn' },
  ungrounded: { text: '无依据', cls: 'bad' },
  blocked: { text: '无依据', cls: 'bad' },
  skipped: { text: '跳过校验', cls: 'skip' },
}

function validationBadge(status: string | null): { text: string; cls: string } {
  return VALIDATION_STATUS[status || ''] || { text: status || '未知', cls: 'skip' }
}

const gapValidationStats = computed(() => {
  const items = assessment.value?.gap_validation || []
  return {
    total: items.length,
    grounded: items.filter(g => g.status === 'grounded').length,
    partial: items.filter(g => g.status === 'partial').length,
    ungrounded: items.filter(g => g.status === 'ungrounded').length,
  }
})

const resourceValidationStats = computed(() => {
  const items = resources.value
  const known = new Set(['passed', 'partial', 'blocked', 'skipped'])
  return {
    total: items.length,
    passed: items.filter(r => r.review_status === 'passed').length,
    partial: items.filter(r => r.review_status === 'partial').length,
    blocked: items.filter(r => r.review_status === 'blocked').length,
    skipped: items.filter(r => r.review_status === 'skipped').length,
    unknown: items.filter(r => !r.review_status || !known.has(r.review_status)).length,
  }
})

// 展示层过滤掉被拦截（blocked）的资源；统计仍基于完整 resources
const visibleResources = computed(() =>
  resources.value.filter(r => r.review_status !== 'blocked'),
)

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

// ---- 用户输入折叠展示 ----
const showInput = ref(false)

// ---- 防幻觉校验展开状态 ----
const showGapDetail = ref(false)
const showResourceDetail = ref(false)

// ---- 雷达图 ----
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function renderChart() {
  console.log('[雷达图] renderChart 调用', {
    hasChartRef: !!chartRef.value,
    hasAssessment: !!assessment.value,
    dimsCount: assessment.value?.ability_vector?.length,
    activeTab: activeTab.value,
  })

  if (!chartRef.value) { console.warn('[雷达图] chartRef 不存在，跳过'); return }
  if (!assessment.value) { console.warn('[雷达图] assessment 不存在，跳过'); return }

  const dims = assessment.value.ability_vector
  console.log('[雷达图] ability_vector 维度数:', dims?.length, '示例:', dims?.[0])

  if (!dims || dims.length === 0) {
    console.warn('[雷达图] ability_vector 为空，跳过')
    return
  }

  if (!chartInstance) {
    console.log('[雷达图] 初始化 ECharts 实例')
    chartInstance = echarts.init(chartRef.value)
  }

  // 按权重给每条轴着色
  const weightColors = { high: '#dc2626', mid: '#f59e0b', low: '#2563eb' }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const dim = dims[params.dimensionIndex]
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
  console.log('[雷达图] setOption 完成，indicator 数量:', dims.length)
}

// 数据就绪后渲染图表
watch(() => assessment.value?.ability_vector, () => {
  nextTick(() => renderChart())
})

// 切换到"诊断结果"tab 时重绘雷达图（解决 DOM 未渲染时初始化失败的问题）
watch(activeTab, (tab) => {
  if (tab === 'diagnosis') {
    nextTick(() => renderChart())
  }
})

// 窗口大小变化时重绘
function handleResize() {
  chartInstance?.resize()
}
window.addEventListener('resize', handleResize)

onBeforeUnmount(() => {
  stopProgressPolling()
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
  animation: pending-hourglass 4s ease-in-out infinite;
}

@keyframes pending-hourglass {
  0%   { transform: rotate(0deg); }
  50%  { transform: rotate(180deg); }
  100% { transform: rotate(0deg); }
}

.pending-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.pending-label {
  font-size: 15px;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 20px;
}

.pending-progress-wrap {
  max-width: 480px;
  margin: 0 auto;
}

.pending-percent {
  font-size: 14px;
  color: #888;
  margin-top: 12px;
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
  max-width: 260px;
  line-height: 1.6;
  text-align: left;
}

.tip-box-wide {
  max-width: 360px;
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

.tip-box p b {
  color: #111827;
}

.tip-diff {
  margin-top: 6px !important;
  padding-top: 6px;
  border-top: 1px solid #eee;
  color: #d97706 !important;
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

/* ---- 用户输入卡片（可折叠） ---- */
.input-review-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.irc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.irc-title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

.irc-toggle {
  font-size: 13px;
  color: #2563eb;
}

.irc-body {
  margin-top: 12px;
  padding: 14px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #444;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
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

/* ---- 防幻觉校验汇总卡 ---- */
.anti-hallucination-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.ah-layer {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  margin-top: 12px;
  overflow: hidden;
}

.ah-layer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  user-select: none;
}

.ah-layer-header:hover {
  background: #fafbfc;
}

.ah-layer-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.ah-layer-tag {
  font-size: 13px;
  font-weight: 700;
  color: #111827;
  background: #eef2ff;
  padding: 3px 10px;
  border-radius: 6px;
  white-space: nowrap;
}

.ah-summary-text {
  font-size: 14px;
  color: #555;
}

.ah-summary-text b {
  font-weight: 700;
}

.c-ok { color: #16a34a; }
.c-warn { color: #d97706; }
.c-bad { color: #dc2626; }
.c-skip { color: #888; }

.ah-blocked {
  color: #dc2626;
  font-weight: 600;
}

.ah-skipped {
  color: #999;
  font-size: 13px;
}

.ah-toggle {
  font-size: 13px;
  color: #2563eb;
  flex-shrink: 0;
  margin-left: 12px;
}

.ah-detail {
  border-top: 1px solid #f0f0f0;
  padding: 8px 16px 12px;
}

.ah-detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px dashed #f0f0f0;
}

.ah-detail-item:last-child {
  border-bottom: none;
}

.ah-detail-gap {
  font-weight: 600;
  color: #111827;
  flex-shrink: 0;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ah-detail-reason {
  color: #888;
  flex: 1;
  line-height: 1.5;
}

.ah-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  flex-shrink: 0;
  white-space: nowrap;
}

.ah-badge.ok { background: #dcfce7; color: #16a34a; }
.ah-badge.warn { background: #fef3c7; color: #d97706; }
.ah-badge.bad { background: #fee2e2; color: #dc2626; }
.ah-badge.skip { background: #f3f4f6; color: #888; }

.ah-detail-empty {
  padding: 12px 0;
  color: #999;
  font-size: 13px;
}
</style>
