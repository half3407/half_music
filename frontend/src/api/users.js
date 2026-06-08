import client from './client'

export const usersApi = {
  // body: UserIn { username, password, role? }
  register: (data) => client.post('/users/register', data),
  login: (data) => client.post('/users/login', data),

  viewAll: (page = 1, page_size = 12) =>
    client.post('/users/view_all_user', null, { params: { page, page_size } }),

  search: (username, page = 1, page_size = 12) =>
    client.post('/users/search_user', null, { params: { username, page, page_size } }),

  viewSingle: (userId) => client.post(`/users/view_single_user/${userId}`),

  // body: UserIn（注意：后端改密码用 MD5，会与登录 bcrypt 不一致，慎用）
  update: (userId, data) => client.post(`/users/update_user/${userId}`, data),

  remove: (userId, deletePlaylists = true) =>
    client.post(`/users/delete_user/${userId}`, null, {
      params: { delete_playlists: deletePlaylists },
    }),
}
