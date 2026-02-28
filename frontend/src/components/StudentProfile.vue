<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
      <div class="sm:col-span-6">
        <label for="learning_style" class="block text-sm font-medium text-gray-700">Learning Style</label>
        <div class="mt-1">
          <select id="learning_style" v-model="profile.learning_style" class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md">
            <option value="visual">Visual (Charts, Graphs)</option>
            <option value="auditory">Auditory (Listening, Discussing)</option>
            <option value="kinesthetic">Kinesthetic (Hands-on, Examples)</option>
          </select>
        </div>
      </div>

      <div class="sm:col-span-6">
        <label for="knowledge_level" class="block text-sm font-medium text-gray-700">Knowledge Level</label>
        <div class="mt-1">
          <select id="knowledge_level" v-model="profile.knowledge_level" class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md">
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div class="sm:col-span-6">
        <label for="interests" class="block text-sm font-medium text-gray-700">Interests (comma separated)</label>
        <div class="mt-1">
          <input type="text" id="interests" v-model="interestsInput" class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md" placeholder="Physics, Math, AI">
        </div>
      </div>
    </div>
    
    <div class="flex justify-end gap-3 mt-4">
      <ModernButton variant="secondary" :loading="saving" @click="saveProfile">Save Profile</ModernButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import ModernButton from './ui/ModernButton.vue'

const profile = ref({
  learning_style: 'visual',
  knowledge_level: 'beginner',
  interests: []
})
const interestsInput = ref('')
const loading = ref(false)
const saving = ref(false)

onMounted(async () => {
  await fetchProfile()
})

async function fetchProfile() {
  loading.value = true
  try {
    const res = await fetch('/api/v1/student/profile')
    if (res.ok) {
      const data = await res.json()
      profile.value = data
      interestsInput.value = data.interests.join(', ')
    }
  } catch (e) {
    console.error('Failed to load profile', e)
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const interests = interestsInput.value.split(',').map(s => s.trim()).filter(Boolean)
    const payload = { ...profile.value, interests }
    
    const res = await fetch('/api/v1/student/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      alert('Profile saved!')
    }
  } catch (e) {
    console.error('Failed to save profile', e)
    alert('Error saving profile')
  } finally {
    saving.value = false
  }
}
</script>
