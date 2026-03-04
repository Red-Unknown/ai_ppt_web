import { mount } from '@vue/test-utils'
import EnhancedChat from '../EnhancedChat.vue'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock global fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url
    this.readyState = 1 // OPEN
    setTimeout(() => {
      this.onopen && this.onopen()
    }, 0)
  }
  send(data) {}
  close() {
    this.onclose && this.onclose()
  }
}
global.WebSocket = MockWebSocket

describe('EnhancedChat.vue', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    // Default mock response for sessions
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ([])
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders thinking block when reasoning starts', async () => {
    const wrapper = mount(EnhancedChat, {
      global: {
        stubs: ['ModernButton', 'Modal']
      }
    })
    
    // Initial message setup
    wrapper.vm.messages = [{
        role: 'assistant',
        content: '',
        reasoning: '',
        isReasoningOpen: true
    }]
    
    // Simulate WebSocket message
    wrapper.vm.handleWSMessage({
      type: 'reasoning',
      content: 'Thinking...'
    })
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Thinking Process')
    // Check if details is open
    // Since isReasoningOpen is true, details should have open attribute
    // But testing details open attribute is tricky in JSDOM sometimes
    const lastMsg = wrapper.vm.messages[wrapper.vm.messages.length - 1]
    expect(lastMsg.reasoning).toBe('Thinking...')
  })

  it('collapses thinking block after reasoning ends', async () => {
    vi.useFakeTimers()
    
    const wrapper = mount(EnhancedChat, {
        global: {
          stubs: ['ModernButton', 'Modal']
        }
      })
      
      // Initial message setup
      wrapper.vm.messages = [{
          role: 'assistant',
          content: '',
          reasoning: 'Thinking...',
          isReasoningOpen: true,
          status: 'thinking'
      }]
      
      // Simulate end
      wrapper.vm.handleWSMessage({ type: 'reasoning_end' })
      
      // Fast-forward 500ms
      vi.advanceTimersByTime(500)
      await wrapper.vm.$nextTick()
      
      const lastMsg = wrapper.vm.messages[wrapper.vm.messages.length - 1]
      expect(lastMsg.isReasoningOpen).toBe(false)
      expect(lastMsg.status).toBe('reasoning_complete')
      
      vi.useRealTimers()
  })

  it('renders suggestions when enabled', async () => {
    const wrapper = mount(EnhancedChat, {
      global: { stubs: ['ModernButton', 'Modal'] }
    })
    
    // Enable suggestions
    wrapper.vm.enableSuggestions = true
    
    // Add message with suggestions
    wrapper.vm.messages = [{
      role: 'assistant',
      content: 'Hello',
      suggestions: ['Question 1', 'Question 2']
    }]
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Suggested Follow-up')
    expect(wrapper.text()).toContain('Question 1')
    expect(wrapper.text()).toContain('Question 2')
  })

  it('hides suggestions when disabled', async () => {
    const wrapper = mount(EnhancedChat, {
      global: { stubs: ['ModernButton', 'Modal'] }
    })
    
    // Disable suggestions
    wrapper.vm.enableSuggestions = false
    
    // Add message with suggestions
    wrapper.vm.messages = [{
      role: 'assistant',
      content: 'Hello',
      suggestions: ['Question 1', 'Question 2']
    }]
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).not.toContain('Suggested Follow-up')
    expect(wrapper.text()).not.toContain('Question 1')
  })

  it('triggers shortcut on Alt+Number', async () => {
    const wrapper = mount(EnhancedChat, {
      global: { stubs: ['ModernButton', 'Modal'] }
    })
    
    // Spy on sendMessage - verify exposed method or internal method
    // Since we can't easily spy on internal setup functions directly without exposing them,
    // we can check if the toast appears or if inputQuery changes if sendMessage fails (but sendMessage is mocked).
    // Actually, triggerShortcut calls sendMessage. 
    // Let's rely on the side effect: showToast should be true.
    
    // Reset toast
    wrapper.vm.showToast = false
    
    // Find textarea
    const textarea = wrapper.find('textarea')
    
    // Trigger Alt+1
    await textarea.trigger('keydown', {
      key: '1',
      altKey: true
    })
    
    expect(wrapper.vm.showToast).toBe(true)
    expect(wrapper.vm.toastMessage).toContain('Sending:')
  })
})
