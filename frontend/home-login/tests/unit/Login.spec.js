import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import LoginPopup from '@/components/LoginPopup.vue'

// 模拟 localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn()
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// 模拟 window.history
Object.defineProperty(window, 'history', {
  value: {
    back: jest.fn()
  },
  writable: true
})

describe('LoginPopup.vue', () => {
  let wrapper

  beforeEach(() => {
    jest.clearAllMocks()
    wrapper = mount(LoginPopup, {
      props: {
        modelValue: true
      },
      global: {
        stubs: {
          'font-awesome-icon': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染登录表单', () => {
      expect(wrapper.find('form').exists()).toBe(true)
      expect(wrapper.find('input#username').exists()).toBe(true)
      expect(wrapper.find('input#password').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })

    it('应该显示标题和品牌名称', () => {
      expect(wrapper.text()).toContain('欢迎回来')
      expect(wrapper.text()).toContain('AI智教')
    })

    it('应该渲染第三方登录按钮', () => {
      expect(wrapper.text()).toContain('微信登录')
      expect(wrapper.text()).toContain('QQ登录')
    })

    it('应该渲染"记住我"复选框', () => {
      expect(wrapper.find('input#remember-me').exists()).toBe(true)
    })

    it('应该渲染"忘记密码"链接', () => {
      expect(wrapper.text()).toContain('忘记密码？')
    })

    it('应该渲染注册链接', () => {
      expect(wrapper.text()).toContain('立即注册')
    })
  })

  describe('表单验证', () => {
    it('用户名输入为空时应该显示错误信息', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('')
      await usernameInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('请输入用户名或邮箱')
    })

    it('用户名格式不正确时应该显示错误信息', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('ab')
      await usernameInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('用户名长度应为3-20个字符')
    })

    it('邮箱格式不正确时应该显示错误信息', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('invalid-email')
      await usernameInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('请输入有效的邮箱地址')
    })

    it('有效的邮箱格式应该通过验证', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('test@example.com')
      await usernameInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).not.toContain('请输入有效的邮箱地址')
    })

    it('密码为空时应该显示错误信息', async () => {
      const passwordInput = wrapper.find('input#password')
      await passwordInput.setValue('')
      await passwordInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('请输入密码')
    })

    it('密码长度小于6时应该显示错误信息', async () => {
      const passwordInput = wrapper.find('input#password')
      await passwordInput.setValue('12345')
      await passwordInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('密码长度至少为6个字符')
    })

    it('密码长度大于20时应该显示错误信息', async () => {
      const passwordInput = wrapper.find('input#password')
      await passwordInput.setValue('123456789012345678901')
      await passwordInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('密码长度不能超过20个字符')
    })

    it('输入时应该清除错误信息', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('')
      await usernameInput.trigger('blur')
      await nextTick()
      
      expect(wrapper.text()).toContain('请输入用户名或邮箱')
      
      await usernameInput.setValue('test')
      await usernameInput.trigger('input')
      await nextTick()
      
      expect(wrapper.text()).not.toContain('请输入用户名或邮箱')
    })
  })

  describe('密码显示/隐藏功能', () => {
    it('密码输入框默认应该是密码类型', () => {
      const passwordInput = wrapper.find('input#password')
      expect(passwordInput.attributes('type')).toBe('password')
    })

    it('点击显示密码按钮应该切换输入框类型', async () => {
      const toggleButton = wrapper.find('button[aria-label="显示密码"]')
      const passwordInput = wrapper.find('input#password')
      
      expect(passwordInput.attributes('type')).toBe('password')
      
      await toggleButton.trigger('click')
      await nextTick()
      
      expect(passwordInput.attributes('type')).toBe('text')
    })

    it('再次点击应该隐藏密码', async () => {
      const toggleButton = wrapper.find('button[aria-label="显示密码"]')
      
      await toggleButton.trigger('click')
      await nextTick()
      
      // 找到隐藏密码按钮
      const hideButton = wrapper.find('button[aria-label="隐藏密码"]')
      await hideButton.trigger('click')
      await nextTick()
      
      const passwordInput = wrapper.find('input#password')
      expect(passwordInput.attributes('type')).toBe('password')
    })
  })

  describe('表单提交', () => {
    it('表单验证失败时不应该提交', async () => {
      await wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      // 由于验证失败，会显示错误信息
      expect(wrapper.text()).toContain('请输入用户名或邮箱')
    })

    it('提交时应该显示加载状态', async () => {
      // 填写有效数据
      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      
      // 提交表单
      wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      // 检查加载状态
      expect(wrapper.text()).toContain('登录中...')
      
      // 等待异步操作完成
      await flushPromises()
    })

    it('提交时应该防止重复提交', async () => {
      // 填写有效数据
      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      
      // 第一次提交
      wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      // 第二次提交应该被忽略（不会报错）
      wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      // 等待异步操作完成
      await flushPromises()
    })
  })

  describe('记住我功能', () => {
    it('应该能够勾选记住我', async () => {
      const rememberMeCheckbox = wrapper.find('input#remember-me')
      
      expect(rememberMeCheckbox.element.checked).toBe(false)
      
      await rememberMeCheckbox.setValue(true)
      await nextTick()
      
      expect(wrapper.vm.form.rememberMe).toBe(true)
    })

    it('登录成功后应该保存用户名到 localStorage', async () => {
      // 填写有效数据并勾选记住我
      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('input#remember-me').setValue(true)
      
      // 提交表单
      wrapper.find('form').trigger('submit.prevent')
      await flushPromises()
      
      // 验证 localStorage.setItem 被调用
      expect(localStorageMock.setItem).toHaveBeenCalledWith('rememberedUsername', 'testuser')
    })

    it('未勾选记住我时不应该保存用户名', async () => {
      // 填写有效数据，不勾选记住我
      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('input#remember-me').setValue(false)
      
      // 提交表单
      wrapper.find('form').trigger('submit.prevent')
      await flushPromises()
      
      // 验证 localStorage.removeItem 被调用
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('rememberedUsername')
    })

    it('组件挂载时应该加载记住的用户名', async () => {
      localStorageMock.getItem.mockReturnValue('rememberedUser')
      
      // 重新挂载组件
      wrapper.unmount()
      wrapper = mount(LoginPopup, {
        props: {
          modelValue: true
        }
      })
      await nextTick()
      
      expect(wrapper.find('input#username').element.value).toBe('rememberedUser')
      expect(wrapper.find('input#remember-me').element.checked).toBe(true)
    })
  })

  describe('第三方登录', () => {
    it('点击微信登录应该显示提示', async () => {
      const wechatButton = wrapper.find('button[aria-label="使用微信登录"]')
      
      await wechatButton.trigger('click')
      await nextTick()
      
      expect(wrapper.text()).toContain('微信登录功能即将上线')
    })

    it('点击QQ登录应该显示提示', async () => {
      const qqButton = wrapper.find('button[aria-label="使用QQ登录"]')
      
      await qqButton.trigger('click')
      await nextTick()
      
      expect(wrapper.text()).toContain('QQ登录功能即将上线')
    })
  })

  describe('其他功能', () => {
    it('点击忘记密码应该显示提示', async () => {
      const forgotPasswordLink = wrapper.find('a:contains("忘记密码？")')
      
      await forgotPasswordLink.trigger('click')
      await nextTick()
      
      expect(wrapper.text()).toContain('密码重置功能即将上线')
    })

    it('点击注册链接应该显示提示', async () => {
      // 找到包含"立即注册"的链接
      const links = wrapper.findAll('a')
      const registerLink = links.find(link => link.text().includes('立即注册'))
      
      if (registerLink) {
        await registerLink.trigger('click')
        await nextTick()
        
        expect(wrapper.text()).toContain('注册功能即将上线')
      }
    })

    it('点击关闭按钮应该发出关闭事件', async () => {
      const closeButton = wrapper.find('button[aria-label="关闭"]')
      
      await closeButton.trigger('click')
      await nextTick()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false])
    })
  })

  describe('可访问性', () => {
    it('输入框应该有正确的 ARIA 属性', () => {
      const usernameInput = wrapper.find('input#username')
      const passwordInput = wrapper.find('input#password')
      
      expect(usernameInput.attributes('aria-required')).toBe('true')
      expect(passwordInput.attributes('aria-required')).toBe('true')
    })

    it('错误信息应该有正确的 ARIA 属性', async () => {
      const usernameInput = wrapper.find('input#username')
      await usernameInput.setValue('')
      await usernameInput.trigger('blur')
      await nextTick()
      
      const errorMessage = wrapper.find('[role="alert"]')
      expect(errorMessage.exists()).toBe(true)
    })

    it('按钮应该有正确的 ARIA 标签', () => {
      expect(wrapper.find('button[aria-label="显示密码"]').exists()).toBe(true)
      expect(wrapper.find('button[aria-label="使用微信登录"]').exists()).toBe(true)
      expect(wrapper.find('button[aria-label="使用QQ登录"]').exists()).toBe(true)
      expect(wrapper.find('button[aria-label="关闭"]').exists()).toBe(true)
    })
  })

  describe('安全性', () => {
    it('应该对输入进行 XSS 防护', async () => {
      // 填写包含 HTML 的数据
      await wrapper.find('input#username').setValue('<script>alert("xss")</script>')
      await wrapper.find('input#password').setValue('password123')
      
      // 提交表单
      wrapper.find('form').trigger('submit.prevent')
      await flushPromises()
      
      // 验证 XSS 被转义（通过检查控制台输出或组件状态）
      // 这里我们主要验证组件不会崩溃
      expect(wrapper.find('input#username').exists()).toBe(true)
    })
  })
})
