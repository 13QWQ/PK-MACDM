<template>
  <div class="home-page">
    <!-- Hero区域 -->
    <section class="hero">
      <div class="hero-left">
        <h1 class="hero-title">用 AI 诊断目标能力<br>生成你的下一步学习资源</h1>
        <p class="hero-subtitle">面向职业学习者的目标能力诊断与个性化培训资源生成系统</p>
        <p class="hero-desc">提交你的技能、项目经验、学习经历等资料，系统将通过 AI 分析你的能力水平，判断是否满足目标岗位要求，识别未达标或证据不足的能力，并生成个性化的培训资源与学习路径。</p>
        <div class="hero-buttons">
          <button class="app-btn app-btn-primary app-btn-large" @click="$router.push('/input')">🚀 立即开始诊断</button>
          <button class="app-btn app-btn-outline app-btn-large" @click="showExample = true">📄 查看示例报告</button>
        </div>
        <div class="tag-group">
          <span class="tag-label">👤 适合人群：</span>
          <span class="tag">大学生</span>
          <span class="tag">应届毕业生</span>
          <span class="tag">转行者</span>
          <span class="tag">在职技能提升者</span>
          <span class="tag">企业培训学员</span>
        </div>
      </div>
      <div class="hero-right">
        <div class="flow-card">
          <div class="flow-title">AI 驱动的资料审查与能力提升流程</div>
          <div class="flow-steps">
            <div class="flow-step">
              <div class="step-number">1</div>
              <div class="step-icon">📝</div>
              <div class="step-name">资料提交</div>
              <div class="step-desc">描述你的技能、项目经验、学习经历</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="step-number">2</div>
              <div class="step-icon">📊</div>
              <div class="step-name">AI 分析</div>
              <div class="step-desc">AI 分析能力水平，识别优势与薄弱点</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="step-number">3</div>
              <div class="step-icon">🎯</div>
              <div class="step-name">资源生成</div>
              <div class="step-desc">生成个性化学习资源与提升路径</div>
            </div>
          </div>
          <div class="flow-tags">
            <span class="flow-tag">自由文本输入</span>
            <span class="flow-tag">AI 智能分析</span>
            <span class="flow-tag">个性化方案</span>
          </div>
          <div class="flow-bottom">
            <span>✦ 基于多 Agent 协同分析，让学习更有方向，让提升更高效</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能卡片区域 -->
    <section class="features">
      <div class="feature-card">
        <div class="feature-header">
          <div class="feature-icon blue">📝</div>
          <span class="feature-name">资料审查</span>
          <span class="feature-badge">自由输入</span>
        </div>
        <p class="feature-desc">自由描述你的技能、项目经验、学习经历、课程记录等，AI 将全面分析你的能力水平，无需填写固定表单。</p>
        <a href="#" class="feature-link" @click.prevent="$router.push('/input')">开始资料审查 →</a>
      </div>
      <div class="feature-card">
        <div class="feature-header">
          <div class="feature-icon green">📊</div>
          <span class="feature-name">能力诊断</span>
          <span class="feature-badge green">AI 智能判定</span>
        </div>
        <p class="feature-desc">对照目标岗位能力模型，AI 多维度分析你的能力，判断整体达标度，识别优势能力与薄弱知识点。</p>
        <a href="#" class="feature-link" @click.prevent="showExample = true">查看诊断示例 →</a>
      </div>
      <div class="feature-card">
        <div class="feature-header">
          <div class="feature-icon purple">📚</div>
          <span class="feature-name">资源包</span>
          <span class="feature-badge purple">个性化推荐</span>
        </div>
        <p class="feature-desc">基于诊断结果，为你推荐个性化的学习资源，包括讲义、练习、案例、视频等多种类型。</p>
        <a href="#" class="feature-link" @click.prevent="showResourceExample = true">查看资源示例 →</a>
      </div>
    </section>

    <!-- 学习路径卡片 -->
    <section class="features" style="padding-top: 0">
      <div class="feature-card feature-card-full">
        <div class="feature-header">
          <div class="feature-icon blue">🗺️</div>
          <span class="feature-name">个性化学习路径</span>
          <span class="feature-badge">智能规划</span>
        </div>
        <p class="feature-desc" style="max-width: 800px">根据你的能力诊断结果，AI 为你规划专属的学习路径，按步骤提升薄弱能力，每个步骤都配有推荐资源和预计学习时间，让学习更有条理、更高效。</p>
        <a href="#" class="feature-link" @click.prevent="showPathExample = true">查看路径示例 →</a>
      </div>
    </section>

    <!-- 底部特色 -->
    <section class="bottom-features">
      <div class="bottom-feature">
        <div class="bottom-feature-icon blue">🔍</div>
        <div>
          <div class="bottom-feature-name">证据链判定</div>
          <div class="bottom-feature-desc">以你提供的资料为基础，确保分析客观、可验证</div>
        </div>
      </div>
      <div class="bottom-feature">
        <div class="bottom-feature-icon cyan">🤝</div>
        <div>
          <div class="bottom-feature-name">多 Agent 协同</div>
          <div class="bottom-feature-desc">多个 AI Agent 协同分析，结论更全面、准确</div>
        </div>
      </div>
      <div class="bottom-feature">
        <div class="bottom-feature-icon green">📋</div>
        <div>
          <div class="bottom-feature-name">资源可追溯</div>
          <div class="bottom-feature-desc">所有推荐资源均可追溯来源与依据，学习更安心</div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      职学导航 © 2026 - 面向职业学习者的目标能力诊断与个性化培训资源生成系统
    </footer>

    <!-- 示例报告弹窗 -->
    <el-dialog
      v-model="showExample"
      title="示例诊断报告（仅供参考）"
      width="920px"
      top="3vh"
      :close-on-click-modal="false"
      @opened="initExampleChart"
      @closed="disposeExampleChart"
    >
      <div class="example-report">
        <!-- 概览行 -->
        <div class="ex-overview">
          <div class="ex-mastery">
            <div class="ex-label">综合掌握度</div>
            <div class="mastery-ring" style="--pct:0.72">
              <span class="mastery-value">72</span>
              <span class="mastery-unit">分</span>
            </div>
            <span class="mastery-tag mid">部分达标</span>
          </div>
          <div class="ex-meta">
            <div class="ex-meta-item"><span>置信度</span><strong>85%</strong></div>
            <div class="ex-meta-item"><span>能力维度</span><strong>16 项</strong></div>
            <div class="ex-meta-item"><span>知识缺口</span><strong style="color:#dc2626">2 项</strong></div>
            <div class="ex-meta-item"><span>诊断时间</span><strong>2026-07-16 17:23</strong></div>
          </div>
        </div>

        <!-- 我的输入 -->
        <div class="ex-input">
          <h4>📝 我的输入</h4>
          <div class="ex-input-body">我目前是计算机专业大三学生，目标是成为一名前端开发工程师。熟悉 HTML、CSS 和 JavaScript，用 Vue 做过两个课程项目（电商前端页面、校园活动报名系统），主要负责页面布局、组件封装和接口联调，使用过 Webpack，了解响应式布局。目前算法题刷得少，贪心和动态规划不太熟练，前端性能优化和 TypeScript 也是初学，希望系统帮我分析短板并给出学习建议。</div>
        </div>

        <!-- 雷达图 -->
        <div class="ex-chart-card">
          <h4>能力雷达图</h4>
          <div ref="exampleChartRef" class="radar-chart"></div>
        </div>

        <!-- 知识缺口 -->
        <div class="ex-gaps">
          <h4>知识缺口</h4>
          <p class="ex-gap-sub">以下能力领域尚未达标或证据不足，建议重点关注</p>
          <div class="ex-gap-item"><span>1</span>TypeScript</div>
          <div class="ex-gap-item"><span>2</span>前端性能优化</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showExample = false">关闭</el-button>
        <el-button type="primary" @click="showExample = false; $router.push('/input')">开始我的诊断</el-button>
      </template>
    </el-dialog>

    <!-- 资源包示例弹窗 -->
    <el-dialog
      v-model="showResourceExample"
      title="资源包示例（仅供参考）"
      width="720px"
      top="18vh"
      :close-on-click-modal="false"
    >
      <div class="example-resources">
        <div class="resource-card">
          <div class="rc-header">
            <span class="rc-type-icon">📖</span>
            <span class="rc-type-tag">讲义</span>
            <span class="rc-difficulty">
              <span v-for="s in 5" :key="s" class="star" :class="{ on: s <= 3 }">★</span>
            </span>
          </div>
          <h4 class="rc-title">TypeScript 类型系统入门</h4>
          <div class="rc-footer">
            <span class="rc-point">TypeScript</span>
            <span class="rc-arrow">查看 →</span>
          </div>
        </div>
        <div class="resource-card">
          <div class="rc-header">
            <span class="rc-type-icon">✏️</span>
            <span class="rc-type-tag">练习</span>
            <span class="rc-difficulty">
              <span v-for="s in 5" :key="s" class="star" :class="{ on: s <= 4 }">★</span>
            </span>
          </div>
          <h4 class="rc-title">前端性能优化实战练习</h4>
          <div class="rc-footer">
            <span class="rc-point">前端性能优化</span>
            <span class="rc-arrow">查看 →</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResourceExample = false">关闭</el-button>
        <el-button type="primary" @click="showResourceExample = false; $router.push('/input')">开始我的诊断</el-button>
      </template>
    </el-dialog>

    <!-- 学习路径示例弹窗 -->
    <el-dialog
      v-model="showPathExample"
      title="学习路径示例（仅供参考）"
      width="720px"
      top="8vh"
      :close-on-click-modal="false"
    >
      <div class="example-path">
        <div class="path-status-row">
          <span class="path-status-badge active">进行中</span>
          <span class="path-date">创建于 2026-08-10</span>
        </div>
        <div class="timeline">
          <div
            v-for="(step, i) in EXAMPLE_PATH_STEPS"
            :key="step.step"
            class="timeline-step"
            :class="{ last: i === EXAMPLE_PATH_STEPS.length - 1 }"
          >
            <div class="tl-left">
              <div class="tl-node" :class="step.status">
                <span v-if="step.status === 'completed'">✓</span>
                <span v-else>{{ step.step }}</span>
              </div>
              <div v-if="i < EXAMPLE_PATH_STEPS.length - 1" class="tl-line" :class="{ filled: step.status === 'completed' }"></div>
            </div>
            <div class="tl-content">
              <div class="tl-title-row">
                <span class="tl-type-icon">{{ step.resource_type === '讲义' ? '📖' : '✏️' }}</span>
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
      <template #footer>
        <el-button @click="showPathExample = false">关闭</el-button>
        <el-button type="primary" @click="showPathExample = false; $router.push('/input')">开始我的诊断</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

