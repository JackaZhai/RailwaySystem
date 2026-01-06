<template>
  <div class="data-management-simple">
    <h1>数据管理 - 简化测试版</h1>
    <p>如果这个页面能显示，说明Vue和路由工作正常</p>

    <div class="test-section">
      <h2>测试1: 基本HTML</h2>
      <p>这是一个段落</p>
      <button @click="testClick">点击测试</button>
      <p>点击次数: {{ clickCount }}</p>
    </div>

    <div class="test-section">
      <h2>测试2: API调用</h2>
      <button @click="testApi" :disabled="loading">测试API</button>
      <div v-if="apiResult">
        <p>API响应: {{ apiResult }}</p>
      </div>
      <div v-if="apiError">
        <p style="color: red">API错误: {{ apiError }}</p>
      </div>
    </div>

    <div class="test-section">
      <h2>测试3: 回到原页面</h2>
      <button @click="goBack">返回原数据管理页面</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { dataService } from '@/services/api'

const router = useRouter()
const clickCount = ref(0)
const loading = ref(false)
const apiResult = ref<any>(null)
const apiError = ref<string>('')

const testClick = () => {
  clickCount.value++
  console.log('按钮被点击:', clickCount.value)
}

const testApi = async () => {
  loading.value = true
  apiResult.value = null
  apiError.value = ''

  try {
    console.log('开始测试API...')
    const result = await dataService.getDataStats()
    console.log('API响应:', result)
    apiResult.value = result
  } catch (error) {
    console.error('API错误:', error)
    apiError.value = (error as Error).message
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/data')
}
</script>

<style scoped>
.data-management-simple {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.test-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  margin: 5px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #0056b3;
}
</style>