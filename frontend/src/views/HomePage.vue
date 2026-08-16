<template>
  <div class="home-page">
    <section class="hero content-width">
      <div class="hero-copy motion-enter">
        <span class="glass-pill hero-pill"><span class="live-dot"></span>AI Agent 赋能 · 精准评估 · 智能成长</span>
        <h1>
          <span class="headline-line">用 AI 看见能力差距，</span>
          <span class="headline-line">生成属于你的<span class="gradient-title">成长路径</span></span>
        </h1>
        <p>职学导航通过多 Agent 协同评估知识、技能与项目经历，对照岗位能力模型形成证据链，生成可追溯的诊断结果与下一步行动路径。</p>
        <div class="hero-actions">
          <button class="hero-primary primary-gradient-button" type="button" @click="startAssessment()">开始测评 <ArrowRight /></button>
          <button class="hero-secondary" type="button" @click="scrollToRoles"><VideoPlay /> 了解职学导航</button>
        </div>
      </div>

      <div class="spatial-hub motion-enter motion-delay-2" aria-label="AI 多智能体能力分析中枢示意" @pointermove="moveSpotlight">
        <img class="hub-visual" src="/assets/spatial-agent-core.png" alt="绿色玻璃质感的 AI Agent 空间分析核心" />
        <article class="float-card score-card depth-front">
          <div class="card-kicker"><DataAnalysis /> 能力评分</div>
          <div class="score-row"><strong>86</strong><span>/100</span></div>
          <small>超过 82% 同岗位学习者</small>
        </article>
        <article class="float-card radar-card depth-back">
          <div class="card-kicker"><Aim /> 能力雷达图</div>
          <div ref="heroRadarRef" class="hero-radar" aria-label="工程能力、项目经验、学习潜力、基础能力和软实力示例雷达图"></div>
        </article>
        <article class="float-card agent-card depth-middle">
          <span class="agent-icon"><Cpu /></span>
          <div><b>AI Agent</b><p>工程实践表现较好，下一阶段建议加强系统设计能力。</p></div>
        </article>
        <article class="float-card path-card depth-front">
          <div class="card-kicker"><Guide /> 个性化学习路径</div>
          <div class="path-line"><span>基础补强</span><i><b style="width:60%"></b></i><em>60%</em></div>
          <div class="path-line"><span>项目进阶</span><i><b style="width:25%"></b></i><em>25%</em></div>
          <div class="path-line muted"><span>综合实战</span><i></i><em>待开始</em></div>
        </article>
      </div>
    </section>

    <section class="workflow content-width motion-enter motion-delay-1" aria-label="产品使用流程">
      <template v-for="(step, index) in workflow" :key="step.title">
        <div class="workflow-step">
          <span class="workflow-index">0{{ index + 1 }}</span>
          <span class="workflow-icon"><component :is="step.icon" /></span>
          <span><b>{{ step.title }}</b><small>{{ step.detail }}</small></span>
        </div>
        <span v-if="index < workflow.length - 1" class="workflow-arrow"><ArrowRight /></span>
      </template>
    </section>

    <section id="roles" class="role-section content-width">
      <div class="section-heading">
        <div><span class="eyebrow">目标岗位能力模型</span><h2>从一个岗位做深，到多个方向扩展</h2></div>
        <p>每个方向都由岗位要求、能力证据标准和领域知识库共同支撑，诊断与推荐结果保留可追溯依据。</p>
      </div>

      <div v-if="jobsLoading" class="role-grid"><div v-for="i in 4" :key="i" class="role-tile skeleton"></div></div>
      <div v-else-if="jobsError" class="role-state glass-surface"><b>岗位能力模型暂时无法加载</b><button type="button" @click="loadJobs">重新加载</button></div>
      <div v-else class="role-grid">
        <button v-for="(job, index) in jobs" :key="job.id" class="role-tile glass-surface" :class="`role-${index + 1}`" type="button" @click="startAssessment(job.id)">
          <span class="role-index">0{{ index + 1 }}</span>
          <span class="role-object"><component :is="roleMeta[index % roleMeta.length].icon" /></span>
          <div class="role-copy"><h3>{{ job.job_title }}</h3><small>{{ roleMeta[index % roleMeta.length].english }}</small><p>{{ job.required_skills.slice(0, 3).join(' · ') }}</p></div>
          <span class="role-more">查看能力模型 <ArrowRight /></span>
        </button>
      </div>
    </section>

    <section class="proof-section content-width">
      <article v-for="item in proofPoints" :key="item.title" class="proof-point">
        <span class="proof-icon"><component :is="item.icon" /></span>
        <div><h3>{{ item.title }}</h3><p>{{ item.detail }}</p></div>
      </article>
    </section>

    <footer class="app-footer"><span>职学导航 · AI 驱动的学习与成长评估平台</span><span>证据驱动 · 审核纠偏 · 路径生成</span></footer>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { Component } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Aim, ArrowRight, Box, Briefcase, CircleCheck, Cloudy, Connection, Cpu,
  DataAnalysis, DocumentChecked, Files, Guide, MagicStick, Monitor, UserFilled, VideoPlay,
} from '@element-plus/icons-vue'
import { getJobList, type JobInfo } from '@/api/jobs'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()
const jobs = ref<JobInfo[]>([])
const jobsLoading = ref(true)
const jobsError = ref(false)
const heroRadarRef = ref<HTMLDivElement | null>(null)
let heroRadar: echarts.ECharts | null = null

