<template>
  <div class="page-shell review-page">
    <div class="content-width">
      <header class="review-heading motion-enter">
        <div>
          <span class="eyebrow">AI REVIEW WORKSPACE</span>
          <h1 class="page-title"><span class="gradient-number">AI</span> 资料审查</h1>
          <p class="page-subtitle">多 Agent 协同核验资料真实性、完整度与岗位相关性，并为每项能力结论建立可追溯证据。</p>
        </div>
        <button class="heading-action" type="button" @click="loadJobs"><Refresh /> 刷新岗位</button>
      </header>

      <div v-if="jobError" class="error-state glass-surface">
        <b>岗位能力模型加载失败</b><span>请确认后端服务已启动后重试。</span><button type="button" @click="loadJobs">重新加载</button>
      </div>

      <div v-else class="workspace-grid motion-enter motion-delay-1">
        <section class="review-workspace glass-surface">
          <div class="workspace-top">
            <div class="workspace-status"><span class="pulse"></span><b>资料审查 Agent</b><span>实时工作区</span></div>
            <div class="job-picker"><label for="job-select">目标岗位</label><select id="job-select" v-model="selectedJobId" :disabled="jobLoading || submitting" @change="onJobChange"><option value="" disabled>请选择岗位</option><option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.job_title }}</option></select></div>
          </div>

          <div class="conversation" aria-live="polite">
            <div class="message agent-message">
              <span class="message-avatar"><Cpu /></span>
              <div class="bubble"><p>你好，我是资料审查 Agent。上传资料或描述你的经历，我会协调多个专业 Agent 建立能力证据图谱。</p><time>已就绪</time></div>
            </div>
            <div v-if="userInput.trim()" class="message user-message"><div class="bubble"><p>{{ userInput }}</p><time>待提交</time></div></div>
            <div v-if="reviewHint" class="message agent-message continuation"><div class="bubble review-feedback"><b>{{ reviewSufficient ? '资料审查通过' : '建议补充资料' }}</b><p>{{ reviewHint }}</p><small v-if="reviewMissing.length">可补充：{{ reviewMissing.join('、') }}</small></div></div>
            <div v-if="submitting" class="message agent-message continuation"><div class="bubble typing-bubble"><span>{{ liveProgress.label }}</span><i></i><i></i><i></i></div></div>

            <div v-if="!userInput.trim() && !submitting && !materials.length" class="workspace-empty">
              <div class="empty-core"><img src="/assets/spatial-agent-core.png" alt="AI Agent 空间核心" /></div>
              <h2>上传一份资料，开始构建能力证据图谱</h2>
              <p>简历、项目说明、学习记录或一段真实经历都可以作为审查起点。</p>
              <div class="empty-actions">
                <button type="button" :disabled="!selectedJobId || uploading" @click="fileInput?.click()"><UploadFilled /> 上传简历</button>
                <button type="button" :disabled="!selectedJobId || uploading" @click="fileInput?.click()"><FolderOpened /> 导入项目</button>
                <button type="button" @click="focusComposer"><EditPen /> 直接描述经历</button>
              </div>
            </div>
          </div>

          <div class="composer" :class="{ dragging, focused: composerFocused }" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="handleDrop">
            <div v-if="dragging" class="drop-overlay"><UploadFilled /><b>释放文件，加入本次资料审查</b></div>
            <textarea v-model="userInput" :disabled="submitting" placeholder="输入你的技能、项目、学习经历或疑问…" @focus="composerFocused = true" @blur="composerFocused = false" @input="resetReview"></textarea>
            <div class="composer-tools">
              <div class="tool-group">
                <button type="button" :disabled="!selectedJobId || uploading || submitting" @click="fileInput?.click()"><UploadFilled /> 简历</button>
                <button type="button" :disabled="!selectedJobId || uploading || submitting" @click="fileInput?.click()"><FolderOpened /> 项目</button>
                <button type="button" :disabled="submitting" @click="focusComposer"><EditPen /> 经历</button>
                <button type="button" :disabled="submitting" @click="focusComposer"><DocumentCopy /> 文本</button>
              </div>
              <div class="submit-group"><span>{{ userInput.length }} 字</span><button class="send-button primary-gradient-button" type="button" :disabled="submitting || !selectedJobId || userInput.trim().length < 10" @click="startReview"><span>{{ submitting ? '审查中' : '启动审查' }}</span><ArrowUp /></button></div>
            </div>
            <input ref="fileInput" type="file" hidden accept=".pdf,.docx,.txt,.md,.json,.csv,.py,.js,.ts,.java,.go,.sql,.yaml,.yml,.png,.jpg,.jpeg,.webp" @change="handleFileChange" />
          </div>
          <p v-if="uploadError" class="inline-error">{{ uploadError }}</p>
        </section>

        <aside class="review-inspector glass-surface">
          <header class="inspector-head"><div><span class="eyebrow">REVIEW INSPECTOR</span><h2>审查控制台</h2></div><span class="inspector-state" :class="{ running: submitting }"><i></i>{{ submitting ? '审查中' : reviewSufficient ? '已就绪' : '待开始' }}</span></header>

          <section class="inspector-section target-section">
            <div class="section-label"><Briefcase /> 目标岗位</div>
            <h3>{{ selectedJob?.job_title || '等待选择岗位' }}</h3>
            <p>{{ selectedJob?.description || '选择目标岗位后，系统会加载对应能力模型。' }}</p>
            <div v-if="selectedJob" class="skill-pills"><span v-for="skill in selectedJob.required_skills.slice(0, 4)" :key="skill">{{ skill }}</span></div>
          </section>

          <section class="inspector-section progress-section">
            <div class="section-label"><DataAnalysis /> 审查进度</div>
            <div class="progress-layout"><div class="progress-ring" :style="{ '--p': `${displayProgress * 3.6}deg` }"><b>{{ displayProgress }}%</b></div><div class="progress-copy"><span>整体进度</span><div class="track"><i :style="{ width: `${displayProgress}%` }"></i></div><small>{{ submitting ? liveProgress.label : reviewSufficient ? '资料可进入能力诊断' : '提交资料后开始' }}</small></div></div>
            <div v-if="submitting" class="live-agent"><span class="live-agent-dot"></span><div><small>当前执行</small><b>{{ liveProgress.agent }}</b></div><em>{{ liveProgress.status === 'failed' ? '执行失败' : '实时同步' }}</em></div>
            <ol v-if="progressEvents.length" class="progress-events" aria-label="Agent 执行记录">
              <li v-for="event in progressEvents" :key="`${event.updated_at}-${event.percent}-${event.label}`" :class="event.status"><i></i><div><b>{{ event.agent }}</b><span>{{ event.label }}</span></div><strong>{{ event.percent }}%</strong></li>
            </ol>
          </section>

          <section class="inspector-section evidence-section">
            <div class="section-label-line"><div class="section-label"><Files /> 能力证据</div><button type="button" @click="loadMaterials" :disabled="!selectedJobId"><Refresh /></button></div>
            <div v-if="materialsLoading" class="file-empty">正在读取资料…</div>
            <div v-else-if="!materials.length" class="file-empty"><DocumentCopy /> 尚未上传资料</div>
            <div v-else class="file-list"><div v-for="item in materials" :key="item.id" class="file-row"><span class="file-icon"><DocumentChecked /></span><span class="file-name">{{ item.original_name }}</span><span class="file-status" :class="item.status">{{ materialStatusText(item.status) }}</span><button type="button" aria-label="删除资料" :disabled="submitting" @click="removeMaterial(item.id)"><Close /></button></div></div>
          </section>

          <section class="inspector-section quality-section">
            <div class="section-label"><CircleCheck /> 证据质量</div>
            <div class="quality-row"><span>已解析资料</span><b>{{ parsedMaterialCount }} 项</b></div>
            <div class="quality-row"><span>学习描述</span><b>{{ userInput.trim().length >= 20 ? '已补充' : '待补充' }}</b></div>
            <div class="quality-row"><span>完整度</span><b>{{ evidenceLabel }}</b></div>
            <div class="evidence-meter"><i :style="{ width: `${evidencePercent}%` }"></i></div>
          </section>
        </aside>
      </div>

      <section class="pipeline glass-surface motion-enter motion-delay-2">
        <div class="pipeline-title"><div><span class="eyebrow">MULTI-AGENT PIPELINE</span><h2>多 Agent 协同工作中</h2></div><span class="pipeline-caption">输入摘要 → 证据抽取 → 能力对照 → 审核纠偏</span></div>
        <div class="pipeline-track">
          <template v-for="(agent, index) in pipeline" :key="agent.name">
            <div class="agent-node" :class="agent.status"><span class="agent-symbol"><component :is="agent.icon" /></span><div><b>{{ agent.name }}</b><small>{{ agent.detail }}</small><em>{{ agentStatusText(agent.status) }}</em></div></div>
            <span v-if="index < pipeline.length - 1" class="pipeline-link" :class="{ active: agent.status === 'running' || agent.status === 'completed' }"><i></i></span>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowUp, Briefcase, CircleCheck, Close, Cpu, DataAnalysis, DocumentChecked,
  DocumentCopy, EditPen, Files, FolderOpened, Link, Refresh, Search, UploadFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getJobList, type JobInfo } from '@/api/jobs'
