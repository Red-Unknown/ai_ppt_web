import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import EnhancedChat from '../components/EnhancedChat.vue'

// Mock fetch
global.fetch = vi.fn((url) => {
  if (url && url.includes && url.includes('/session/start')) {
    return Promise.resolve({
      json: () => Promise.resolve({ session_id: 'sess_123' }),
      ok: true
    })
  }
  return Promise.resolve({
    json: () => Promise.resolve([]),
    ok: true
  })
})

// Mock WebSocket
const mockSend = vi.fn()
global.WebSocket = class {
  constructor() {
    this.readyState = 1 // OPEN
    this.send = mockSend
    this.close = vi.fn()
    setTimeout(() => {
      this.onopen && this.onopen()
    }, 0)
  }
}
global.WebSocket.OPEN = 1
global.WebSocket.CONNECTING = 0
global.WebSocket.CLOSING = 2
global.WebSocket.CLOSED = 3

describe('EnhancedChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mockSend
    mockSend.mockClear()
  })

  // ... (render tests omitted for brevity in SearchReplace if unchanged) ...
  
  it('renders New Chat button', () => {
    const wrapper = mount(EnhancedChat)
    const newChatBtn = wrapper.find('button[aria-label="Start a new chat session"]')
    expect(newChatBtn.exists()).toBe(true)
  })

  it('renders Student Profile button', () => {
    const wrapper = mount(EnhancedChat)
    const profileBtn = wrapper.find('button[aria-label="Edit Student Profile"]')
    expect(profileBtn.exists()).toBe(true)
  })

  it('opens new chat modal when clicked', async () => {
    const wrapper = mount(EnhancedChat)
    await wrapper.find('button[aria-label="Start a new chat session"]').trigger('click')
    expect(wrapper.text()).toContain('Start New Session')
  })

  it('input area exists', () => {
    const wrapper = mount(EnhancedChat)
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('sends message on Enter', async () => {
    const wrapper = mount(EnhancedChat)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Hello')
    
    // Trigger Enter
    await textarea.trigger('keydown.enter.exact')
    
    // Wait for debounce (300ms)
    await new Promise(r => setTimeout(r, 350))
    await flushPromises() // Wait for async operations like fetch
    
    // Expect WebSocket send to be called
    expect(global.fetch).toHaveBeenCalled() 
    expect(mockSend).toHaveBeenCalled()
  })

  it('does not send on Shift+Enter', async () => {
    const wrapper = mount(EnhancedChat)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Hello')
    
    await textarea.trigger('keydown.enter.shift')
    
    await new Promise(r => setTimeout(r, 350))
    await flushPromises()
    
    expect(mockSend).not.toHaveBeenCalled()
  })
  
  it('debounces rapid Enter presses', async () => {
    const wrapper = mount(EnhancedChat)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Hello')
    
    // Trigger multiple times quickly
    await textarea.trigger('keydown.enter.exact')
    await textarea.trigger('keydown.enter.exact')
    await textarea.trigger('keydown.enter.exact')
    
    await new Promise(r => setTimeout(r, 350))
    await flushPromises()
    
    // Should only send once
    expect(mockSend).toHaveBeenCalledTimes(1)
  })
})
