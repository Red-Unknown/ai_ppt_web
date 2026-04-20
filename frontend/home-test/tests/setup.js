import { createApp } from 'vue'

// 全局设置
global.Vue = { createApp }
global.createApp = createApp

// Mock 全局方法
global.confirm = jest.fn(() => true)
global.alert = jest.fn()

// Mock window
Object.defineProperty(global, 'window', {
  value: {
    addEventListener: jest.fn(),
    removeEventListener: jest.fn()
  }
})

// Mock requestAnimationFrame
global.requestAnimationFrame = (cb) => {
  setTimeout(cb, 0)
}

// Mock getBoundingClientRect
Object.defineProperty(HTMLElement.prototype, 'getBoundingClientRect', {
  value: () => ({
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    width: 100,
    height: 50
  })
})
