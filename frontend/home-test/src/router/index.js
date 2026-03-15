import { createRouter, createWebHistory } from 'vue-router'
import loginHomeRoutes from './LoginHome.js'
import pptShowRoutes from './PptShow.js'
import pptShow2Routes from './PptShow2.js'
import pptTeachRoutes from './PptTeach.js'
import pptTeach2Routes from './PptTeach2.js'

// 组合所有路由
const routes = [
  ...loginHomeRoutes,
  ...pptShowRoutes,
  ...pptShow2Routes,
  ...pptTeachRoutes,
  ...pptTeach2Routes
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
