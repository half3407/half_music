import client from './client'

function formData(file) {
  const fd = new FormData()
  fd.append('file', file)
  return fd
}

export const filesApi = {
  // 管理员：封面图片，返回 { data: { file_url } }
  uploadCover: (file) => client.post('/files/cover', formData(file)),
  // 管理员：音频文件
  uploadSong: (file) => client.post('/files/song', formData(file)),
  // 登录用户：头像（注意：后端 User 缺 avatar_url 字段，可能 500）
  uploadAvatar: (file) => client.post('/files/avatar', formData(file)),
}