const showExample = ref(false)
const showResourceExample = ref(false)
const showPathExample = ref(false)
const exampleChartRef = ref<HTMLDivElement | null>(null)
let exampleChart: echarts.ECharts | null = null

// 示例雷达图 — 16 维度的静态 mock 数据
const EXAMPLE_VECTOR = [
  { name: '编程基础', value: 0.8, weight: 'high' as const },
  { name: '数据结构与算法', value: 0.6, weight: 'mid' as const },
  { name: '计算机网络', value: 0.9, weight: 'mid' as const },
  { name: '操作系统', value: 0.7, weight: 'low' as const },
  { name: '前端技术', value: 0.5, weight: 'high' as const },
  { name: '后端技术', value: 0.8, weight: 'mid' as const },
  { name: '数据库', value: 0.6, weight: 'mid' as const },
  { name: '系统设计', value: 0.9, weight: 'mid' as const },
  { name: '运维部署', value: 0.7, weight: 'low' as const },
  { name: '测试与质量', value: 0.8, weight: 'mid' as const },
  { name: '产品分析', value: 0.6, weight: 'mid' as const },
  { name: '项目管理', value: 0.5, weight: 'low' as const },
  { name: '沟通表达', value: 0.9, weight: 'mid' as const },
  { name: '逻辑思维', value: 0.7, weight: 'mid' as const },
  { name: '学习能力', value: 0.8, weight: 'mid' as const },
  { name: '安全规范', value: 0.6, weight: 'low' as const },
]

