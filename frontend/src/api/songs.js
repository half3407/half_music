import client from './client'

export const songsApi = {
  viewAll: (page = 1, page_size = 12) =>
    client.post('/songs/view_all', null, { params: { page, page_size } }),

  search: (keyword, page = 1, page_size = 12) =>
    client.post('/songs/search_song', null, { params: { keyword, page, page_size } }),

  viewSingle: (songId) => client.post(`/songs/view_single/${songId}`),

  // body: SongIn（管理员）
  create: (data) => client.post('/songs/create', data),
  update: (songId, data) => client.post(`/songs/update/${songId}`, data),
  remove: (songId) => client.post(`/songs/delete/${songId}`),

  // 歌单所有者
  addToPlaylist: (songId, playlistId) =>
    client.post(`/songs/add_to_playlist/${songId}/${playlistId}`),
  removeFromPlaylist: (songId, playlistId) =>
    client.post(`/songs/delete_from_playlist/${songId}/${playlistId}`),
}
