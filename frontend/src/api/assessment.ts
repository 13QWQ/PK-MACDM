import request from './request'

export interface DimensionItem {
  index: number
  name: string
  value: number
  weight: 'high' | 'mid' | 'low'
  category: string
}

export interface AssessmentResponse {
  id: string
  user_id: string
  job_id: string
  overall_mastery: number | null
  ability_vector: DimensionItem[]
  knowledge_gaps: string[]
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

/** 创建一次评估 */
export function createAssessment(data: { job_id: string }): Promise<{ id: string }> {
  return request.post('/assessment/create', data) as any
}

/** 提交用户输入，触发 AI 诊断 */
export function submitAssessment(id: string, data: { user_input: string }): Promise<AssessmentResponse> {
  return request.post(`/assessment/${id}/submit`, data) as any
}

/** 查询单次评估详情 */
export function getAssessment(id: string): Promise<AssessmentResponse> {
  return request.get(`/assessment/${id}`) as any
}

/** 当前用户的评估历史 */
export function getAssessmentList(): Promise<AssessmentListItem[]> {
  return request.get('/assessment/list') as any
}

/** 删除评估记录 */
export function deleteAssessment(id: string): Promise<void> {
  return request.delete(`/assessment/${id}`) as any
}
