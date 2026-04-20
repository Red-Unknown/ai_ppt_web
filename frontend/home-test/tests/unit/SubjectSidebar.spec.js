import { mount } from '@vue/test-utils'
import SubjectSidebar from '@/components/SubjectSidebar.vue'

describe('SubjectSidebar', () => {
  const mockSubjects = [
    { id: 'subject_1', name: '数学' },
    { id: 'subject_2', name: '语文' },
    { id: 'subject_3', name: '英语' }
  ]

  describe('渲染测试', () => {
    it('应该正确渲染科目列表', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1'
        }
      })
      
      expect(wrapper.findAll('.subject-item')).toHaveLength(3)
      expect(wrapper.text()).toContain('数学')
      expect(wrapper.text()).toContain('语文')
      expect(wrapper.text()).toContain('英语')
    })

    it('应该正确显示标题', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1'
        }
      })
      
      expect(wrapper.find('.sidebar-title').text()).toBe('科目')
    })

    it('应该正确高亮选中的科目', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_2'
        }
      })
      
      const selectedItem = wrapper.findAll('.subject-item')[1]
      expect(selectedItem.classes()).toContain('selected')
    })
  })

  describe('主题切换测试', () => {
    it('应该正确应用蓝色主题（教师端）', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1',
          theme: 'blue'
        }
      })
      
      expect(wrapper.classes()).toContain('theme-blue')
      expect(wrapper.classes()).not.toContain('theme-orange')
    })

    it('应该正确应用橙色主题（学生端）', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1',
          theme: 'orange'
        }
      })
      
      expect(wrapper.classes()).toContain('theme-orange')
      expect(wrapper.classes()).not.toContain('theme-blue')
    })

    it('蓝色主题下应该显示操作按钮', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1',
          theme: 'blue'
        }
      })
      
      expect(wrapper.find('.title-actions').exists()).toBe(true)
    })

    it('橙色主题下不应该显示操作按钮', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1',
          theme: 'orange'
        }
      })
      
      expect(wrapper.find('.title-actions').exists()).toBe(false)
    })
  })

  describe('交互功能测试', () => {
    it('点击科目应该触发 select 事件', async () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: mockSubjects,
          selectedSubject: 'subject_1'
        }
      })
      
      const secondSubject = wrapper.findAll('.subject-item')[1]
      await secondSubject.trigger('click')
      
      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')[0][0]).toEqual(mockSubjects[1])
    })

    it('空科目列表应该正常显示', () => {
      const wrapper = mount(SubjectSidebar, {
        props: {
          subjects: [],
          selectedSubject: ''
        }
      })
      
      expect(wrapper.findAll('.subject-item')).toHaveLength(0)
    })
  })
})
