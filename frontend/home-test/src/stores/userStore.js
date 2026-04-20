import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: {
      name: '学生',
      studentId: '20260001',
      major: '计算机科学与技术'
    }
  }),
  
  getters: {
    userName: (state) => state.userInfo.name || '学生'
  },
  
  actions: {
    updateUserInfo(info) {
      this.userInfo = { ...info }
      // 持久化到 localStorage
      localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
    },
    
    loadUserInfo() {
      const savedInfo = localStorage.getItem('userInfo')
      if (savedInfo) {
        try {
          this.userInfo = JSON.parse(savedInfo)
        } catch (error) {
          console.error('Failed to load user info from localStorage:', error)
        }
      }
    }
  }
})