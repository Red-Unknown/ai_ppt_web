import { createRouter, createWebHistory } from 'vue-router'
import LoginHome from '../pages/LoginHome.vue'
import PptShow from '../pages/PptShow.vue'
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
  },
  {
    path: '/ppt-show',
    name: 'PptShow',
    component: PptShow
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