const workflow: Array<{ icon: Component; title: string; detail: string }> = [
  { icon: Briefcase, title: '岗位选择', detail: '选择目标职业方向' },
  { icon: DocumentChecked, title: '资料审查', detail: 'AI 审查学习与项目资料' },
  { icon: DataAnalysis, title: '能力诊断', detail: '多维度能力精准评估' },
  { icon: MagicStick, title: '个性化学习建议', detail: '生成专属成长路径' },
]
const roleMeta: Array<{ icon: Component; english: string }> = [
  { icon: Monitor, english: 'Frontend Engineering' },
  { icon: Box, english: 'Backend Engineering' },
  { icon: Cloudy, english: 'Operations Engineering' },
  { icon: UserFilled, english: 'Product Management' },
]
const proofPoints: Array<{ icon: Component; title: string; detail: string }> = [
  { icon: Connection, title: '多 Agent 协同', detail: '多角色 Agent 分工分析，过程可见、决策可解释。' },
  { icon: Files, title: '证据驱动', detail: '结论绑定学习资料与项目证据，可追溯、可复核。' },
  { icon: CircleCheck, title: '审核纠偏', detail: '生成内容经过来源校验与交叉审核，降低幻觉风险。' },
  { icon: Guide, title: '路径生成', detail: '结合岗位要求与个人差距，生成可执行学习路径。' },
]

