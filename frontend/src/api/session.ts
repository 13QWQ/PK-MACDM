import request from './request'

/** 创建学习会话 */
export function createSession(data: { job_id: string }): Promise<{ id: string }> {
  return request.post('/session/create', data) as any
}
