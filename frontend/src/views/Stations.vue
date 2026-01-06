<template>
  <div class="stations">
    <div class="page-header">
      <h1>站点评估</h1>
      <p>站点繁忙度评估和角色分析</p>
    </div>
    <div class="content">
      <div class="placeholder">
        <p>站点评估页面 - 开发中</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.stations {
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