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

// 检查是否为开发环境
const isDevelopment = () => {
  return import.meta.env.DEV || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
}

// 检查是否启用预览模式
const checkPreviewMode = (to) => {
  if (!isDevelopment()) {
    return false
  }
  
  // 检查URL参数
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('preview') === 'true'
}

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否是需要登录的页面
  const requiresAuth = ['PptShow', 'PptShow2', 'PptTeach', 'PptTeach2'].includes(to.name)
  
  if (requiresAuth) {
    // 检查是否有session_id
    const sessionId = localStorage.getItem('session_id')
    
    // 如果没有session_id但启用了预览模式，允许访问
    if (!sessionId && checkPreviewMode()) {
      next()
    } 
    // 如果有session_id，允许访问
    else if (sessionId) {
      next()
    } 
    // 否则重定向到登录页
    else {
      next({ name: 'Home' })
    }
  } else {
    next()
  }
})

export default router
