export const mockBboxService = {
  bboxes: [
    {
      id: 'bbox_1',
      slideIndex: 0,
      pageNum: 13,
      bbox: {
        x: 100,
        y: 150,
        width: 300,
        height: 200
      },
      content: '胡克定律 - 描述材料在弹性范围内应力与应变关系的定律',
      relevanceScore: 0.85
    },
    {
      id: 'bbox_2',
      slideIndex: 0,
      pageNum: 13,
      bbox: {
        x: 450,
        y: 180,
        width: 280,
        height: 150
      },
      content: '胡克定律公式：σ = E·ε',
      relevanceScore: 0.82
    },
    {
      id: 'bbox_3',
      slideIndex: 0,
      pageNum: 12,
      bbox: {
        x: 80,
        y: 120,
        width: 350,
        height: 180
      },
      content: '纵向变形：构件在轴向力作用下，其长度发生改变',
      relevanceScore: 0.78
    },
    {
      id: 'bbox_4',
      slideIndex: 1,
      pageNum: 10,
      bbox: {
        x: 120,
        y: 200,
        width: 400,
        height: 160
      },
      content: '正应力均匀分布 - 横截面上各点的正应力是均匀分布的',
      relevanceScore: 0.75
    }
  ],

  getBboxesForAnswer(answerContent) {
    if (!answerContent) return []

    const keywords = ['胡克定律', '弹性', '应力', '应变', '变形', '正应力']
    const matchedBboxes = []

    for (const bbox of this.bboxes) {
      for (const keyword of keywords) {
        if (answerContent.includes(keyword) || bbox.content.includes(keyword)) {
          matchedBboxes.push(bbox)
          break
        }
      }
    }

    return matchedBboxes.length > 0 ? matchedBboxes : this.bboxes.slice(0, 2)
  },

  getBboxById(id) {
    return this.bboxes.find(bbox => bbox.id === id)
  },

  getBboxesBySlideIndex(slideIndex) {
    return this.bboxes.filter(bbox => bbox.slideIndex === slideIndex)
  }
}

export default mockBboxService