// 示例学习路径 — 静态 mock（对应前端开发工程师，HTML→CSS→JS→Vue→React→TypeScript）
const EXAMPLE_PATH_STEPS = [
  { step: 1, knowledge_point: 'HTML', resource_type: '讲义', estimated_time: 30, prerequisite: null, status: 'pending', weight: 'high' },
  { step: 2, knowledge_point: 'CSS', resource_type: '练习', estimated_time: 30, prerequisite: 'HTML', status: 'pending', weight: 'high' },
  { step: 3, knowledge_point: 'JavaScript', resource_type: '讲义', estimated_time: 30, prerequisite: 'CSS', status: 'pending', weight: 'high' },
  { step: 4, knowledge_point: 'Vue', resource_type: '练习', estimated_time: 30, prerequisite: 'JavaScript', status: 'pending', weight: 'mid' },
  { step: 5, knowledge_point: 'React', resource_type: '讲义', estimated_time: 30, prerequisite: 'Vue', status: 'pending', weight: 'mid' },
  { step: 6, knowledge_point: 'TypeScript', resource_type: '练习', estimated_time: 30, prerequisite: 'React', status: 'pending', weight: 'mid' },
]

function initExampleChart() {
  if (!exampleChartRef.value) return
  const weightColors: Record<string, string> = { high: '#dc2626', mid: '#f59e0b', low: '#2563eb' }
  exampleChart = echarts.init(exampleChartRef.value)
  exampleChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => {
        const d = EXAMPLE_VECTOR[p.dataIndex]
        return `<b>${p.name}</b><br/>得分：${(d.value * 100).toFixed(0)}<br/>权重：${d.weight === 'high' ? '高' : d.weight === 'mid' ? '中' : '低'}`
      },
    },
    radar: {
      center: ['50%', '55%'],
      radius: '65%',
      axisName: { fontSize: 12, color: '#555' },
      indicator: EXAMPLE_VECTOR.map(d => ({
        name: d.name, max: 1,
        color: weightColors[d.weight] || '#555',
      })),
    },
    series: [{
      type: 'radar',
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2, color: '#2563eb' },
      areaStyle: { color: 'rgba(37,99,235,0.12)' },
      itemStyle: { color: '#2563eb' },
      data: [{ value: EXAMPLE_VECTOR.map(d => d.value), name: '能力值' }],
    }],
  })
}

