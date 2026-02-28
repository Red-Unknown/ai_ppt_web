import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Modal from '../components/ui/Modal.vue'

describe('Modal.vue', () => {
  it('renders correctly when open', () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true },
      slots: { default: 'Content', title: 'Title' }
    })
    expect(wrapper.text()).toContain('Title')
    expect(wrapper.text()).toContain('Content')
    // Use a simpler selector or just check for presence of role="dialog"
    expect(wrapper.find('div[role="dialog"]').exists()).toBe(true)
  })

  it('does not render when closed', () => {
    const wrapper = mount(Modal, {
      props: { isOpen: false }
    })
    expect(wrapper.find('div[role="dialog"]').exists()).toBe(false)
  })

  it('emits close event on backdrop click', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true }
    })
    await wrapper.find('.bg-opacity-75').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  it('emits close event on ESC key', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true },
      attachTo: document.body
    })
    
    await wrapper.trigger('keydown', { key: 'Escape' })
    // Since we listen on document, trigger on document or window
    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    document.dispatchEvent(event)
    
    expect(wrapper.emitted()).toHaveProperty('close')
    wrapper.unmount()
  })
})