import { createAssessment, getAssessmentProgress, reviewInput, submitAssessment, type AssessmentProgress } from '@/api/assessment'
import { createSession } from '@/api/session'
import { createTextMaterial, deleteMaterial, getMaterialList, uploadMaterial, type MaterialStatus, type UserMaterial } from '@/api/material'
import { useUserStore } from '@/stores/user'

const router = useRouter(); const route = useRoute(); const store = useUserStore()
const jobs = ref<JobInfo[]>([]); const jobLoading = ref(true); const jobError = ref(false); const selectedJobId = ref('')
const userInput = ref(''); const reviewHint = ref(''); const reviewMissing = ref<string[]>([]); const reviewSufficient = ref(false)
const fileInput = ref<HTMLInputElement | null>(null); const materials = ref<UserMaterial[]>([]); const materialsLoading = ref(false); const uploading = ref(false); const uploadError = ref('')
const submitting = ref(false); const assessmentId = ref('')
const liveProgress = ref<AssessmentProgress>({ stage: 'material', agent: '资料解析 Agent', label: '等待开始', percent: 0, status: 'waiting', updated_at: null, events: [] })
let progressTimer: number | null = null; let progressPolling = false
const dragging = ref(false); const composerFocused = ref(false)
const selectedJob = computed(() => jobs.value.find(job => job.id === selectedJobId.value) || null)
const parsedMaterialCount = computed(() => materials.value.filter(item => item.status === 'parsed').length)
const evidencePercent = computed(() => Math.min(100, (userInput.value.trim().length >= 20 ? 32 : 0) + parsedMaterialCount.value * 23 + (materials.value.length ? 10 : 0)))
const evidenceLabel = computed(() => evidencePercent.value >= 70 ? '较完整' : evidencePercent.value >= 40 ? '可用' : '待补充')
const displayProgress = computed(() => submitting.value ? Math.max(4, liveProgress.value.percent) : reviewSufficient.value ? Math.max(62, evidencePercent.value) : evidencePercent.value)
const progressEvents = computed(() => liveProgress.value.events.slice(-4).reverse())
const pipeline = computed(() => {
  const p = liveProgress.value.percent
  const active = submitting.value
  const failedStage = liveProgress.value.status === 'failed' ? liveProgress.value.stage : ''
  const statusAt = (stage: string, start: number, done: number) => !active ? (reviewSufficient.value ? 'waiting' : 'idle') : failedStage === stage ? 'failed' : p >= done ? 'completed' : p >= start ? 'running' : 'waiting'
  return [
    { icon: DocumentCopy, name: '资料解析 Agent', detail: '解析描述与上传资料', status: statusAt('material', 5, 10) },
    { icon: Search, name: '能力诊断 Agent', detail: '抽取证据并对照能力模型', status: statusAt('diagnosis', 10, 50) },
    { icon: Link, name: '路径规划 Agent', detail: '依据能力缺口规划路径', status: statusAt('path', 50, 55) },
    { icon: Cpu, name: '资源生成 Agent', detail: '检索知识库并生成资源', status: statusAt('resource', 55, 92) },
    { icon: CircleCheck, name: '审核纠偏 Agent', detail: '校验来源与生成内容', status: statusAt('review', 92, 100) },
  ]
})