async function loadJobs() {
  jobsLoading.value = true
  jobsError.value = false
  try { jobs.value = await getJobList() } catch { jobsError.value = true } finally { jobsLoading.value = false }
}
function startAssessment(jobId?: string) {
  if (!store.isLoggedIn) {
    router.push({ path: '/login', query: { next: jobId ? `/input?job=${jobId}` : '/input' } })
    return
  }
  router.push({ path: '/input', query: jobId ? { job: jobId } : undefined })
}
function scrollToRoles() { document.querySelector('#roles')?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
function moveSpotlight(event: PointerEvent) {
  const element = event.currentTarget as HTMLElement
  const rect = element.getBoundingClientRect()
  element.style.setProperty('--spot-x', `${event.clientX - rect.left}px`)
  element.style.setProperty('--spot-y', `${event.clientY - rect.top}px`)
}
function renderHeroRadar() {
  if (!heroRadarRef.value) return
  heroRadar?.dispose()
  heroRadar = echarts.init(heroRadarRef.value)
  heroRadar.setOption({
    animationDuration: 700,
    radar: {
      center: ['50%', '53%'], radius: '62%', splitNumber: 4,
      indicator: ['工程能力', '项目经验', '学习潜力', '基础能力', '软实力'].map(name => ({ name, max: 100 })),
      axisName: { color: '#617168', fontSize: 8 },
      splitArea: { areaStyle: { color: ['rgba(222,250,222,.06)', 'rgba(222,250,222,.2)'] } },
      splitLine: { lineStyle: { color: 'rgba(7,148,85,.17)' } },
      axisLine: { lineStyle: { color: 'rgba(7,148,85,.17)' } },
    },
    series: [{ type: 'radar', symbol: 'circle', symbolSize: 3, lineStyle: { color: '#079455', width: 1.5 }, itemStyle: { color: '#079455' }, areaStyle: { color: 'rgba(34,181,107,.31)' }, data: [{ value: [86, 76, 90, 82, 78] }] }],
  })
}
function handleResize() { heroRadar?.resize() }
onMounted(async () => { await loadJobs(); await nextTick(); renderHeroRadar(); window.addEventListener('resize', handleResize) })
onBeforeUnmount(() => { heroRadar?.dispose(); window.removeEventListener('resize', handleResize) })
</script>

<style scoped>
.home-page {
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - 78px);
  padding: 24px 24px 30px;
  isolation: isolate;
  background:
    radial-gradient(circle at 74% 34%, rgba(222,250,222,.78), rgba(222,250,222,.28) 28%, transparent 61%),
    radial-gradient(circle at 91% 51%, rgba(77,220,135,.11), transparent 38%),
    linear-gradient(180deg, #fdfffe 0%, #f4fbf7 100%);
}
.hero {
  min-height: 548px;
  display: grid;
  grid-template-columns: minmax(540px, .42fr) minmax(650px, .58fr);
  align-items: center;
  gap: 18px;
  position: relative;
}
.hero-copy { position: relative; z-index: 4; padding-left: clamp(0px, 1.8vw, 28px); }
.hero-pill { margin-bottom: 22px; }
.live-dot { height: 7px; width: 7px; border-radius: 50%; background: var(--gradient-primary); box-shadow: 0 0 10px rgba(34,181,107,.42); animation: breathe 2.5s ease-in-out infinite; }
.hero h1 { margin: 0; color: var(--ink); font-size: clamp(46px, 3.25vw, 62px); line-height: 1.18; font-weight: 850; letter-spacing: 0; }
.headline-line { display: block; white-space: nowrap; }
.gradient-title { color: transparent; background: var(--gradient-number); background-clip: text; -webkit-background-clip: text; }
.hero-copy > p { max-width: 575px; margin: 23px 0 28px; color: var(--ink-soft); line-height: 1.85; font-size: 15px; }
.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.hero-primary, .hero-secondary { min-height: 51px; padding: 0 23px; border-radius: 15px; display: inline-flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 750; cursor: pointer; }
.hero-primary svg, .hero-secondary svg { width: 17px; }
.hero-secondary { color: var(--ink); background: rgba(255,255,255,.64); border: 1px solid rgba(20,86,53,.11); box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 8px 20px rgba(33,82,58,.055); transition: transform .2s ease, box-shadow .2s ease; }
.hero-secondary:hover { transform: translateY(-2px); box-shadow: inset 0 1px 0 #fff, 0 14px 26px rgba(33,82,58,.1); }
.hero-secondary svg { color: var(--green-deep); }

.spatial-hub {
  --spot-x: 50%;
  --spot-y: 50%;
  width: calc(100% - clamp(24px, 2.4vw, 42px));
  height: 548px;
  position: relative;
  justify-self: start;
  z-index: 2;
  isolation: isolate;
  overflow: hidden;
  contain: layout paint;
  border-radius: 44px;
  perspective: 1120px;
  transform-style: preserve-3d;
}
.spatial-hub::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  background: radial-gradient(280px circle at var(--spot-x) var(--spot-y), rgba(255,255,255,.34), transparent 68%);
  opacity: .7;
}
.hub-visual {
  position: absolute;
  inset: -2% -4% -2% -4%;
  z-index: 0;
  width: 108%;
  height: 104%;
  object-fit: cover;
  object-position: center;
  mix-blend-mode: multiply;
  filter: saturate(.94) contrast(.98);
  mask-image: radial-gradient(ellipse at center, #000 55%, transparent 86%);
  transform: perspective(1100px) rotateX(2.2deg) rotateZ(-.55deg) scale(1.015);
  transform-origin: 53% 56%;
}
.float-card {
  --tilt-x: 0deg;
  --tilt-y: 0deg;
  --tilt-z: 0deg;
  --depth-z: 0px;
  --depth-scale: 1;
  position: absolute;
  z-index: 5;
  box-sizing: border-box;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.78);
  border-radius: 20px;
  background:
    linear-gradient(142deg, rgba(255,255,255,.7), rgba(247,255,250,.34) 52%, rgba(189,244,207,.18)),
    rgba(250,255,252,.42);
  box-shadow: 0 25px 54px rgba(23,96,57,.13), 0 8px 18px rgba(21,79,48,.05), inset 0 1px 1px rgba(255,255,255,.98), inset 0 -1px 1px rgba(48,169,98,.04);
  backdrop-filter: blur(27px) saturate(158%);
  -webkit-backdrop-filter: blur(27px) saturate(158%);
  color: var(--ink);
  transform: rotateX(var(--tilt-x)) rotateY(var(--tilt-y)) rotateZ(var(--tilt-z)) translate3d(0,0,var(--depth-z)) scale(var(--depth-scale));
  transform-style: preserve-3d;
  will-change: transform;
}
.float-card::before { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; background: linear-gradient(118deg, rgba(255,255,255,.62), transparent 27%, rgba(132,235,174,.1) 63%, rgba(255,255,255,.26)); opacity: .8; }
.float-card::after { content: ''; position: absolute; inset: 1px; border-radius: inherit; pointer-events: none; background: linear-gradient(180deg, rgba(255,255,255,.23), transparent 38%), radial-gradient(circle at 74% 112%, rgba(111,231,160,.15), transparent 46%); }
.float-card > * { position: relative; z-index: 1; }
.depth-front { --depth-scale: 1; opacity: .98; }
.depth-middle { --depth-scale: .95; opacity: .91; }
.depth-back { --depth-scale: .91; opacity: .84; filter: saturate(.93); }
.card-kicker { display: flex; align-items: center; gap: 7px; color: var(--ink-soft); font-size: 11px; font-weight: 700; }
.card-kicker svg { width: 15px; height: 15px; color: var(--green-deep); }
.score-card { --tilt-x: 2deg; --tilt-y: 7deg; --tilt-z: -1.35deg; --depth-z: 22px; left: 7%; top: 8%; width: 196px; aspect-ratio: 1.48 / 1; padding: 16px 17px; animation: spatial-float 5.7s .2s ease-in-out infinite; }
.score-row { display: flex; align-items: end; gap: 4px; margin-top: 8px; }
.score-row strong { font-size: 38px; line-height: 1; color: transparent; background: var(--gradient-number); background-clip: text; -webkit-background-clip: text; }
.score-row span { margin-bottom: 4px; color: var(--ink-faint); font-size: 12px; }
.score-card small { display: block; margin-top: 7px; color: var(--green-deep); font-size: 10px; }
.radar-card { --tilt-x: 2.5deg; --tilt-y: -7deg; --tilt-z: 1.15deg; --depth-z: -12px; right: 6%; top: 6%; width: 210px; aspect-ratio: 1.08 / 1; padding: 13px 14px; transform-origin: right top; animation: spatial-float 6.2s ease-in-out infinite; }
.hero-radar { height: 148px; width: 100%; }
.agent-card { --tilt-x: -2deg; --tilt-y: 6deg; --tilt-z: .75deg; --depth-z: 4px; left: 5%; bottom: 14%; width: 244px; aspect-ratio: 1.58 / 1; padding: 15px; display: flex; gap: 12px; align-items: flex-start; transform-origin: left center; animation: spatial-float 5.2s .5s ease-in-out infinite; }
.agent-icon { width: 34px; height: 34px; flex: 0 0 auto; display: grid; place-items: center; border-radius: 11px; color: #fff; background: var(--gradient-primary); box-shadow: 0 7px 16px rgba(15,164,91,.2); }
.agent-icon svg { width: 18px; }
.agent-card b { font-size: 12px; }
.agent-card p { margin: 6px 0 0; color: var(--ink-soft); font-size: 11px; line-height: 1.55; }
.path-card { --tilt-x: -2.2deg; --tilt-y: -6deg; --tilt-z: -.85deg; --depth-z: 19px; right: 6%; bottom: 15%; width: 244px; aspect-ratio: 1.55 / 1; padding: 15px 16px; animation: spatial-float 6s .7s ease-in-out infinite; }
.path-line { margin-top: 10px; display: grid; grid-template-columns: 58px 1fr auto; align-items: center; gap: 7px; font-size: 9px; color: var(--ink-soft); }
.path-line i { height: 5px; overflow: hidden; border-radius: 99px; background: rgba(44,126,80,.1); }
.path-line i b { display: block; height: 100%; border-radius: inherit; background: var(--gradient-progress); }
.path-line em { min-width: 31px; color: var(--green-deep); font-style: normal; text-align: right; }
.path-line.muted { opacity: .55; }
@keyframes spatial-float {
  0%,100% { transform: rotateX(var(--tilt-x)) rotateY(var(--tilt-y)) rotateZ(var(--tilt-z)) translate3d(0,0,var(--depth-z)) scale(var(--depth-scale)); }
  50% { transform: rotateX(var(--tilt-x)) rotateY(var(--tilt-y)) rotateZ(var(--tilt-z)) translate3d(0,-7px,var(--depth-z)) scale(var(--depth-scale)); }
}

.workflow {
  min-height: 86px;
  padding: 14px 25px;
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(255,255,255,.86);
  border-radius: 22px;
  background: rgba(255,255,255,.54);
  box-shadow: var(--surface-shadow), inset 0 1px 1px #fff;
  backdrop-filter: blur(22px) saturate(138%);
}
.workflow-step { min-width: 0; display: grid; grid-template-columns: auto auto 1fr; align-items: center; gap: 11px; }
.workflow-index { color: var(--green-deep); font-size: 16px; }
.workflow-icon { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; color: var(--green-deep); background: rgba(222,250,222,.7); box-shadow: inset 0 1px 0 #fff; }
.workflow-icon svg { width: 19px; }
.workflow-step b, .workflow-step small { display: block; }
.workflow-step b { font-size: 13px; }
.workflow-step small { margin-top: 3px; color: var(--ink-soft); font-size: 10px; white-space: nowrap; }
.workflow-arrow { width: 24px; color: rgba(7,148,85,.5); }
.workflow-arrow svg { width: 19px; }

.role-section { padding-top: 62px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 30px; margin-bottom: 22px; }
.section-heading h2 { margin: 8px 0 0; font-size: 29px; line-height: 1.25; }
.section-heading p { max-width: 460px; margin: 0; color: var(--ink-soft); font-size: 13px; line-height: 1.7; }
.role-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.role-tile {
  min-height: 226px;
  padding: 19px;
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
  transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
}
.role-tile:hover { transform: translateY(-5px); border-color: rgba(189,244,207,.82); box-shadow: var(--surface-shadow-raised), inset 0 1px 1px #fff; }
.role-index { color: var(--ink-faint); font-size: 11px; }
.role-object { position: absolute; right: 24px; top: 36px; width: 68px; height: 68px; display: grid; place-items: center; border-radius: 22px; color: #fff; background: var(--gradient-primary); box-shadow: inset 0 1px 1px rgba(255,255,255,.5), 0 16px 30px rgba(15,164,91,.2); transition: transform .28s ease; }
.role-object svg { width: 33px; height: 33px; }
.role-tile:hover .role-object { transform: translateY(-4px) rotate(-2deg); }
.role-2 .role-object { top: 53px; border-radius: 18px; background: linear-gradient(140deg, #a2efbd, #119f5a); }
.role-3 .role-object { top: 29px; right: 30px; border-radius: 50%; background: linear-gradient(140deg, #85d8a8, #087e48); }
.role-4 .role-object { top: 48px; transform: rotate(5deg); background: linear-gradient(140deg, #b7efc9, #22b56b 60%, #087e48); }
.role-4:hover .role-object { transform: translateY(-4px) rotate(2deg); }
.role-copy { margin-top: 62px; max-width: 76%; }
.role-copy h3 { margin: 0; font-size: 17px; }
.role-copy small { display: block; margin-top: 5px; color: var(--ink-faint); font-size: 10px; }
.role-copy p { margin: 10px 0 0; color: var(--ink-soft); font-size: 11px; line-height: 1.55; }
.role-more { position: absolute; left: 19px; bottom: 17px; display: inline-flex; align-items: center; gap: 7px; color: var(--green-deep); font-size: 11px; font-weight: 700; }
.role-more svg { width: 14px; }
.role-state { padding: 35px; border-radius: var(--radius-lg); display: flex; gap: 16px; align-items: center; justify-content: space-between; }
.role-state button { border: 0; border-radius: 10px; padding: 9px 13px; background: var(--gradient-primary); color: #fff; cursor: pointer; }
.skeleton { background: linear-gradient(100deg, #f2faf5 30%, #fcfffd 47%, #f2faf5 63%); background-size: 200% 100%; animation: loading 1.4s infinite; }
@keyframes loading { to { background-position: -200% 0; } }
.proof-section { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; margin-top: 22px; padding: 18px 8px; border-radius: 20px; background: rgba(255,255,255,.45); border: 1px solid rgba(255,255,255,.82); box-shadow: 0 15px 36px rgba(25,87,55,.06), inset 0 1px 1px #fff; }
.proof-point { min-height: 72px; padding: 7px 20px; display: flex; gap: 13px; align-items: flex-start; border-right: 1px solid var(--line); }
.proof-point:last-child { border-right: 0; }
.proof-icon { width: 35px; height: 35px; flex: 0 0 auto; display: grid; place-items: center; border-radius: 12px; color: var(--green-deep); background: rgba(222,250,222,.72); }
.proof-icon svg { width: 19px; }
.proof-point h3 { margin: 1px 0 5px; font-size: 13px; }
.proof-point p { margin: 0; color: var(--ink-soft); font-size: 10px; line-height: 1.55; }

@media (max-width: 1366px) {
  .home-page { padding-top: 17px; }
  .hero { min-height: 500px; grid-template-columns: minmax(485px, .42fr) minmax(560px, .58fr); }
  .spatial-hub { height: 500px; }
  .hero h1 { font-size: clamp(44px, 3.35vw, 52px); }
  .hero-copy > p { margin-block: 19px 23px; }
  .float-card { transform-origin: center; }
  .score-card { left: 5%; width: 184px; }
  .radar-card { right: 5%; width: 198px; }
  .agent-card { left: 4%; width: 226px; }
  .path-card { right: 5%; bottom: 16%; width: 226px; }
  .workflow { min-height: 78px; }
  .role-section { padding-top: 48px; }
}
@media (max-width: 1120px) {
  .hero { grid-template-columns: 1fr 1fr; gap: 8px; }
  .headline-line { white-space: normal; }
  .hero h1 { font-size: 44px; }
  .spatial-hub { width: calc(100% - 18px); }
  .radar-card { right: 3%; }
  .agent-card { left: 3%; }
  .path-card { right: 3%; }
  .role-grid, .proof-section { grid-template-columns: repeat(2, 1fr); }
  .proof-point:nth-child(2) { border-right: 0; }
  .proof-point:nth-child(-n+2) { border-bottom: 1px solid var(--line); }
}
@media (max-width: 760px) {
  .home-page { padding: 19px 14px 26px; }
  .hero { grid-template-columns: 1fr; min-height: 0; }
  .hero-copy { padding: 0 3px; }
  .hero h1 { font-size: 39px; }
  .headline-line { white-space: normal; }
  .spatial-hub { width: auto; height: 390px; justify-self: stretch; order: -1; margin: -20px -42px 0; contain: paint; }
  .float-card { animation: none; }
  .score-card { left: 8%; top: 7%; transform: scale(.75) rotateZ(-1deg); transform-origin: left top; }
  .radar-card { right: 5%; top: 5%; transform: scale(.67) rotateZ(1deg); transform-origin: right top; }
  .agent-card { left: 7%; bottom: 11%; width: 220px; transform: scale(.75) rotateZ(.6deg); transform-origin: left bottom; }
  .path-card { right: 3%; bottom: 8%; transform: scale(.7) rotateZ(-.6deg); transform-origin: right bottom; }
  .workflow { grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 25px; }
  .workflow-arrow { display: none; }
  .workflow-step small { white-space: normal; }
  .role-section { padding-top: 47px; }
  .section-heading { display: block; }
  .section-heading p { margin-top: 12px; }
  .role-grid, .proof-section { grid-template-columns: 1fr; }
  .proof-point { border-right: 0; border-bottom: 1px solid var(--line); }
  .proof-point:last-child { border-bottom: 0; }
  .role-tile { min-height: 205px; }
}
</style>
