import { mount } from '@vue/test-utils'
import ChapterSidebar from '@/components/ChapterSidebar.vue'

describe('ChapterSidebar', () => {
  const mockChapters = [
    { id: 'chapter_1', name: '第一章' },
    { id: 'chapter_2', name: '第二章' },
    { id: 'chapter_3', name: '第三章' }
  ]

  describe('渲染测试', () => {
    it('应该正确渲染章节列表', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1'
        }
      })
      
      expect(wrapper.findAll('.chapter-item')).toHaveLength(3)
      expect(wrapper.text()).toContain('第一章')
      expect(wrapper.text()).toContain('第二章')
      expect(wrapper.text()).toContain('第三章')
    })

    it('应该正确显示标题', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1'
        }
      })
      
      expect(wrapper.find('.sidebar-title').text()).toBe('章节')
    })

    it('应该正确高亮选中的章节', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_2'
        }
      })
      
      const selectedItem = wrapper.findAll('.chapter-item')[1]
      expect(selectedItem.classes()).toContain('selected')
    })
  })

  describe('主题切换测试', () => {
    it('应该正确应用蓝色主题（教师端）', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1',
          theme: 'blue'
        }
      })
      
      expect(wrapper.classes()).toContain('theme-blue')
      expect(wrapper.classes()).not.toContain('theme-orange')
    })

    it('应该正确应用橙色主题（学生端）', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1',
          theme: 'orange'
        }
      })
      
      expect(wrapper.classes()).toContain('theme-orange')
      expect(wrapper.classes()).not.toContain('theme-blue')
    })

    it('蓝色主题下应该显示操作按钮', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1',
          theme: 'blue'
        }
      })
      
      expect(wrapper.find('.title-actions').exists()).toBe(true)
    })

    it('橙色主题下不应该显示操作按钮', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1',
          theme: 'orange'
        }
      })
      
      expect(wrapper.find('.title-actions').exists()).toBe(false)
    })
  })

  describe('交互功能测试', () => {
    it('点击章节应该触发 select 事件', async () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: mockChapters,
          selectedChapter: 'chapter_1'
        }
      })
      
      const secondChapter = wrapper.findAll('.chapter-item')[1]
      await secondChapter.trigger('click')
      
      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')[0][0]).toEqual(mockChapters[1])
    })

    it('空章节列表应该正常显示', () => {
      const wrapper = mount(ChapterSidebar, {
        props: {
          chapters: [],
          selectedChapter: ''
        }
      })
      
      expect(wrapper.findAll('.chapter-item')).toHaveLength(0)
    })
  })
})