async function loadJobs() { jobLoading.value = true; jobError.value = false; try { jobs.value = await getJobList(); const queryJob = typeof route.query.job === 'string' ? route.query.job : ''; if (queryJob && jobs.value.some(job => job.id === queryJob)) selectedJobId.value = queryJob; else if (!selectedJobId.value && jobs.value[0]) selectedJobId.value = jobs.value[0].id; } catch { jobError.value = true } finally { jobLoading.value = false } }
async function loadMaterials() { if (!selectedJobId.value || !store.isLoggedIn) { materials.value = []; return }; materialsLoading.value = true; try { materials.value = await getMaterialList({ job_id: selectedJobId.value }) } catch { materials.value = [] } finally { materialsLoading.value = false } }
function onJobChange() { resetReview(); loadMaterials() }
function resetReview() { reviewHint.value = ''; reviewMissing.value = []; reviewSufficient.value = false }
function focusComposer() { nextTick(() => document.querySelector<HTMLTextAreaElement>('.composer textarea')?.focus()) }
function materialStatusText(status: MaterialStatus) { return { uploaded: '已上传', parsed: '已解析', needs_ocr: '待 OCR', processing: '解析中', failed: '失败' }[status] || status }
function agentStatusText(status: string) { return { idle: '待开始', waiting: '等待中', running: '运行中', completed: '已完成', failed: '失败', blocked: '已拦截' }[status] || '等待中' }
async function uploadSelectedFile(file: File) { if (!selectedJobId.value) return; uploading.value = true; uploadError.value = ''; try { const material = await uploadMaterial(file, selectedJobId.value); materials.value.unshift(material); ElMessage.success(`${file.name} 已上传`) } catch (error: any) { uploadError.value = error?.response?.data?.detail || '资料上传失败，请重试' } finally { uploading.value = false } }
async function handleFileChange(event: Event) { const file = (event.target as HTMLInputElement).files?.[0]; if (file) await uploadSelectedFile(file); if (fileInput.value) fileInput.value.value = '' }
async function handleDrop(event: DragEvent) { dragging.value = false; const file = event.dataTransfer?.files?.[0]; if (!file || submitting.value) return; await uploadSelectedFile(file) }
async function removeMaterial(id: string) { try { await deleteMaterial(id); materials.value = materials.value.filter(item => item.id !== id) } catch { ElMessage.error('删除资料失败') } }
async function pollProgress() { if (!assessmentId.value || progressPolling) return; progressPolling = true; try { liveProgress.value = await getAssessmentProgress(assessmentId.value) } catch { /* keep the latest verified progress */ } finally { progressPolling = false } }
function startPolling() { stopPolling(); pollProgress(); progressTimer = window.setInterval(pollProgress, 900) }
function stopPolling() { if (progressTimer !== null) { window.clearInterval(progressTimer); progressTimer = null } }
async function startReview() {
  if (!store.isLoggedIn) { router.push({ path: '/login', query: { next: '/input' } }); return }
  if (!selectedJobId.value || userInput.value.trim().length < 10) return
  reviewHint.value = ''; reviewMissing.value = []; reviewSufficient.value = false
  try {
    const review = await reviewInput({ job_id: selectedJobId.value, user_input: userInput.value.trim() })
    reviewHint.value = review.hint; reviewMissing.value = review.missing || []; reviewSufficient.value = review.sufficient
    if (!review.sufficient) { ElMessage.warning('请按提示补充资料后再次审查'); return }
    submitting.value = true; liveProgress.value = { stage: 'material', agent: '资料解析 Agent', label: '正在创建审查任务', percent: 2, status: 'running', updated_at: null, events: [] }
    const [assessment, session] = await Promise.all([createAssessment({ job_id: selectedJobId.value }), createSession({ job_id: selectedJobId.value })])
    assessmentId.value = assessment.id; store.setCurrentSession(session.id); startPolling()
    const textEvidence = userInput.value.trim()
    if (!materials.value.some(item => item.extracted_text === textEvidence)) {
      try { const textMaterial = await createTextMaterial({ content: textEvidence, title: '学习经历补充', job_id: selectedJobId.value }); materials.value.unshift(textMaterial) } catch { /* diagnosis still carries user_input */ }
    }
    await submitAssessment(assessment.id, { user_input: textEvidence, material_ids: materials.value.map(item => item.id) })
    await pollProgress(); stopPolling(); liveProgress.value = { ...liveProgress.value, stage: 'complete', agent: '协同调度器', label: '审查完成', percent: 100, status: 'completed' }; await router.push(`/diagnosis/${assessment.id}`)
  } catch (error: any) { const message = error?.response?.data?.detail || '审查任务启动失败，请稍后重试'; ElMessage.error(message); reviewHint.value = message } finally { submitting.value = false; stopPolling() }
}
watch(selectedJobId, () => { if (selectedJobId.value) loadMaterials() })
onMounted(loadJobs); onBeforeUnmount(stopPolling)
</script>

