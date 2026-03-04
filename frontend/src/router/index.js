import { createRouter, createWebHistory } from 'vue-router'
import LoginHome from '../views/LoginHome.vue'
import EnhancedChat from '../components/EnhancedChat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: LoginHome
  },
  {
    path: '/debug',
    name: 'Debug',
    component: EnhancedChat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
