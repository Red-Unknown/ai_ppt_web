import { createRouter, createWebHistory } from 'vue-router'
import LoginHome from '../pages/LoginHome.vue'
import PptShow from '../pages/PptShow.vue'
import PptShow2 from '../pages/PptShow2.vue'
import PptTeach from '../pages/PptTeach.vue'
import PptTeach2 from '../pages/PptTeach2.vue'
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
    path: '/ppt-show2',
    name: 'PptShow2',
    component: PptShow2
  },
  {
    path: '/ppt-teach',
    name: 'PptTeach',
    component: PptTeach
  },
  {
    path: '/ppt-teach2',
    name: 'PptTeach2',
    component: PptTeach2
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
