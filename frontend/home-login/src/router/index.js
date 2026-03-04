import { createRouter, createWebHistory } from 'vue-router'
import LoginHome from '../pages/LoginHome.vue'
const routes = [
  {
    path: '/',
    name: 'Home',
    component: LoginHome
  },
  {
    path: '/login2',
    name: 'Login2',
    component: LoginHome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
