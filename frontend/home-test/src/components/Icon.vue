<template>
  <svg 
    class="custom-icon"
    :style="iconStyle"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <slot></slot>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  size: {
    type: [Number, String],
    default: 24
  },
  color: {
    type: String,
    default: 'currentColor'
  }
})

// 计算属性
const iconStyle = computed(() => {
  return {
    width: typeof props.size === 'number' ? `${props.size}px` : props.size,
    height: typeof props.size === 'number' ? `${props.size}px` : props.size,
    color: props.color
  }
})
</script>

<style scoped>
.custom-icon {
  display: inline-block;
  vertical-align: middle;
  transition: all 0.2s ease;
}
</style>