function disposeExampleChart() {
  exampleChart?.dispose()
  exampleChart = null
}
</script>

<style scoped>
/* ---- Hero区域 ---- */
.hero {
  display: flex;
  padding: 60px 80px;
  gap: 60px;
  background: var(--hero-gradient);
}

.hero-left {
  flex: 1;
  max-width: 520px;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  line-height: 1.3;
  color: #111827;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 18px;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 12px;
}

.hero-desc {
  font-size: 15px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 28px;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  margin-bottom: 28px;
}

.tag-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag {
  padding: 4px 12px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 4px;
  font-size: 13px;
}

/* ---- Hero右侧卡片 ---- */
.hero-right {
  flex: 1;
  max-width: 560px;
}

.flow-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.flow-title {
  font-size: 18px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 32px;
  color: #111827;
}

.flow-steps {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
}

.step-number {
  width: 32px;
  height: 32px;
  background: #2563eb;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
}

.step-icon {
  width: 64px;
  height: 64px;
  background: #eef2ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 12px;
}

.step-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #111827;
}

.step-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.flow-arrow {
  display: flex;
  align-items: center;
  color: #d0d5dd;
  font-size: 20px;
  margin-top: 40px;
}

.flow-tags {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.flow-tag {
  padding: 4px 10px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 4px;
  font-size: 12px;
}

.flow-bottom {
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 20px;
}

.flow-bottom span {
  color: #2563eb;
  font-size: 13px;
}

/* ---- 功能卡片区域 ---- */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 40px 80px;
}

