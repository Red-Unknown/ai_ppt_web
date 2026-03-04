import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ModernButton from '../components/ui/ModernButton.vue'

describe('ModernButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(ModernButton, {
      slots: {
        default: 'Click Me'
      }
    })
    expect(wrapper.text()).toContain('Click Me')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(ModernButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(ModernButton, {
      props: {
        disabled: true
      }
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })

  it('shows loading spinner when loading is true', () => {
    const wrapper = mount(ModernButton, {
      props: {
        loading: true
      }
    })
    expect(wrapper.find('svg.animate-spin').exists()).toBe(true)
  })

  it('applies variant classes', () => {
    const wrapper = mount(ModernButton, {
      props: {
        variant: 'danger'
      }
    })
    expect(wrapper.classes()).toContain('variant-danger')
  })
})
