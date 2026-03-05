import { createRouter, createWebHistory } from 'vue-router'
import LoginHome from '../pages/LoginHome.vue'
import PptShow from '../pages/PptShow.vue'
import PptTeach from '../pages/PptTeach.vue'
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
  },
  {
    path: '/ppt-teach',
    name: 'PptTeach',
    component: PptTeach
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
