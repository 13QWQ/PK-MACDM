<template>
  <div class="page-shell diagnosis-page">
    <div class="content-width">
      <header class="diagnosis-heading motion-enter">
        <div><span class="eyebrow">DIAGNOSTIC CORE</span><h1 class="page-title">能力诊断 <MagicStick /></h1><p class="page-subtitle">基于岗位能力模型与可追溯证据，形成多维能力判断、真实结果校准和下一阶段学习建议。</p></div>
        <div class="heading-actions"><button type="button" class="top-action" :disabled="loading || running" @click="loadAssessment"><Refresh /> 重新读取</button><button type="button" class="top-action primary" :disabled="demoMode || !assessment || !requirementItems.length" @click="showCalibration = !showCalibration"><Aim /> {{ showCalibration ? '收起校准' : '校准准确率' }}</button></div>
      </header>

      <section v-if="loading || running" class="diagnosis-loading glass-surface">
        <img src="/assets/diagnostic-platform.png" alt="正在运行的诊断空间核心" />
        <div class="loading-copy"><span class="glass-pill"><Loading /> Agent 运行中</span><h2>{{ running ? progress.label : '正在读取诊断报告' }}</h2><p>{{ running ? `${progress.percent}% · 系统会在真实 Agent 任务完成后自动刷新` : '正在加载本次诊断的真实数据' }}</p><div class="loading-track"><i :style="{ width: `${Math.max(8, progress.percent)}%` }"></i></div></div>
      </section>

      <section v-else-if="loadError" class="diagnosis-error glass-surface"><WarningFilled /><div><h2>{{ loadError }}</h2><p>请检查本次诊断是否已完成，或返回资料审查重新启动任务。</p></div><button type="button" @click="router.push('/input')">前往资料审查</button></section>

      <section v-else-if="!assessment" class="empty-diagnostic glass-surface motion-enter motion-delay-1">
        <div class="empty-visual-grid">
          <aside class="empty-match-preview"><span class="empty-label">岗位匹配度</span><strong>--</strong><small>等待能力证据</small><div class="empty-glass-orb"><Briefcase /></div></aside>
          <div class="empty-core-stage"><img src="/assets/diagnostic-platform.png" alt="待激活的能力诊断空间核心" /><div class="empty-core-copy"><span class="glass-pill"><DataAnalysis /> Diagnostic Core</span><h2>完成资料审查，激活能力诊断核心</h2><p>系统将汇总资料证据、能力问答与岗位要求，生成评分、雷达图和优先学习路径。</p><button class="primary-gradient-button" type="button" @click="router.push('/input')">开始资料审查 <ArrowRight /></button></div></div>
          <aside class="empty-dimension-preview"><span class="empty-label">能力维度</span><div v-for="name in emptyDimensions" :key="name"><span>{{ name }}</span><i></i><em>待评估</em></div></aside>
        </div>
        <div class="empty-process"><div v-for="(step, index) in emptySteps" :key="step.title"><span><component :is="step.icon" /></span><b>{{ index + 1 }}. {{ step.title }}</b><small>{{ step.detail }}</small></div></div>
      </section>

      <template v-else>
        <section v-if="showCalibration" class="calibration-panel glass-surface motion-enter"><div><span class="glass-pill">真实结果校准</span><h2>录入客观题、实操或专家标注结果</h2><p>系统仅在收到可追溯的真实结果后计算准确率；未校准不等于准确率低。</p></div><div class="calibration-fields"><label v-for="item in requirementItems" :key="item.requirement_id"><span>{{ item.requirement_name }}</span><input v-model.number="goldScores[item.requirement_id]" type="number" min="0" max="100" placeholder="0–100" /></label></div><div class="calibration-actions"><label class="correction-check"><input v-model="applyCorrections" type="checkbox" /> 将可信结果用于校正本次诊断</label><button type="button" :disabled="calibrationSubmitting" @click="submitCalibration">{{ calibrationSubmitting ? '校准中…' : '提交真实结果' }}</button></div></section>

        <section class="core-grid motion-enter motion-delay-1">
          <article class="match-card glass-surface">
            <div class="card-heading"><span class="card-eyebrow">总体匹配度</span><Briefcase /></div>
            <p>与 {{ jobTitle }} 能力模型匹配度</p>
            <strong class="gradient-number">{{ overallPercent }}<small>%</small></strong>
            <span class="match-badge" :class="levelClass"><i></i>{{ levelText }}</span>
            <div class="match-insight"><span>诊断置信度</span><b>{{ confidencePercent }}%</b></div>
            <footer>基于 {{ traceSourceCount || '待加载' }} 条可追溯依据</footer>
          </article>

          <article class="diagnostic-core" @pointermove="moveSpotlight">
            <img class="diagnostic-platform" src="/assets/diagnostic-platform.png" alt="绿色玻璃质感的能力诊断空间平台" />
            <div class="core-glass glass-surface">
              <div class="core-topline"><span>综合得分</span><span>能力雷达图</span></div>
              <div class="core-body"><div class="score-dial" :style="{ '--score': `${overallPercent * 3.6}deg` }"><div><b class="gradient-number">{{ overallPercent }}</b><small>/100</small><em>{{ levelText }}</em></div></div><div ref="radarRef" class="radar-chart"></div></div>
              <div class="core-meta"><span>评估于 {{ formattedDate }}</span><span>·</span><span>{{ traceLabel }}</span><span v-if="demoMode" class="demo-badge">DEV 示例</span></div>
            </div>
          </article>

          <article class="dimension-card glass-surface">
            <div class="dimension-head"><span class="card-eyebrow">能力维度评分</span><span class="dimension-count">{{ assessment.ability_vector?.length || 0 }} 项</span></div>
            <div class="dimension-list"><div v-for="item in dimensionPreview" :key="item.index" class="dimension-row"><div><span class="dimension-icon"><component :is="dimensionIcon(item.index)" /></span><b>{{ item.name }}</b></div><strong>{{ toPercent(item.value) }}<small>/100</small></strong><div class="dimension-bar"><i :style="{ width: `${toPercent(item.value)}%` }"></i></div></div></div>
          </article>
        </section>

        <section class="analysis-grid motion-enter motion-delay-2">
          <article class="evidence-insights glass-surface">
            <section class="strengths"><h2><StarFilled /> 优势亮点</h2><ul v-if="strengths.length"><li v-for="item in strengths" :key="item.index"><span><CircleCheck /></span><div><b>{{ item.name }}</b><small>{{ toPercent(item.value) }} 分 · 已具备较强能力证据</small></div></li></ul><p v-else>本次诊断暂未形成足够的优势能力结论。</p></section>
            <section class="gaps"><h2><WarningFilled /> 待提升项</h2><ul v-if="gaps.length"><li v-for="(gap, index) in gaps.slice(0, 3)" :key="gap"><b>{{ String(index + 1).padStart(2, '0') }}</b><span>{{ gap }}</span></li></ul><p v-else>当前未识别到需要优先补强的能力缺口。</p></section>
          </article>

          <article class="agent-summary glass-surface"><span class="agent-face"><Cpu /></span><h2>Agent 综合结论</h2><p>{{ agentSummary }}</p><div class="summary-evidence"><Files /><span>资料证据 · 项目描述 · 学习轨迹</span></div><div class="review-metric"><span>真实结果准确率</span><b :class="accuracyClass">{{ calibrationText }}</b></div><button type="button" @click="openLibrary">查看推荐学习资料 <ArrowRight /></button></article>

          <article class="roadmap-card glass-surface"><div class="roadmap-heading"><h2><MapLocation /> 优先学习路径</h2><span>推荐</span></div><div v-if="pathLoading" class="path-empty">正在读取学习路径…</div><div v-else-if="currentPath?.steps?.length" class="roadmap"><div class="roadmap-line"></div><div v-for="(step, index) in currentPath.steps.slice(0, 3)" :key="step.step" class="roadmap-step" :class="{ current: index === 0 }"><span>{{ String(index + 1).padStart(2, '0') }}</span><div><b>{{ step.knowledge_point }}</b><small>{{ step.resource_type }} · {{ step.estimated_time }} 分钟</small></div></div></div><div v-else class="path-empty">本次诊断尚未生成可展示的学习路径。</div></article>
        </section>

        <section class="quality-strip glass-panel"><div><CircleCheck /><span>防幻觉审核</span><b>{{ resourceQualityText }}</b></div><div><Files /><span>证据链来源</span><b>{{ traceSourceCount }} 条检索依据</b></div><div><Aim /><span>校准状态</span><b>{{ calibrationStatusText }}</b></div><button type="button" @click="openLibrary">进入资料库 <ArrowRight /></button></section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Aim, ArrowRight, Briefcase, CircleCheck, Connection, Cpu, DataAnalysis, DocumentChecked,
  Files, Guide, Loading, MagicStick, MapLocation, Refresh, Search, StarFilled,
  TrendCharts, WarningFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { calibrateAssessment, getAssessment, getAssessmentAgents, getAssessmentProgress, type AssessmentResponse, type RequirementScore } from '@/api/assessment'
