import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { setUnauthorizedHandler } from '@/api/client'

import AppLayout from '@/components/layout/AppLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
      { path: 'search', name: 'search', component: () => import('@/views/SearchView.vue') },
      {
        path: 'playlists/:id',
        name: 'playlist',
        component: () => import('@/views/PlaylistDetailView.vue'),
      },
      {
        path: 'songs/:id',
        name: 'song',
        component: () => import('@/views/SongDetailView.vue'),
      },
      {
        path: 'collections',
        name: 'collections',
        component: () => import('@/views/CollectionsView.vue'),
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
      },
      {
        path: 'admin/songs',
        name: 'admin-songs',
        component: () => import('@/views/AdminSongsView.vue'),
        meta: { admin: true },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !auth.isAdmin) {
    return { name: 'home' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'home' }
  }
})

// 401 时由 axios 拦截器触发：登出并跳登录
setUnauthorizedHandler(() => {
  const auth = useAuthStore()
  auth.logout()
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
})

export default router