.feature-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.feature-card-full {
  grid-column: 1 / -1;
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.feature-icon.blue {
  background: #eef2ff;
  color: #2563eb;
}

.feature-icon.green {
  background: #f0fdf4;
  color: #16a34a;
}

.feature-icon.purple {
  background: #faf5ff;
  color: #9333ea;
}

.feature-name {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.feature-badge {
  padding: 2px 8px;
  background: #dbeafe;
  color: #2563eb;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.feature-badge.green {
  background: #dcfce7;
  color: #16a34a;
}

.feature-badge.purple {
  background: #f3e8ff;
  color: #9333ea;
}

.feature-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.7;
  margin-bottom: 16px;
}

.feature-link {
  color: #2563eb;
  font-size: 14px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.feature-link:hover {
  text-decoration: underline;
}

/* ---- 底部特色 ---- */
.bottom-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  margin: 0 80px 60px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.bottom-feature {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 28px;
  border-right: 1px solid #f0f0f0;
}

.bottom-feature:last-child {
  border-right: none;
}

.bottom-feature-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.bottom-feature-icon.blue {
  background: #eef2ff;
  color: #2563eb;
}

.bottom-feature-icon.cyan {
  background: #ecfeff;
  color: #0891b2;
}

.bottom-feature-icon.green {
  background: #f0fdf4;
  color: #16a34a;
}

.bottom-feature-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.bottom-feature-desc {
  font-size: 13px;
  color: #666;
}

/* ---- 页脚 ---- */
.footer {
  text-align: center;
  padding: 24px;
  color: #999;
  font-size: 13px;
  border-top: 1px solid #eee;
  background: #fff;
}

/* ---- 示例报告弹窗内容 ---- */
.example-report {
  padding: 0 8px;
}

.ex-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.ex-mastery {
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ex-label {
  font-size: 14px;
  color: #888;
  margin-bottom: 14px;
}

/* 掌握度圆环（与 DiagnosisPage 一致） */
.mastery-ring {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  --pct: 0;
  background: conic-gradient(#2563eb calc(var(--pct) * 360deg), #e5e7eb 0deg);
}

.mastery-ring::after {
  content: '';
  position: absolute;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: #f8fafc;
}

.mastery-value {
  position: relative;
  z-index: 1;
  font-size: 30px;
  font-weight: 800;
  color: #111827;
  line-height: 1;
}

.mastery-unit {
  position: relative;
  z-index: 1;
  font-size: 12px;
  color: #888;
}

.mastery-tag {
  font-size: 13px;
  font-weight: 600;
  padding: 3px 14px;
  border-radius: 12px;
}

.mastery-tag.mid { background: #fef3c7; color: #d97706; }

.ex-meta {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  justify-content: center;
}

.ex-meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #888;
}

.ex-meta-item strong {
  color: #111827;
  font-size: 15px;
}

.ex-input {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.ex-input h4 {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.ex-input-body {
  font-size: 14px;
  color: #444;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  background: #fff;
  border-radius: 8px;
  padding: 14px 16px;
}

.ex-chart-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.ex-chart-card h4 {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.radar-chart {
  width: 100%;
  height: 360px;
}

.ex-gaps {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px 24px;
}

.ex-gaps h4 {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 2px;
}

.ex-gap-sub {
  font-size: 12px;
  color: #999;
  margin-bottom: 14px;
}

.ex-gap-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #fef2f2;
  border-radius: 6px;
  border-left: 3px solid #fca5a5;
  font-size: 14px;
  color: #991b1b;
  margin-bottom: 8px;
}

.ex-gap-item span {
  width: 22px;
  height: 22px;
  background: #fca5a5;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

/* ---- 资源包示例卡片 ---- */
.example-resources {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.resource-card {
  width: 300px;
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

/* ---- 学习路径示例时间线 ---- */
.example-path {
  padding: 0 8px;
}

.path-status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 14px;
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
</style>