import { getLearningPaths, type LearningPathInfo } from '@/api/path'
import { getResourceList, type ResourceInfo } from '@/api/resource'
import { getJobList } from '@/api/jobs'
import { useUserStore } from '@/stores/user'

const route = useRoute(); const router = useRouter(); const store = useUserStore()
const publicPreview = import.meta.env.VITE_PUBLIC_PREVIEW === 'true'
const demoMode = computed(() => publicPreview && route.query.demo === '1')
const assessment = ref<AssessmentResponse | null>(null); const loading = ref(false); const loadError = ref(''); const progress = ref({ label: '正在解析学习情况', percent: 0 }); const running = ref(false)
const radarRef = ref<HTMLDivElement | null>(null); let chart: echarts.ECharts | null = null; let progressTimer: number | null = null
const currentPath = ref<LearningPathInfo | null>(null); const pathLoading = ref(false); const resources = ref<ResourceInfo[]>([]); const traceSourceCount = ref(0)
const showCalibration = ref(false); const calibrationSubmitting = ref(false); const applyCorrections = ref(false); const goldScores = ref<Record<string, number | null>>({})
const jobTitle = ref('目标岗位能力模型')
const assessmentId = computed(() => typeof route.params.id === 'string' ? route.params.id : '')
const overallPercent = computed(() => Math.round((assessment.value?.overall_mastery || 0) * 100)); const confidencePercent = computed(() => Math.round((assessment.value?.confidence || 0) * 100)); const formattedDate = computed(() => assessment.value ? new Date(assessment.value.created_at).toLocaleDateString('zh-CN') : '—')
const dimensionPreview = computed(() => (assessment.value?.ability_vector || []).slice(0, 5)); const strengths = computed(() => [...(assessment.value?.ability_vector || [])].sort((a,b) => b.value - a.value).slice(0, 3)); const gaps = computed(() => assessment.value?.knowledge_gaps || []); const requirementItems = computed<RequirementScore[]>(() => assessment.value?.requirement_scores || [])
const levelClass = computed(() => overallPercent.value >= 80 ? 'good' : overallPercent.value >= 60 ? 'partial' : 'needs'); const levelText = computed(() => overallPercent.value >= 80 ? '良好匹配' : overallPercent.value >= 60 ? '部分匹配' : '优先补强')
const calibration = computed(() => assessment.value?.calibration_summary); const calibrationText = computed(() => calibration.value?.accuracy === null || calibration.value?.accuracy === undefined ? '待校准' : `${Math.round(calibration.value.accuracy * 100)}%`); const accuracyClass = computed(() => calibration.value?.accuracy && calibration.value.accuracy >= .9 ? 'accurate' : 'pending')
const calibrationStatusText = computed(() => assessment.value?.calibration_status === 'passed' ? '已通过' : assessment.value?.calibration_status === 'needs_review' ? '需要复核' : '未校准')
const resourceQualityText = computed(() => !resources.value.length ? '暂无可展示资源' : `${resources.value.filter(item => item.review_status === 'passed').length}/${resources.value.length} 已通过来源校验`)
const traceLabel = computed(() => traceSourceCount.value ? `${traceSourceCount.value} 条依据` : '证据待加载')
const agentSummary = computed(() => { const high = strengths.value.slice(0,2).map(item => item.name).join('、'); const low = [...(assessment.value?.ability_vector || [])].sort((a,b) => a.value - b.value)[0]?.name; if (!high && !low) return '本次诊断尚未形成完整的能力结论。'; return `你已具备较稳定的岗位基础，当前优势集中在${high || '已提交证据覆盖的能力'}。影响下一阶段竞争力的主要因素不是学习资源数量，而是${low || '复杂任务经验'}仍需补强。建议围绕能力缺口完成一次可验证的项目实践，并在复测后更新路径。` })
const emptyDimensions = ['工程能力', '项目经验', '学习潜力', '基础能力', '软实力']
const emptySteps: Array<{ icon: Component; title: string; detail: string }> = [
  { icon: DocumentChecked, title: '资料审查', detail: '提取学习与项目证据' },
  { icon: Search, title: '能力映射', detail: '对照岗位要求和达标规则' },
  { icon: Aim, title: '交叉校验', detail: '复核结论与来源依据' },
  { icon: Guide, title: '路径生成', detail: '输出下一阶段学习行动' },
]
const dimensionIcons: Component[] = [Cpu, Briefcase, TrendCharts, DataAnalysis, Connection]

