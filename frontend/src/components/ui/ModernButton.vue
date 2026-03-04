<template>
  <button
    :class="[
      'modern-button',
      `variant-${variant}`,
      `size-${size}`,
      { 'w-full': block, 'is-loading': loading, 'is-disabled': disabled }
    ]"
    :disabled="disabled || loading"
    :aria-busy="loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner">
      <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <span v-else-if="$slots.icon" class="icon">
      <slot name="icon"></slot>
    </span>
    <span :class="{ 'ml-2': loading || $slots.icon }">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'ghost', 'outline'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>

<style scoped>
.modern-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.modern-button:disabled,
.modern-button.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Sizes */
.size-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  height: 2rem;
}

.size-md {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  height: 2.5rem;
}

.size-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
  height: 3rem;
}

/* Variants */
.variant-primary {
  background-color: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-sm);
}
.variant-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
  box-shadow: var(--shadow-md);
}

.variant-secondary {
  background-color: var(--secondary-color);
  color: white;
  box-shadow: var(--shadow-sm);
}
.variant-secondary:hover:not(:disabled) {
  background-color: var(--secondary-hover);
  box-shadow: var(--shadow-md);
}

.variant-danger {
  background-color: var(--danger-color);
  color: white;
}
.variant-danger:hover:not(:disabled) {
  background-color: var(--danger-hover);
}

.variant-ghost {
  background-color: transparent;
  color: var(--text-secondary);
}
.variant-ghost:hover:not(:disabled) {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-color);
}

.variant-outline {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--text-color);
}
.variant-outline:hover:not(:disabled) {
  background-color: var(--bg-color);
  border-color: var(--text-secondary);
}

.spinner {
  display: flex;
  align-items: center;
}

.icon {
  display: flex;
  align-items: center;
  margin-right: 0.5rem;
}
</style>
