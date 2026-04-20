<template>
  <button 
    class="base-button"
    :class="[
      `button-${type}`,
      `button-${size}`,
      { 'button-disabled': disabled },
      { 'button-icon-only': iconOnly }
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

/**
 * 基础按钮组件
 * @description 支持多种类型、尺寸和主题的通用按钮
 * @example
 * <BaseButton type="primary" size="medium">点击我</BaseButton>
 */

// Props
const props = defineProps({
  /**
   * 按钮类型
   * @type {'primary' | 'secondary' | 'outline' | 'text'}
   * @default 'primary'
   */
  type: {
    type: String,
    default: 'primary',
    validator: (value) => {
      const validTypes = ['primary', 'secondary', 'outline', 'text']
      if (!validTypes.includes(value)) {
        console.warn(`[BaseButton] Invalid type: "${value}". Must be one of: ${validTypes.join(', ')}`)
        return false
      }
      return true
    }
  },
  /**
   * 按钮尺寸
   * @type {'small' | 'medium' | 'large'}
   * @default 'medium'
   */
  size: {
    type: String,
    default: 'medium',
    validator: (value) => {
      const validSizes = ['small', 'medium', 'large']
      if (!validSizes.includes(value)) {
        console.warn(`[BaseButton] Invalid size: "${value}". Must be one of: ${validSizes.join(', ')}`)
        return false
      }
      return true
    }
  },
  /**
   * 是否禁用按钮
   * @type {boolean}
   * @default false
   */
  disabled: {
    type: Boolean,
    default: false
  },
  /**
   * 是否仅显示图标
   * @type {boolean}
   * @default false
   */
  iconOnly: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['click'])

/**
 * 点击事件处理
 * @param {Event} event - 点击事件对象
 */
const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button {
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 按钮类型 */
.button-primary {
  background: var(--theme-secondary);
  color: white;
}

.button-primary:hover:not(.button-disabled) {
  background: var(--theme-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.button-secondary {
  background: var(--theme-primary-mix-5);
  color: var(--theme-secondary);
  border: 1px solid var(--theme-primary-mix-10);
}

.button-secondary:hover:not(.button-disabled) {
  background: var(--theme-primary-mix-10);
  transform: translateY(-1px);
}

.button-outline {
  background: white;
  color: var(--theme-secondary);
  border: 1px solid var(--theme-secondary);
}

.button-outline:hover:not(.button-disabled) {
  background: var(--theme-primary-mix-5);
  transform: translateY(-1px);
}

.button-text {
  background: transparent;
  color: var(--theme-secondary);
  border: none;
}

.button-text:hover:not(.button-disabled) {
  background: var(--theme-primary-opacity-20);
  transform: translateY(-1px);
}

/* 按钮尺寸 */
.button-small {
  padding: 6px 12px;
  font-size: 12px;
}

.button-medium {
  padding: 8px 16px;
  font-size: 14px;
}

.button-large {
  padding: 10px 20px;
  font-size: 16px;
}

/* 图标按钮 */
.button-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
}

.button-icon-only.button-small {
  width: 24px;
  height: 24px;
}

.button-icon-only.button-large {
  width: 40px;
  height: 40px;
}

/* 禁用状态 */
.button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}
</style>