const demoAssessment: AssessmentResponse = {
  id: 'demo-assessment', user_id: 'demo-user', job_id: 'demo-backend', user_input: '本地视觉验收示例', overall_mastery: .82, confidence: .94,
  ability_vector: [
    { index: 0, name: '工程能力', value: .85, weight: 'high', category: 'engineering' },
    { index: 1, name: '项目经验', value: .78, weight: 'high', category: 'project' },
    { index: 2, name: '学习潜力', value: .88, weight: 'mid', category: 'learning' },
    { index: 3, name: '基础能力', value: .74, weight: 'mid', category: 'foundation' },
    { index: 4, name: '软实力', value: .80, weight: 'low', category: 'soft_skill' },
  ],
  knowledge_gaps: ['复杂项目经验不足，缺少大型系统实践', '系统设计与架构思维需要加强', '高并发与分布式技术广度有待拓展'],
  gap_validation: [],
  requirement_scores: [
    { requirement_id: 'demo-r1', requirement_name: '工程实践', dimension: '工程能力', score: .85, status: 'qualified', evidence_ids: ['demo-e1'] },
    { requirement_id: 'demo-r2', requirement_name: '系统设计', dimension: '项目经验', score: .72, status: 'partial', evidence_ids: ['demo-e2'] },
    { requirement_id: 'demo-r3', requirement_name: '学习迁移', dimension: '学习潜力', score: .88, status: 'qualified', evidence_ids: ['demo-e3'] },
  ],
  calibration_status: 'passed',
  calibration_summary: { status: 'passed', evaluated_count: 3, accuracy: .93, mean_absolute_error: .06 },
  material_ids: ['demo-m1', 'demo-m2'], created_at: '2026-08-16T10:20:00+08:00',
}
const demoPath: LearningPathInfo = {
  id: 'demo-path', user_id: 'demo-user', job_id: 'demo-backend', assessment_id: 'demo-assessment', current_step: 1, status: 'active', created_at: '2026-08-16T10:20:00+08:00', updated_at: '2026-08-16T10:20:00+08:00',
  steps: [
    { step: 1, knowledge_point: '夯实工程基础', resource_type: '讲义 + 实操', resource_id: null, estimated_time: 120, prerequisite: null, status: 'current', record_id: null, weight: 'high' },
    { step: 2, knowledge_point: '项目进阶', resource_type: '项目任务书', resource_id: null, estimated_time: 180, prerequisite: '夯实工程基础', status: 'pending', record_id: null, weight: 'high' },
    { step: 3, knowledge_point: '综合突破', resource_type: '阶段复测', resource_id: null, estimated_time: 90, prerequisite: '项目进阶', status: 'pending', record_id: null, weight: 'mid' },
  ],
}
const demoResources: ResourceInfo[] = [0,1,2].map(index => ({ id: `demo-resource-${index}`, assessment_id: 'demo-assessment', knowledge_point: ['系统设计基础','并发编程','项目复盘'][index], content_type: ['讲义','实操任务','错题解析'][index], title: ['系统设计核心概念','并发任务实战','项目问题复盘'][index], body: '仅用于本地视觉验收的示例资料。', difficulty: index + 2, source_chunk_id: `demo-source-${index}`, source_text: '本地视觉示例来源', review_status: 'passed', review_reason: '示例已通过', display_status: 'visible', generation_method: 'demo', created_at: '2026-08-16T10:20:00+08:00' }))

