import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/LoginHome.vue'

const routes = [
  // 登录主页
  {
    path: '/',
    name: 'Home',
    component: Home

  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router