<style scoped>
.review-page { background: radial-gradient(circle at 10% 8%, rgba(189,244,207,.2), transparent 32%), radial-gradient(circle at 88% 82%, rgba(222,250,222,.5), transparent 35%), linear-gradient(180deg,#fdfffe 0%,#f4fbf7 100%); }
.review-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 25px; }
.heading-action { height: 40px; padding: 0 14px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.6); color: var(--ink-soft); font-size: 12px; cursor: pointer; }
.heading-action svg { width: 15px; }
.workspace-grid { display: grid; grid-template-columns: minmax(0, 1.82fr) minmax(315px, .62fr); gap: 22px; align-items: stretch; }
.review-workspace {
  min-height: 628px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  isolation: isolate;
  border: 1px solid rgba(255,255,255,.78);
  border-radius: var(--radius-xl);
  background: linear-gradient(144deg, rgba(255,255,255,.62), rgba(247,255,250,.35) 53%, rgba(189,244,207,.13)), rgba(250,255,252,.4);
  box-shadow: 0 32px 78px rgba(20,93,56,.09), inset 0 1px 1px rgba(255,255,255,.98), inset 0 -1px 1px rgba(34,181,107,.035);
  backdrop-filter: blur(34px) saturate(158%);
}
.workspace-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 0 4px 16px; border-bottom: 1px solid var(--line); }
.workspace-status { display: flex; align-items: center; gap: 7px; color: var(--ink-soft); font-size: 12px; }
.workspace-status b { color: var(--ink); font-size: 13px; }
.pulse { height: 8px; width: 8px; border-radius: 50%; background: var(--gradient-primary); box-shadow: 0 0 0 5px rgba(19,169,99,.11), 0 0 14px rgba(34,181,107,.25); animation: breathe 2s ease-in-out infinite; }
.job-picker { display: flex; align-items: center; gap: 7px; }
.job-picker label { font-size: 11px; color: var(--ink-soft); }
.job-picker select { max-width: 190px; border: 1px solid var(--line); border-radius: 10px; padding: 7px 25px 7px 10px; color: var(--ink); background: rgba(255,255,255,.69); outline: none; font-size: 12px; }
.conversation { min-height: 334px; flex: 1; position: relative; padding: 22px 9px 14px; display: flex; flex-direction: column; gap: 15px; }
.message { display: flex; gap: 10px; align-items: flex-start; max-width: 82%; }
.message.user-message { align-self: flex-end; justify-content: flex-end; }
.message.continuation { padding-left: 41px; }
.message-avatar { width: 32px; height: 32px; flex: 0 0 32px; display: grid; place-items: center; border-radius: 11px; background: var(--gradient-primary); color: #fff; box-shadow: 0 7px 15px rgba(9,132,72,.2); }
.message-avatar svg { width: 17px; }
.bubble { padding: 13px 15px; border: 1px solid rgba(255,255,255,.82); border-radius: 18px 18px 18px 6px; background: linear-gradient(138deg, rgba(246,255,249,.64), rgba(222,250,222,.31)), rgba(245,255,248,.37); box-shadow: inset 0 1px 1px rgba(255,255,255,.96), inset 0 -1px 1px rgba(57,178,105,.035), 0 10px 24px rgba(28,89,58,.06); backdrop-filter: blur(19px) saturate(145%); color: var(--ink-soft); font-size: 12px; line-height: 1.68; }
.bubble p { margin: 0; }
.bubble time { display: block; margin-top: 7px; color: var(--ink-faint); font-size: 9px; }
.user-message .bubble { border-radius: 18px 18px 6px 18px; background: linear-gradient(145deg, rgba(255,255,255,.72), rgba(234,255,242,.34)), rgba(255,255,255,.38); box-shadow: inset 0 1px 1px rgba(255,255,255,.98), 0 12px 28px rgba(19,110,60,.07); color: var(--ink); }
.review-feedback b { display: block; color: var(--green-deep); font-size: 12px; margin-bottom: 5px; }
.review-feedback small { display: block; margin-top: 6px; color: #9b6c13; }
.typing-bubble { display: flex; align-items: center; gap: 6px; min-width: 190px; }
.typing-bubble span { margin-right: 5px; }
.typing-bubble i { width: 5px; height: 5px; border-radius: 50%; background: var(--green); animation: breathe 1.2s infinite; }
.typing-bubble i:nth-of-type(2) { animation-delay: .18s; }
.typing-bubble i:nth-of-type(3) { animation-delay: .36s; }
.workspace-empty { position: absolute; inset: 103px 0 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; pointer-events: none; }
.empty-core { width: 116px; height: 86px; overflow: hidden; border-radius: 50%; mix-blend-mode: multiply; opacity: .87; }
.empty-core img { width: 168px; height: 95px; margin-left: -25px; object-fit: cover; object-position: 51% 47%; }
.workspace-empty h2 { margin: 10px 0 6px; font-size: 17px; }
.workspace-empty p { margin: 0; color: var(--ink-soft); font-size: 11px; }
.empty-actions { display: flex; gap: 8px; margin-top: 16px; pointer-events: auto; }
.empty-actions button { height: 35px; padding: 0 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(14,94,52,.09); border-radius: 11px; background: rgba(255,255,255,.64); color: var(--ink-soft); font-size: 11px; cursor: pointer; }
.empty-actions button:hover:not(:disabled) { color: var(--green-deep); background: rgba(222,250,222,.65); }
.empty-actions svg { width: 14px; }
.composer { position: relative; z-index: 3; margin-top: auto; overflow: hidden; border-radius: 22px; padding: 14px 15px 12px; background: linear-gradient(145deg, rgba(255,255,255,.73), rgba(244,255,248,.4) 60%, rgba(189,244,207,.14)), rgba(255,255,255,.38); border: 1px solid rgba(255,255,255,.9); box-shadow: inset 0 1px 2px rgba(255,255,255,.98), inset 0 -2px 5px rgba(18,98,56,.022), 0 17px 38px rgba(27,85,56,.08); backdrop-filter: blur(27px) saturate(155%); transition: box-shadow .25s ease, border-color .25s ease; }
.composer::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(110deg, rgba(255,255,255,.34), transparent 25%, rgba(117,231,163,.07)); }
.composer > * { position: relative; z-index: 1; }
.composer.focused { border-color: rgba(134,231,177,.72); box-shadow: inset 0 1px 2px #fff, 0 0 0 4px rgba(222,250,222,.55), 0 17px 36px rgba(27,126,71,.11); }
.composer.dragging { border-color: rgba(34,181,107,.55); }
.drop-overlay { position: absolute; inset: 0; z-index: 4; display: flex; align-items: center; justify-content: center; gap: 10px; border-radius: inherit; background: rgba(238,255,244,.94); color: var(--green-deep); backdrop-filter: blur(12px); }
.drop-overlay svg { width: 21px; }
.composer textarea { width: 100%; height: 72px; resize: none; border: 0; outline: none; background: transparent; color: var(--ink); line-height: 1.62; font-size: 13px; }
.composer textarea::placeholder { color: var(--ink-faint); }
.composer-tools { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.tool-group { display: flex; gap: 6px; flex-wrap: wrap; }
.tool-group button { height: 31px; padding: 0 9px; display: inline-flex; align-items: center; gap: 5px; border: 0; border-radius: 9px; background: rgba(243,251,246,.62); color: var(--ink-soft); font-size: 10px; cursor: pointer; }
.tool-group button:hover:not(:disabled) { color: var(--green-deep); background: rgba(222,250,222,.72); }
.tool-group svg { width: 13px; }
.submit-group { display: flex; align-items: center; gap: 10px; color: var(--ink-faint); font-size: 10px; }
.send-button { min-width: 106px; height: 36px; padding: 0 12px; display: inline-flex; align-items: center; justify-content: center; gap: 7px; border-radius: 12px; font-size: 11px; font-weight: 700; cursor: pointer; }
.send-button:disabled { opacity: .43; cursor: not-allowed; transform: none; }
.send-button svg { width: 14px; }
.inline-error { margin: 9px 2px 0; color: #b33434; font-size: 12px; }

.review-inspector { min-height: 628px; padding: 21px; overflow: hidden; isolation: isolate; border: 1px solid rgba(255,255,255,.76); border-radius: var(--radius-xl); background: linear-gradient(145deg, rgba(255,255,255,.61), rgba(247,255,250,.33) 56%, rgba(189,244,207,.13)), rgba(250,255,252,.4); box-shadow: 0 28px 68px rgba(20,91,55,.085), inset 0 1px 1px rgba(255,255,255,.98); backdrop-filter: blur(32px) saturate(154%); }
.inspector-head { display: flex; align-items: start; justify-content: space-between; gap: 12px; padding-bottom: 18px; }
.inspector-head h2 { margin: 6px 0 0; font-size: 17px; }
.inspector-state { display: inline-flex; align-items: center; gap: 6px; padding: 6px 9px; border-radius: 99px; background: rgba(243,251,246,.72); color: var(--ink-faint); font-size: 9px; }
.inspector-state i { width: 6px; height: 6px; border-radius: 50%; background: #aab7b0; }
.inspector-state.running { color: var(--green-deep); background: rgba(222,250,222,.72); }
.inspector-state.running i { background: var(--green); box-shadow: 0 0 9px rgba(34,181,107,.42); }
.inspector-section { padding: 18px 2px; border-top: 1px solid rgba(20,89,53,.075); }
.section-label, .section-label-line { display: flex; align-items: center; gap: 7px; color: var(--ink-soft); font-size: 10px; font-weight: 700; text-transform: uppercase; }
.section-label svg { width: 14px; color: var(--green-deep); }
.section-label-line { justify-content: space-between; }
.section-label-line button { width: 26px; height: 26px; display: grid; place-items: center; border: 0; border-radius: 8px; background: transparent; color: var(--ink-faint); cursor: pointer; }
.section-label-line button svg { width: 13px; }
.target-section h3 { margin: 11px 0 6px; font-size: 18px; }
.target-section p { margin: 0; color: var(--ink-soft); line-height: 1.55; font-size: 11px; }
.skill-pills { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 12px; }
.skill-pills span { padding: 4px 7px; border-radius: 8px; background: rgba(222,250,222,.66); color: var(--green-deep); font-size: 9px; }
.progress-layout { display: grid; grid-template-columns: 78px 1fr; gap: 15px; align-items: center; margin-top: 13px; }
.progress-ring { width: 74px; height: 74px; display: grid; place-items: center; position: relative; border-radius: 50%; background: conic-gradient(from 210deg, #079455 0deg, #45d986 var(--p), rgba(222,250,222,.72) var(--p)); }
.progress-ring::after { content: ''; position: absolute; inset: 8px; border-radius: 50%; background: rgba(255,255,255,.88); box-shadow: inset 0 1px 2px #fff; }
.progress-ring b { position: relative; z-index: 1; color: var(--green-deep); font-size: 16px; }
.progress-copy > span { color: var(--ink); font-size: 11px; font-weight: 700; }
.track, .evidence-meter { height: 6px; margin: 8px 0; overflow: hidden; border-radius: 99px; background: rgba(98,148,118,.12); }
.track i, .evidence-meter i { display: block; height: 100%; border-radius: inherit; background: var(--gradient-progress); transition: width .45s ease; }
.progress-copy small { color: var(--ink-faint); font-size: 9px; }
.live-agent { margin-top: 13px; padding: 9px 10px; display: flex; align-items: center; gap: 8px; border: 1px solid rgba(31,158,91,.13); border-radius: 11px; background: linear-gradient(120deg,rgba(222,250,222,.5),rgba(255,255,255,.42)); }
.live-agent-dot { width: 7px; height: 7px; flex: 0 0 auto; border-radius: 50%; background: #20b66a; box-shadow: 0 0 0 5px rgba(32,182,106,.1); animation: breathe 1.6s ease-in-out infinite; }
.live-agent div { min-width: 0; flex: 1; }
.live-agent small, .live-agent b { display: block; }
.live-agent small { color: var(--ink-faint); font-size: 8px; }
.live-agent b { margin-top: 2px; overflow: hidden; color: var(--green-deep); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.live-agent em { color: var(--green-deep); font-size: 8px; font-style: normal; }
.progress-events { margin: 10px 0 0; padding: 0; display: flex; flex-direction: column; gap: 7px; list-style: none; }
.progress-events li { display: grid; grid-template-columns: auto minmax(0,1fr) auto; gap: 7px; align-items: center; color: var(--ink-faint); }
.progress-events li > i { width: 6px; height: 6px; border-radius: 50%; background: rgba(30,118,70,.24); }
.progress-events li.running > i { background: #20b66a; box-shadow: 0 0 0 3px rgba(32,182,106,.1); }
.progress-events li.completed > i { background: #079455; }
.progress-events li.failed > i { background: #d94b4b; }
.progress-events li b, .progress-events li span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.progress-events li b { color: var(--ink-soft); font-size: 8px; }
.progress-events li span { margin-top: 1px; font-size: 8px; }
.progress-events li strong { color: var(--green-deep); font-size: 8px; }
.file-empty { padding: 19px 0 2px; display: flex; align-items: center; justify-content: center; gap: 6px; color: var(--ink-faint); font-size: 10px; }
.file-empty svg { width: 14px; }
.file-list { margin-top: 11px; display: flex; flex-direction: column; gap: 9px; }
.file-row { display: grid; grid-template-columns: auto minmax(0,1fr) auto auto; gap: 7px; align-items: center; font-size: 10px; }
.file-icon { width: 22px; height: 22px; display: grid; place-items: center; border-radius: 7px; background: rgba(222,250,222,.62); color: var(--green-deep); }
.file-icon svg { width: 12px; }
.file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--ink-soft); }
.file-status { color: var(--ink-faint); font-size: 9px; }
.file-status.parsed { color: var(--green-deep); }
.file-status.failed { color: #c34c4c; }
.file-status.needs_ocr { color: #a36c18; }
.file-row button { width: 22px; height: 22px; display: grid; place-items: center; border: 0; background: transparent; color: var(--ink-faint); cursor: pointer; }
.file-row button svg { width: 12px; }
.quality-row { display: flex; justify-content: space-between; margin-top: 10px; color: var(--ink-soft); font-size: 10px; }
.quality-row b { color: var(--green-deep); }

.pipeline { margin-top: 22px; padding: 19px 23px 21px; overflow: hidden; isolation: isolate; border: 1px solid rgba(255,255,255,.76); border-radius: var(--radius-xl); background: linear-gradient(145deg, rgba(255,255,255,.58), rgba(243,255,248,.33) 52%, rgba(189,244,207,.14)), rgba(250,255,252,.38); box-shadow: 0 25px 62px rgba(20,91,55,.075), inset 0 1px 1px rgba(255,255,255,.96); backdrop-filter: blur(31px) saturate(154%); }
.pipeline-title { display: flex; align-items: end; justify-content: space-between; gap: 20px; }
.pipeline-title h2 { margin: 5px 0 0; font-size: 17px; }
.pipeline-caption { color: var(--ink-faint); font-size: 10px; }
.pipeline-track { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
.agent-node { min-width: 0; flex: 1 1 0; display: grid; grid-template-columns: auto minmax(0,1fr); gap: 9px; align-items: center; }
.agent-symbol { width: 40px; height: 40px; display: grid; place-items: center; position: relative; border-radius: 50%; color: var(--ink-faint); background: rgba(255,255,255,.58); border: 1px solid rgba(15,112,62,.1); }
.agent-symbol svg { width: 17px; }
.agent-node.running .agent-symbol { color: var(--green-deep); background: linear-gradient(135deg, #f5fff7, #bdf4cf); box-shadow: 0 0 0 6px rgba(222,250,222,.44), 0 0 22px rgba(34,181,107,.18); animation: breathe 2s ease-in-out infinite; }
.agent-node.completed .agent-symbol { color: #fff; background: var(--gradient-primary); }
.agent-node.failed .agent-symbol { color: #fff; background: linear-gradient(135deg,#e96b6b,#c83e3e); box-shadow: 0 0 0 5px rgba(217,75,75,.1); }
.agent-node b, .agent-node small, .agent-node em { display: block; }
.agent-node b { font-size: 11px; }
.agent-node small { margin-top: 3px; color: var(--ink-soft); font-size: 9px; line-height: 1.4; }
.agent-node em { margin-top: 4px; color: var(--ink-faint); font-size: 8px; font-style: normal; }
.agent-node.running em, .agent-node.completed em { color: var(--green-deep); }
.pipeline-link { width: 45px; height: 1px; position: relative; background: rgba(30,118,70,.12); overflow: hidden; }
.pipeline-link::before, .pipeline-link::after { content: ''; position: absolute; }
.pipeline-link::after { right: 0; top: -2px; width: 5px; height: 5px; border-top: 1px solid rgba(30,118,70,.25); border-right: 1px solid rgba(30,118,70,.25); transform: rotate(45deg); }
.pipeline-link i { display: block; width: 42%; height: 100%; background: var(--gradient-progress); opacity: 0; }
.pipeline-link.active i { opacity: 1; animation: link-flow 2.2s ease-in-out infinite; }
@keyframes link-flow { from { transform: translateX(-110%); } to { transform: translateX(340%); } }
.error-state { padding: 30px; border-radius: var(--radius-md); display: flex; align-items: center; gap: 14px; }
.error-state span { color: var(--ink-soft); font-size: 13px; }
.error-state button { border: 0; border-radius: 10px; padding: 9px 12px; margin-left: auto; background: var(--gradient-primary); color: #fff; cursor: pointer; }
@media (max-width: 1060px) { .workspace-grid { grid-template-columns: 1fr; } .review-inspector { min-height: auto; display: grid; grid-template-columns: repeat(2,1fr); gap: 0 22px; } .inspector-head { grid-column: 1 / 3; } .inspector-section:nth-of-type(1), .inspector-section:nth-of-type(2) { border-top: 1px solid var(--line); } .pipeline-track { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; } .pipeline-link { display: none; } }
@media (max-width: 680px) { .review-heading { display: block; } .heading-action { margin-top: 15px; } .workspace-top { align-items: flex-start; flex-direction: column; } .job-picker select { max-width: 230px; } .review-workspace { padding: 14px; min-height: 640px; } .conversation { min-height: 330px; } .workspace-empty { inset-top: 100px; } .empty-actions { flex-wrap: wrap; justify-content: center; } .composer-tools { align-items: flex-end; } .submit-group > span { display: none; } .tool-group button { padding-inline: 7px; } .review-inspector { display: block; padding: 18px; } .inspector-head { display: flex; } .pipeline { padding: 16px; } .pipeline-title { display: block; } .pipeline-caption { display: block; margin-top: 8px; } .pipeline-track { grid-template-columns: 1fr; } .message { max-width: 96%; } .error-state { display: block; } .error-state > * { display: block; margin: 8px 0; } .error-state button { margin-left: 0; } }
</style>