function toPercent(value: number) { return Math.round(value * 100) }
function dimensionIcon(index: number) { return dimensionIcons[index % dimensionIcons.length] }
function moveSpotlight(event: PointerEvent) { const element = event.currentTarget as HTMLElement; const rect = element.getBoundingClientRect(); element.style.setProperty('--spot-x', `${event.clientX - rect.left}px`); element.style.setProperty('--spot-y', `${event.clientY - rect.top}px`) }
function openLibrary() { if (!assessment.value) return; router.push({ path: '/library', query: demoMode.value ? { demo: '1' } : { assessment: assessment.value.id } }) }
async function loadDemoFixture() { stopPolling(); loading.value = false; loadError.value = ''; running.value = false; assessment.value = demoAssessment; jobTitle.value = '后端开发工程师'; currentPath.value = demoPath; resources.value = demoResources; traceSourceCount.value = 12; await nextTick(); renderRadar() }
async function loadAssessment() {
  if (demoMode.value) { await loadDemoFixture(); return }
  if (!assessmentId.value) { if (!publicPreview && !store.userInfo) await store.fetchUserInfo().catch(() => undefined); const latest = store.userInfo?.latest_assessment_id; if (latest) { await router.replace(`/diagnosis/${latest}`); return }; assessment.value = null; currentPath.value = null; resources.value = []; traceSourceCount.value = 0; return }
  loading.value = true; loadError.value = ''
  try { const item = await getAssessment(assessmentId.value); assessment.value = item; jobTitle.value = '目标岗位能力模型'; getJobList().then(jobs => { jobTitle.value = jobs.find(job => job.id === item.job_id)?.job_title || '目标岗位能力模型' }).catch(() => undefined); running.value = item.overall_mastery === null; if (running.value) startPolling(); else { stopPolling(); await Promise.all([loadPath(), loadResources(), loadTrace()]); nextTick(renderRadar) } } catch (error: any) { loadError.value = error?.response?.data?.detail || '无法读取诊断结果' } finally { loading.value = false }
}
async function startPolling() { stopPolling(); await pollProgress(); progressTimer = window.setInterval(pollProgress, 2500) }
async function pollProgress() { if (!assessmentId.value) return; try { progress.value = await getAssessmentProgress(assessmentId.value); if (progress.value.percent >= 100) { stopPolling(); await loadAssessment() } } catch { /* next verified polling cycle retries */ } }
function stopPolling() { if (progressTimer !== null) { window.clearInterval(progressTimer); progressTimer = null } }
async function loadPath() { if (!assessment.value) return; if (!store.userInfo) await store.fetchUserInfo().catch(() => undefined); if (!store.userInfo) return; pathLoading.value = true; try { const paths = await getLearningPaths(store.userInfo.id); currentPath.value = paths.find(path => path.assessment_id === assessment.value?.id) || null } finally { pathLoading.value = false } }
async function loadResources() { if (!assessment.value) return; try { resources.value = await getResourceList({ assessment_id: assessment.value.id }) } catch { resources.value = [] } }
async function loadTrace() { if (!assessment.value) return; try { const response = await getAssessmentAgents(assessment.value.id); traceSourceCount.value = response.trace.retrieval_sources?.length || 0 } catch { traceSourceCount.value = 0 } }
function renderRadar() { const dims = assessment.value?.ability_vector || []; if (!radarRef.value || !dims.length) return; chart?.dispose(); chart = echarts.init(radarRef.value); chart.setOption({ animationDuration: 780, tooltip: { trigger: 'item', formatter: (params: any) => `${params.name || '能力向量'}<br/>${params.value?.map((value: number, index: number) => `${dims[index]?.name} ${toPercent(value)}`).join('<br/>') || ''}` }, radar: { center: ['50%','53%'], radius: '65%', splitNumber: 4, axisName: { color: '#4e7460', fontSize: 10 }, splitArea: { areaStyle: { color: ['rgba(222,250,222,.08)','rgba(222,250,222,.19)'] } }, splitLine: { lineStyle: { color: 'rgba(12,150,76,.18)' } }, axisLine: { lineStyle: { color: 'rgba(12,150,76,.22)' } }, indicator: dims.map(item => ({ name: item.name, max: 1 })) }, series: [{ type: 'radar', symbol: 'circle', symbolSize: 5, lineStyle: { color: '#079455', width: 2 }, itemStyle: { color: '#079455' }, areaStyle: { color: new echarts.graphic.RadialGradient(.5,.5,.68,[{ offset: 0, color: 'rgba(39,200,115,.43)' }, { offset: 1, color: 'rgba(222,250,222,.09)' }]) }, data: [{ value: dims.map(item => item.value), name: '能力得分' }] }] }) }
async function submitCalibration() { if (!assessment.value || demoMode.value) return; const labels = requirementItems.value.map(item => ({ requirement_id: item.requirement_id, gold_score: goldScores.value[item.requirement_id], source_type: 'expert', trusted: true })).filter(item => typeof item.gold_score === 'number' && Number.isFinite(item.gold_score)); if (!labels.length) { ElMessage.warning('至少录入一项真实结果分数'); return }; calibrationSubmitting.value = true; try { await calibrateAssessment(assessment.value.id, { gold_labels: labels, apply_corrections: applyCorrections.value }); ElMessage.success('真实结果校准完成'); await loadAssessment(); showCalibration.value = false } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '校准失败') } finally { calibrationSubmitting.value = false } }
function handleResize() { chart?.resize() }
watch(() => [assessmentId.value, demoMode.value], () => { chart?.dispose(); chart = null; loadAssessment() }, { immediate: true }); window.addEventListener('resize', handleResize); onBeforeUnmount(() => { stopPolling(); chart?.dispose(); window.removeEventListener('resize', handleResize) })
</script>

