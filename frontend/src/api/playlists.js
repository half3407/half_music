import client from './client'

export const playlistsApi = {
  viewAll: (page = 1, page_size = 12) =>
    client.post('/playlists/view_all', null, { params: { page, page_size } }),

  search: (playlist_name, page = 1, page_size = 12) =>
    client.post('/playlists/search_playlist', null, {
      params: { playlist_name, page, page_size },
    }),

  viewSingle: (playlistId) => client.post(`/playlists/view_single/${playlistId}`),

  // body: PlaylistIn { playlist_name, playlist_introduction?, playlist_cover_url? }
  create: (data) => client.post('/playlists/create', data),
  update: (playlistId, data) => client.post(`/playlists/update/${playlistId}`, data),
  remove: (playlistId) => client.post(`/playlists/delete/${playlistId}`),

  collect: (playlistId) => client.post(`/playlists/collect/${playlistId}`),
}
