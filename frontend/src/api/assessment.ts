import request from './request'

export interface DimensionItem {
  index: number
  name: string
  value: number
  weight: 'high' | 'mid' | 'low'
  category: string
}

export interface GapValidationItem {
  gap: string
  status: 'grounded' | 'partial' | 'ungrounded'
  reason: string
}

export interface AssessmentResponse {
  id: string
  user_id: string
  job_id: string
  user_input: string | null
  overall_mastery: number | null
  ability_vector: DimensionItem[]
  knowledge_gaps: string[]
  gap_validation: GapValidationItem[] | null
  confidence: number | null
  created_at: string
}

export interface AssessmentListItem {
  id: string
  user_id: string
  job_id: string
  overall_mastery: number | null
  knowledge_gaps: string[]
  created_at: string
}

export interface ReviewInputResponse {
  sufficient: boolean
  missing: string[]
  hint: string
}

/** 创建一次评估 */
export function createAssessment(data: { job_id: string }): Promise<{ id: string }> {
  return request.post('/assessment/create', data) as any
}

/** 输入完整性审查（提交前预检） */
export function reviewInput(data: { job_id: string; user_input: string }): Promise<ReviewInputResponse> {
  return request.post('/assessment/review-input', data) as any
}

/** 提交用户输入，触发 AI 诊断（14 次 LLM 调用 + BGE-M3 加载，超时设为 10 分钟） */
export function submitAssessment(id: string, data: { user_input: string }): Promise<AssessmentResponse> {
  return request.post(`/assessment/${id}/submit`, data, { timeout: 600_000 }) as any
}

/** 查询单次评估详情 */
export function getAssessment(id: string): Promise<AssessmentResponse> {
  return request.get(`/assessment/${id}`) as any
}

/** 查询诊断进度（前端轮询用） */
export function getAssessmentProgress(id: string): Promise<{ label: string; percent: number }> {
  return request.get(`/assessment/${id}/progress`) as any
}

/** 当前用户的评估历史 */
export function getAssessmentList(): Promise<AssessmentListItem[]> {
  return request.get('/assessment/list') as any
}

/** 删除评估记录 */
export function deleteAssessment(id: string): Promise<void> {
  return request.delete(`/assessment/${id}`) as any
}
