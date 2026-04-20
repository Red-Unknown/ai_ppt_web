<template>
  <div class="loading-state">
    <div class="loading-content">
      <div class="loading-icon" v-if="type === 'loading'">
        <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 6v6l4 2"></path>
        </svg>
      </div>
      <div class="loading-icon" v-else-if="type === 'empty'">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
        </svg>
      </div>
      <div class="loading-icon" v-else-if="type === 'error'">
        <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      </div>
      <div class="loading-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  type: {
    type: String,
    default: 'loading',
    validator: (value) => ['loading', 'empty', 'error'].includes(value)
  },
  text: {
    type: String,
    default: '正在解析PPT...'
  }
})
</script>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  background: #f8f9fa;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  text-align: center;
}

.loading-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #f0f8ff;
}

.spinner {
  width: 32px;
  height: 32px;
  color: #276884;
  animation: spin 1s linear infinite;
}

.empty-icon {
  width: 32px;
  height: 32px;
  color: #90caf9;
}

.error-icon {
  width: 32px;
  height: 32px;
  color: #f44336;
}

.loading-text {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  line-height: 1.5;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>