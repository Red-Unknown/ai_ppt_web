import { mount } from '@vue/test-utils'
import BaseButton from '@/components/BaseButton.vue'

describe('BaseButton', () => {
  describe('渲染测试', () => {
    it('应该正确渲染按钮', () => {
      const wrapper = mount(BaseButton, {
        slots: {
          default: '点击我'
        }
      })
      expect(wrapper.text()).toBe('点击我')
      expect(wrapper.classes()).toContain('base-button')
    })

    it('应该正确渲染默认类型（primary）', () => {
      const wrapper = mount(BaseButton)
      expect(wrapper.classes()).toContain('button-primary')
    })
  })

  describe('Props 测试', () => {
    it('应该正确应用不同的按钮类型', () => {
      const types = ['primary', 'secondary', 'outline', 'text']
      
      types.forEach(type => {
        const wrapper = mount(BaseButton, {
          props: { type }
        })
        expect(wrapper.classes()).toContain(`button-${type}`)
      })
    })

    it('应该正确应用不同的尺寸', () => {
      const sizes = ['small', 'medium', 'large']
      
      sizes.forEach(size => {
        const wrapper = mount(BaseButton, {
          props: { size }
        })
        expect(wrapper.classes()).toContain(`button-${size}`)
      })
    })

    it('应该正确禁用按钮', () => {
      const wrapper = mount(BaseButton, {
        props: { disabled: true }
      })
      expect(wrapper.classes()).toContain('button-disabled')
      expect(wrapper.attributes('disabled')).toBeDefined()
    })

    it('应该正确应用图标按钮样式', () => {
      const wrapper = mount(BaseButton, {
        props: { iconOnly: true }
      })
      expect(wrapper.classes()).toContain('button-icon-only')
    })
  })

  describe('事件测试', () => {
    it('点击按钮应该触发 click 事件', async () => {
      const wrapper = mount(BaseButton, {
        slots: {
          default: '点击我'
        }
      })
      
      await wrapper.trigger('click')
      expect(wrapper.emitted('click')).toHaveLength(1)
    })

    it('禁用状态下点击不应该触发事件', async () => {
      const wrapper = mount(BaseButton, {
        props: { disabled: true },
        slots: {
          default: '点击我'
        }
      })
      
      await wrapper.trigger('click')
      expect(wrapper.emitted('click')).toBeUndefined()
    })
  })
})
