<template>
  <div class="analytics">
    <div class="page-header">
      <h1>客流分析</h1>
      <p>客流统计、时空分布和预测分析</p>
    </div>
    <div class="content">
      <div class="placeholder">
        <p>客流分析页面 - 开发中</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.analytics {
  padding: var(--spacing-4);
}

.page-header {
  margin-bottom: var(--spacing-6);
}

.page-header h1 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--spacing-2);
}

.page-header p {
  color: var(--color-text-secondary);
}

.placeholder {
  text-align: center;
  padding: var(--spacing-12);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
}
</style>