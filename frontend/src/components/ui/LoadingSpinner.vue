<template>
  <div class="loading-spinner" :class="[size, variant, { 'fullscreen': fullscreen }]">
    <div class="spinner-container">
      <!-- 单圈旋转器 -->
      <div class="spinner-ring" :style="ringStyle"></div>

      <!-- 加载文本 -->
      <div v-if="showText" class="loading-text" :class="textSize">
        {{ text }}
      </div>
    </div>

    <!-- 背景遮罩 -->
    <div v-if="fullscreen" class="loading-backdrop"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'small' | 'medium' | 'large' | 'xlarge'
  variant?: 'primary' | 'secondary' | 'accent' | 'light' | 'dark'
  color?: string
  text?: string
  showText?: boolean
  fullscreen?: boolean
  speed?: 'slow' | 'normal' | 'fast'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  variant: 'primary',
  text: '加载中...',
  showText: true,
  fullscreen: false,
  speed: 'normal'
})

const ringStyle = computed(() => {
  const speeds = {
    slow: '2s',
    normal: '1.5s',
    fast: '1s'
  }

  // 如果提供了自定义颜色，使用自定义颜色
  if (props.color) {
    return {
      borderTopColor: props.color,
      animationDuration: speeds[props.speed]
    }
  }

  // 否则根据变体设置颜色
  const colors = {
    primary: 'var(--color-primary)',
    secondary: 'var(--color-secondary)',
    accent: 'var(--color-accent)',
    light: 'var(--color-text-inverse)',
    dark: 'var(--color-text-primary)'
  }

  return {
    borderTopColor: colors[props.variant],
    animationDuration: speeds[props.speed]
  }
})

const textSize = computed(() => {
  const sizes = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
    xlarge: 'text-lg'
  }
  return sizes[props.size]
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: var(--z-index-modal);
}

.loading-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(2px);
}

.spinner-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

/* 旋转器尺寸 */
.loading-spinner.small .spinner-ring {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-spinner.medium .spinner-ring {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading-spinner.large .spinner-ring {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

.loading-spinner.xlarge .spinner-ring {
  width: 80px;
  height: 80px;
  border-width: 5px;
}

/* 旋转器样式 */
.spinner-ring {
  border: 3px solid var(--color-bg-tertiary);
  border-top-color: var(--color-primary); /* 默认颜色，会被变体类覆盖 */
  border-radius: 50%;
  animation: spin linear infinite;
}

/* 不同尺寸的边框调整 */
.loading-spinner.small .spinner-ring {
  border-width: 2px;
}

.loading-spinner.medium .spinner-ring {
  border-width: 3px;
}

.loading-spinner.large .spinner-ring {
  border-width: 4px;
}

.loading-spinner.xlarge .spinner-ring {
  border-width: 5px;
}

/* 变体颜色 */
.loading-spinner.primary .spinner-ring {
  border-top-color: var(--color-primary);
}

.loading-spinner.secondary .spinner-ring {
  border-top-color: var(--color-secondary);
}

.loading-spinner.accent .spinner-ring {
  border-top-color: var(--color-accent);
}

.loading-spinner.light .spinner-ring {
  border-top-color: var(--color-text-inverse);
}

.loading-spinner.dark .spinner-ring {
  border-top-color: var(--color-text-primary);
}

/* 加载文本 */
.loading-text {
  margin-top: var(--spacing-3);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

.loading-text.text-xs {
  font-size: var(--font-size-xs);
}

.loading-text.text-sm {
  font-size: var(--font-size-sm);
}

.loading-text.text-base {
  font-size: var(--font-size-base);
}

.loading-text.text-lg {
  font-size: var(--font-size-lg);
}

/* 动画关键帧 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 脉冲动画变体 */
.loading-spinner.pulse .spinner-ring {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

/* 波浪动画变体 */
.loading-spinner.wave .spinner-ring {
  animation: wave 1.5s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% {
    border-radius: 50%;
    transform: rotate(0deg);
  }
  25% {
    border-radius: 40% 60% 60% 40%;
  }
  50% {
    border-radius: 60% 40% 40% 60%;
  }
  75% {
    border-radius: 40% 60% 60% 40%;
  }
}
</style>