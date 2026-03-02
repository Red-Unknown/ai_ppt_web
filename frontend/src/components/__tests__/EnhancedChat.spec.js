import { mount } from '@vue/test-utils'
import EnhancedChat from '../EnhancedChat.vue'
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('EnhancedChat.vue', () => {
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
})