<style scoped>
.diagnosis-page { background: radial-gradient(circle at 50% 36%, rgba(222,250,222,.62), transparent 41%), radial-gradient(circle at 83% 13%, rgba(134,231,177,.1), transparent 27%), linear-gradient(180deg,#fdfffe 0%,#f5fbf7 100%); }
.diagnosis-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 25px; }
.diagnosis-heading .page-title { display: flex; align-items: center; gap: 9px; }
.diagnosis-heading .page-title svg { width: 26px; color: var(--green-accent); }
.heading-actions { display: flex; gap: 10px; }
.top-action { height: 40px; padding: 0 13px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.66); color: var(--ink-soft); font-size: 12px; cursor: pointer; }
.top-action svg { width: 15px; }
.top-action.primary { border-color: rgba(14,155,79,.2); color: var(--green-deep); background: rgba(237,255,244,.67); }
.top-action:disabled { opacity: .5; cursor: not-allowed; }
.diagnosis-loading { min-height: 430px; position: relative; overflow: hidden; display: grid; place-items: center; border-radius: var(--radius-xl); text-align: center; }
.diagnosis-loading img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; mix-blend-mode: multiply; opacity: .72; }
.loading-copy { z-index: 2; padding: 25px; }
.loading-copy h2 { margin: 17px 0 8px; font-size: 21px; }
.loading-copy p { margin: 0; color: var(--ink-soft); font-size: 12px; }
.loading-copy .glass-pill svg { width: 14px; animation: spin 1.2s linear infinite; }
.loading-track { width: 340px; max-width: 80vw; height: 7px; margin: 21px auto 0; border-radius: 99px; overflow: hidden; background: rgba(19,133,72,.11); }
.loading-track i { display: block; height: 100%; border-radius: inherit; background: var(--gradient-progress); transition: width .4s; }
@keyframes spin { to { transform: rotate(360deg); } }
.diagnosis-error { padding: 28px; display: flex; align-items: center; gap: 15px; border-radius: var(--radius-lg); }
.diagnosis-error > svg { width: 28px; color: #c88821; }
.diagnosis-error h2 { margin: 0 0 5px; font-size: 17px; }
.diagnosis-error p { margin: 0; color: var(--ink-soft); font-size: 12px; }
.diagnosis-error button { margin-left: auto; border: 0; border-radius: 11px; padding: 10px 13px; background: var(--gradient-primary); color: #fff; cursor: pointer; }

.empty-diagnostic { min-height: 560px; padding: 24px; overflow: hidden; border-radius: var(--radius-xl); }
.empty-visual-grid { min-height: 430px; display: grid; grid-template-columns: .72fr 1.65fr .8fr; align-items: center; gap: 18px; }
.empty-match-preview, .empty-dimension-preview { min-height: 255px; padding: 22px; border-radius: 21px; border: 1px solid rgba(255,255,255,.84); background: rgba(255,255,255,.48); box-shadow: inset 0 1px 1px #fff; }
.empty-label { color: var(--ink-soft); font-size: 11px; font-weight: 700; }
.empty-match-preview strong { display: block; margin-top: 25px; color: var(--ink-faint); font-size: 54px; line-height: 1; }
.empty-match-preview small { color: var(--ink-faint); font-size: 10px; }
.empty-glass-orb { width: 78px; height: 78px; margin: 25px auto 0; display: grid; place-items: center; border-radius: 50%; color: var(--green-deep); background: radial-gradient(circle at 35% 30%, #fff, rgba(222,250,222,.74) 45%, rgba(134,231,177,.34)); box-shadow: inset 0 1px 2px #fff, 0 13px 30px rgba(27,139,76,.1); opacity: .72; }
.empty-glass-orb svg { width: 27px; }
.empty-core-stage { min-height: 390px; position: relative; display: grid; place-items: center; overflow: hidden; }
.empty-core-stage > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; mix-blend-mode: multiply; opacity: .76; mask-image: radial-gradient(ellipse, #000 56%, transparent 91%); }
.empty-core-copy { z-index: 2; width: min(470px, 84%); padding: 25px; text-align: center; border: 1px solid rgba(255,255,255,.73); border-radius: 22px; background: rgba(255,255,255,.48); backdrop-filter: blur(13px); box-shadow: 0 20px 50px rgba(25,109,62,.08), inset 0 1px 1px #fff; }
.empty-core-copy h2 { margin: 15px 0 8px; font-size: 21px; line-height: 1.3; }
.empty-core-copy p { margin: 0; color: var(--ink-soft); font-size: 11px; line-height: 1.65; }
.empty-core-copy button { min-height: 42px; margin-top: 18px; padding: 0 15px; display: inline-flex; align-items: center; gap: 8px; border-radius: 13px; font-size: 12px; font-weight: 700; cursor: pointer; }
.empty-core-copy button svg { width: 15px; }
.empty-dimension-preview > div { display: grid; grid-template-columns: 66px 1fr auto; align-items: center; gap: 7px; margin-top: 17px; color: var(--ink-soft); font-size: 10px; }
.empty-dimension-preview i { height: 5px; border-radius: 99px; background: linear-gradient(90deg, rgba(189,244,207,.64), rgba(224,238,229,.5)); }
.empty-dimension-preview em { color: var(--ink-faint); font-size: 8px; font-style: normal; }
.empty-process { display: grid; grid-template-columns: repeat(4,1fr); border-top: 1px solid var(--line); padding-top: 20px; }
.empty-process > div { display: grid; grid-template-columns: auto 1fr; gap: 3px 9px; padding: 0 18px; border-right: 1px solid var(--line); }
.empty-process > div:last-child { border-right: 0; }
.empty-process > div > span { grid-row: 1/3; width: 34px; height: 34px; display: grid; place-items: center; border-radius: 11px; color: var(--green-deep); background: rgba(222,250,222,.67); }
.empty-process svg { width: 17px; }
.empty-process b { font-size: 11px; }
.empty-process small { color: var(--ink-faint); font-size: 9px; }

.calibration-panel { border-radius: var(--radius-lg); padding: 21px; margin-bottom: 18px; display: grid; grid-template-columns: .8fr 1.6fr; gap: 21px; align-items: start; }
.calibration-panel h2 { font-size: 18px; margin: 12px 0 7px; }
.calibration-panel p { margin: 0; color: var(--ink-soft); font-size: 12px; line-height: 1.65; }
.calibration-fields { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 8px; }
.calibration-fields label { display: flex; flex-direction: column; gap: 5px; font-size: 11px; color: var(--ink-soft); }
.calibration-fields input { width: 100%; padding: 8px 9px; border: 1px solid var(--line); border-radius: 9px; background: rgba(255,255,255,.65); outline: none; color: var(--ink); }
.calibration-actions { grid-column: 2; display: flex; justify-content: space-between; align-items: center; }
.calibration-actions button { border: 0; border-radius: 10px; padding: 10px 13px; background: var(--gradient-primary); color: #fff; cursor: pointer; font-size: 12px; }
.calibration-actions button:disabled { opacity: .5; }
.correction-check { font-size: 11px; color: var(--ink-soft); }

.core-grid {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(520px, 1fr) minmax(220px, 280px);
  gap: clamp(16px, 1.25vw, 22px);
  align-items: center;
  width: 100%;
}
.core-grid > * { min-width: 0; max-width: 100%; }
.match-card, .dimension-card {
  min-height: 366px;
  padding: clamp(20px, 1.45vw, 25px);
  overflow: hidden;
  isolation: isolate;
  border: 1px solid rgba(255,255,255,.76);
  border-radius: var(--radius-xl);
  background: linear-gradient(145deg, rgba(255,255,255,.62), rgba(245,255,249,.38) 54%, rgba(189,244,207,.15)), rgba(250,255,252,.42);
  box-shadow: 0 27px 66px rgba(21,88,54,.09), inset 0 1px 1px rgba(255,255,255,.97), inset 0 -1px 1px rgba(36,164,91,.035);
  backdrop-filter: blur(31px) saturate(154%);
}
.card-heading { display: flex; align-items: center; justify-content: space-between; }
.card-heading > svg { width: 21px; color: var(--green-deep); }
.card-eyebrow { color: var(--ink); font-size: 14px; font-weight: 800; }
.match-card p { margin: 38px 0 0; color: var(--ink-soft); font-size: 12px; line-height: 1.55; }
.match-card > strong { display: block; margin-top: 10px; font-size: 59px; line-height: 1; }
.match-card > strong small { font-size: 22px; }
.match-badge { display: inline-flex; align-items: center; gap: 6px; width: max-content; margin-top: 15px; padding: 7px 10px; border-radius: 99px; background: rgba(236,255,243,.78); color: var(--green-deep); font-size: 11px; font-weight: 700; }
.match-badge i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.match-badge.needs { color: #a85c21; background: #fff3df; }
.match-insight { display: flex; align-items: center; justify-content: space-between; margin-top: 31px; padding: 13px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); color: var(--ink-soft); font-size: 10px; }
.match-insight b { color: var(--green-deep); font-size: 14px; }
.match-card footer { margin-top: 13px; color: var(--ink-faint); font-size: 10px; }
.diagnostic-core {
  --spot-x: 50%;
  --spot-y: 50%;
  width: 100%;
  min-width: 0;
  min-height: 426px;
  position: relative;
  display: grid;
  place-items: center;
  overflow: hidden;
  contain: layout paint;
  isolation: isolate;
  border: 1px solid rgba(255,255,255,.58);
  border-radius: 34px;
  background: linear-gradient(145deg, rgba(255,255,255,.22), rgba(222,250,222,.08));
  box-shadow: 0 30px 82px rgba(17,107,59,.095), inset 0 1px 1px rgba(255,255,255,.74);
  backdrop-filter: blur(12px) saturate(126%);
}
.diagnostic-core::before { content: ''; position: absolute; inset: 5% 4% 1%; z-index: 1; border-radius: 44%; pointer-events: none; background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(109,226,156,.13) 68%, rgba(255,255,255,.21)); filter: blur(25px); opacity: .76; }
.diagnostic-core::after { content: ''; position: absolute; inset: 0; z-index: 2; pointer-events: none; background: radial-gradient(min(240px, 30vw) circle at var(--spot-x) var(--spot-y), rgba(255,255,255,.35), transparent 68%); }
.diagnostic-platform { position: absolute; inset: 0; z-index: 1; width: 100%; height: 100%; max-width: 100%; object-fit: cover; object-position: center; mix-blend-mode: multiply; opacity: .78; mask-image: radial-gradient(ellipse, #000 62%, transparent 92%); filter: saturate(.96) contrast(1.02); }
.core-glass {
  z-index: 3;
  width: min(740px, calc(100% - 46px));
  max-width: 100%;
  min-width: 0;
  min-height: 338px;
  padding: 20px clamp(18px, 2vw, 26px) 17px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.8);
  border-radius: 26px;
  background: linear-gradient(142deg, rgba(255,255,255,.67), rgba(248,255,251,.36) 47%, rgba(184,246,207,.17)), rgba(252,255,253,.4);
  box-shadow: 0 34px 78px rgba(13,111,58,.14), 0 0 42px rgba(104,228,153,.11), inset 0 1px 1px rgba(255,255,255,.99), inset 0 -1px 1px rgba(45,176,101,.045);
  backdrop-filter: blur(35px) saturate(165%);
  -webkit-backdrop-filter: blur(35px) saturate(165%);
}
.core-topline { display: grid; grid-template-columns: .72fr 1.2fr; text-align: center; color: var(--ink); font-size: 13px; font-weight: 800; }
.core-body { display: grid; grid-template-columns: .72fr 1.2fr; align-items: center; height: 252px; }
.score-dial { width: clamp(136px, 10vw, 155px); height: clamp(136px, 10vw, 155px); margin: auto; display: grid; place-items: center; position: relative; border-radius: 50%; background: conic-gradient(from 210deg, #079455 0deg, #45d986 var(--score), rgba(218,248,227,.78) var(--score)); box-shadow: 0 0 0 9px rgba(255,255,255,.39), 0 0 0 10px rgba(12,159,78,.08), 0 13px 28px rgba(13,124,69,.13); }
.score-dial::before { content: ''; position: absolute; inset: 7px; border-radius: 50%; border-top: 2px solid rgba(255,255,255,.88); transform: rotate(-28deg); }
.score-dial > div { width: 125px; height: 125px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.88); box-shadow: inset 0 1px 2px #fff; }
.score-dial b { font-size: 46px; line-height: 1; }
.score-dial small { color: var(--ink-soft); font-size: 11px; }
.score-dial em { margin-top: 6px; color: var(--green-deep); font-size: 9px; font-style: normal; font-weight: 700; }
.radar-chart { width: 100%; max-width: 360px; height: 225px; margin: 0 auto; }
.core-meta { display: flex; justify-content: center; align-items: center; gap: 8px; color: var(--ink-faint); font-size: 10px; }
.demo-badge { padding: 3px 6px; border-radius: 99px; color: var(--green-deep); background: rgba(222,250,222,.72); }
.dimension-card { padding: 25px; }
.dimension-head { display: flex; justify-content: space-between; align-items: center; }
.dimension-count { color: var(--ink-faint); font-size: 10px; }
.dimension-list { margin-top: 25px; display: flex; flex-direction: column; gap: 16px; }
.dimension-row { display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 7px; align-items: center; }
.dimension-row > div:first-child { display: flex; align-items: center; gap: 8px; min-width: 0; }
.dimension-row b { font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dimension-icon { width: 29px; height: 29px; display: grid; place-items: center; border-radius: 9px; background: rgba(222,250,222,.68); color: var(--green-deep); }
.dimension-icon svg { width: 15px; }
.dimension-row strong { font-size: 11px; color: var(--ink); }
.dimension-row strong small { color: var(--ink-faint); font-weight: 500; }
.dimension-bar { grid-column: 1/3; height: 6px; overflow: hidden; border-radius: 99px; background: rgba(44,126,80,.1); }
.dimension-bar i { display: block; height: 100%; border-radius: inherit; background: var(--gradient-progress); transition: width .9s ease; }

.analysis-grid { display: grid; grid-template-columns: 1.2fr .7fr 1.12fr; gap: 14px; margin-top: 20px; }
.evidence-insights, .agent-summary, .roadmap-card { min-height: 238px; border-radius: var(--radius-lg); padding: 20px; }
.evidence-insights { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
.evidence-insights > section { padding-right: 20px; }
.evidence-insights > section + section { padding: 0 0 0 20px; border-left: 1px solid var(--line); }
.evidence-insights h2, .agent-summary h2, .roadmap-card h2 { margin: 0; display: flex; align-items: center; gap: 7px; color: var(--ink); font-size: 15px; }
.evidence-insights h2 svg, .roadmap-card h2 svg { width: 17px; color: var(--green-deep); }
.gaps h2 svg { color: #d28c1e; }
.evidence-insights ul { padding: 0; margin: 18px 0 0; list-style: none; display: flex; flex-direction: column; gap: 12px; }
.strengths li { display: flex; gap: 8px; align-items: flex-start; }
.strengths li > span { width: 18px; height: 18px; flex: 0 0 auto; display: grid; place-items: center; border-radius: 50%; color: var(--green-deep); background: rgba(222,250,222,.74); }
.strengths li svg { width: 10px; }
.strengths li b, .strengths li small { display: block; }
.strengths li b { font-size: 11px; }
.strengths li small { margin-top: 3px; color: var(--ink-soft); font-size: 9px; line-height: 1.4; }
.gaps li { display: grid; grid-template-columns: 22px 1fr; gap: 6px; align-items: start; }
.gaps li b { color: #c7831c; font-size: 9px; }
.gaps li span { color: var(--ink-soft); font-size: 10px; line-height: 1.45; }
.evidence-insights p { margin-top: 20px; color: var(--ink-soft); font-size: 11px; line-height: 1.6; }
.agent-summary { position: relative; }
.agent-face { display: inline-grid; place-items: center; width: 35px; height: 35px; margin-right: 7px; border-radius: 11px; background: var(--gradient-primary); color: #fff; vertical-align: middle; box-shadow: 0 7px 15px rgba(15,164,91,.19); }
.agent-face svg { width: 18px; }
.agent-summary h2 { display: inline-flex; }
.agent-summary p { margin: 13px 0 10px; color: var(--ink-soft); font-size: 11px; line-height: 1.68; }
.summary-evidence { display: flex; align-items: center; gap: 7px; padding: 8px 0; border-top: 1px solid var(--line); color: var(--ink-faint); font-size: 9px; }
.summary-evidence svg { width: 13px; color: var(--green-deep); }
.review-metric { padding: 8px 0; border-top: 1px solid var(--line); display: flex; justify-content: space-between; color: var(--ink-soft); font-size: 9px; }
.review-metric b { font-size: 10px; }
.review-metric .accurate { color: var(--green-deep); }
.review-metric .pending { color: #9a781d; }
.agent-summary button { width: 100%; min-height: 34px; margin-top: 8px; display: flex; align-items: center; justify-content: center; gap: 6px; border: 0; border-radius: 10px; background: rgba(222,250,222,.72); color: var(--green-deep); cursor: pointer; font-size: 10px; font-weight: 700; }
.agent-summary button svg { width: 13px; }
.roadmap-heading { display: flex; align-items: center; justify-content: space-between; }
.roadmap-heading > span { padding: 4px 7px; border-radius: 99px; background: rgba(222,250,222,.7); color: var(--green-deep); font-size: 8px; }
.roadmap { min-height: 152px; position: relative; display: grid; grid-template-columns: repeat(3,1fr); gap: 9px; align-items: start; margin-top: 24px; }
.roadmap-line { position: absolute; left: 14%; right: 14%; top: 17px; height: 1px; border-top: 1px dashed rgba(34,181,107,.32); }
.roadmap-step { z-index: 2; text-align: center; }
.roadmap-step > span { width: 34px; height: 34px; margin: auto; display: grid; place-items: center; border-radius: 50%; background: rgba(248,255,250,.9); border: 1px solid rgba(34,181,107,.2); color: var(--green-deep); box-shadow: 0 6px 14px rgba(23,107,62,.08); font-size: 9px; font-weight: 800; }
.roadmap-step.current > span { color: #fff; background: var(--gradient-primary); box-shadow: 0 0 0 5px rgba(222,250,222,.66), 0 9px 19px rgba(15,164,91,.2); }
.roadmap-step > div { min-height: 84px; margin-top: 12px; padding: 11px 7px; border-radius: 12px; background: rgba(255,255,255,.45); border: 1px solid rgba(255,255,255,.83); }
.roadmap-step b, .roadmap-step small { display: block; }
.roadmap-step b { font-size: 10px; }
.roadmap-step small { margin-top: 5px; color: var(--ink-soft); font-size: 8px; line-height: 1.4; }
.path-empty { margin-top: 28px; color: var(--ink-faint); font-size: 11px; }
.quality-strip { margin-top: 16px; padding: 14px 19px; border-radius: 15px; display: grid; grid-template-columns: 1fr 1fr 1fr auto; align-items: center; gap: 15px; }
.quality-strip > div { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; padding-right: 15px; border-right: 1px solid var(--line); }
.quality-strip > div svg { grid-row: 1/3; width: 17px; color: var(--green-deep); }
.quality-strip span, .quality-strip b { display: block; }
.quality-strip span { color: var(--ink-faint); font-size: 9px; }
.quality-strip b { color: var(--green-deep); font-size: 11px; }
.quality-strip button { display: flex; align-items: center; gap: 6px; border: 0; background: transparent; color: var(--green-deep); font-weight: 700; font-size: 11px; cursor: pointer; }
.quality-strip button svg { width: 13px; }
@media (max-width: 1260px) { .core-grid { grid-template-columns: minmax(220px, .72fr) minmax(520px, 1.3fr); } .dimension-card { grid-column: 1/3; min-height: auto; } .dimension-list { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; } .analysis-grid { grid-template-columns: 1fr 1fr; } .roadmap-card { grid-column: 1/3; } .empty-visual-grid { grid-template-columns: .7fr 1.4fr; } .empty-dimension-preview { grid-column: 1/3; min-height: auto; display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; } .empty-dimension-preview > .empty-label { grid-column: 1/6; } .empty-dimension-preview > div { grid-template-columns: 1fr; } }
@media (max-width: 720px) { .diagnosis-heading { display: block; } .heading-actions { margin-top: 15px; } .diagnosis-error { display: block; } .diagnosis-error button { margin: 14px 0 0; } .empty-diagnostic { padding: 14px; } .empty-visual-grid { grid-template-columns: 1fr; } .empty-match-preview { display: none; } .empty-core-stage { min-height: 400px; } .empty-dimension-preview { grid-column: auto; display: block; } .empty-process { grid-template-columns: 1fr 1fr; gap: 15px 0; } .empty-process > div:nth-child(2) { border-right: 0; } .core-grid { grid-template-columns: 1fr; } .diagnostic-core { order: -1; min-height: 510px; } .dimension-card { grid-column: auto; } .core-glass { width: 94%; } .core-body { grid-template-columns: 1fr; height: auto; } .core-topline { display: none; } .score-dial { margin: 13px auto 0; } .radar-chart { height: 220px; } .core-meta { flex-wrap: wrap; } .dimension-list { grid-template-columns: 1fr; } .analysis-grid { grid-template-columns: 1fr; } .roadmap-card { grid-column: auto; } .evidence-insights { grid-template-columns: 1fr; } .evidence-insights > section { padding: 0; } .evidence-insights > section + section { margin-top: 20px; padding: 20px 0 0; border-left: 0; border-top: 1px solid var(--line); } .quality-strip { grid-template-columns: 1fr 1fr; } .quality-strip > div { border: 0; } .calibration-panel { grid-template-columns: 1fr; } .calibration-fields { grid-template-columns: 1fr 1fr; } .calibration-actions { grid-column: auto; display: block; } .calibration-actions button { margin-top: 12px; } .match-card { min-height: 290px; } }
</style>
