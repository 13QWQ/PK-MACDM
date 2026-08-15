<template>
  <div class="detail-page">
    <!-- 顶部渐变区 -->
    <section class="detail-hero">
      <button class="back-btn" @click="$router.back()">← 返回</button>
      <h2 v-if="resource" class="page-title">{{ resource.title }}</h2>
      <p v-if="resource" class="page-desc">
        <span class="type-tag">{{ resource.content_type }}</span>
        <span class="point-tag">{{ resource.knowledge_point }}</span>
        <span v-if="resource.difficulty" class="diff-stars">
          难度：
          <span v-for="s in 5" :key="s" class="star" :class="{ on: s <= resource.difficulty }">★</span>
        </span>
        <span v-if="resource.generation_method === 'llm'" class="method-tag method-llm">AI 生成</span>
        <span v-else-if="resource.generation_method === 'rules'" class="method-tag method-rules">规则兜底生成</span>
      </p>
    </section>

    <div class="page-content">
      <!-- 加载中 -->
      <div v-if="loading" class="loading-area">
        <div class="loading-spinner"></div>
        <p>加载文档...</p>
      </div>

      <!-- 加载失败 -->
      <el-alert
        v-else-if="loadError"
        :title="loadError"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <el-button type="primary" size="small" @click="loadResource">重试</el-button>
        </template>
      </el-alert>

      <!-- 文档正文 -->
      <div v-else-if="resource" class="doc-card">
        <div class="doc-body" v-html="renderedBody"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import { getResource, type ResourceInfo } from '@/api/resource'

const route = useRoute()

const resource = ref<ResourceInfo | null>(null)
const loading = ref(false)
const loadError = ref('')

async function loadResource() {
  const id = route.params.id as string
  if (!id) return
  loading.value = true
  loadError.value = ''
  try {
    resource.value = await getResource(id)
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    loadError.value = typeof detail === 'string' ? detail : '加载文档失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadResource())
watch(() => route.params.id, () => loadResource())

// 剥掉正文里嵌入的切片元数据行（ID：/ 难度：），其余内容原样保留
function cleanBody(body: string): string {
  return body
    .split('\n')
    .filter(line => !/^(ID|难度)[：:]/.test(line.trim()))
    .join('\n')
}

const renderedBody = computed(() => {
  if (!resource.value) return ''
  return marked(cleanBody(resource.value.body)) as string
})
</script>

<style scoped>
.detail-page {
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
}

.detail-hero {
  padding: 28px 80px 36px;
  background: var(--hero-gradient);
}

.back-btn {
  border: none;
  background: none;
  font-size: 14px;
  color: #2563eb;
  cursor: pointer;
  padding: 0;
  margin-bottom: 12px;
  font-family: inherit;
}

.back-btn:hover { text-decoration: underline; }

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #111827;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.type-tag {
  padding: 2px 10px;
  background: #eef2ff;
  color: #2563eb;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.point-tag {
  padding: 2px 10px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 4px;
  font-size: 12px;
}

.method-tag {
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.method-llm {
  background: #eef2ff;
  color: #2563eb;
}

.method-rules {
  background: #fffbeb;
  color: #b45309;
}

.diff-stars { font-size: 13px; color: #888; }
.star { color: #e5e7eb; }
.star.on { color: #f59e0b; }

.page-content {
  max-width: 860px;
  margin: 0 auto;
  padding: 0 80px 60px;
}

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

.doc-card {
  background: #fff;
  border-radius: 16px;
  padding: 36px 40px;
  margin-top: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

/* ---- Markdown 正文排版 ---- */
.doc-body :deep(h1) { font-size: 24px; font-weight: 700; color: #111827; margin: 24px 0 12px; }
.doc-body :deep(h2) { font-size: 20px; font-weight: 700; color: #111827; margin: 20px 0 10px; }
.doc-body :deep(h3) { font-size: 17px; font-weight: 600; color: #111827; margin: 16px 0 8px; }
.doc-body :deep(p) { font-size: 15px; color: #444; line-height: 1.9; margin-bottom: 14px; }
.doc-body :deep(ul), .doc-body :deep(ol) { padding-left: 24px; margin-bottom: 14px; }
.doc-body :deep(li) { font-size: 15px; color: #444; line-height: 1.8; margin-bottom: 4px; }
.doc-body :deep(code) { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #dc2626; font-family: Consolas, Monaco, monospace; }
.doc-body :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin-bottom: 14px; font-size: 13px; line-height: 1.6; }
.doc-body :deep(blockquote) { border-left: 3px solid #2563eb; padding: 8px 16px; background: #f8fafc; border-radius: 0 6px 6px 0; margin-bottom: 14px; color: #555; }
</style>
