import client from './client'

export const commentsApi = {
  // body: CommentIn { content, song_id }
  create: (data) => client.post('/comments/create', data),

  remove: (commentId) => client.post(`/comments/delete/${commentId}`),

  // 仅返回 [{comment_id, created_at}]，需逐条 viewOne 取内容
  viewAll: (songId, page = 1, page_size = 12) =>
    client.post(`/comments/view_all/${songId}`, null, { params: { page, page_size } }),

  viewOne: (commentId) => client.post(`/comments/view/${commentId}`),
}
