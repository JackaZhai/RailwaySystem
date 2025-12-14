<template>
  <span class="animated-number" :class="{ 'animate-count-up': animate }">
    {{ formattedValue }}
  </span>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'

interface Props {
  value: number
  duration?: number
  decimals?: number
  prefix?: string
  suffix?: string
  separator?: string
  animate?: boolean
  format?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  duration: 1000,
  decimals: 0,
  prefix: '',
  suffix: '',
  separator: ',',
  animate: true,
  format: true
})

const animatedValue = ref(0)
const animationFrame = ref<number | null>(null)
const startTime = ref<number | null>(null)
const startValue = ref(0)
const endValue = ref(0)

const formattedValue = computed(() => {
  const value = props.animate ? animatedValue.value : props.value
  let formatted = value.toFixed(props.decimals)

  if (props.format) {
    // 添加千位分隔符
    formatted = formatted.replace(/\B(?=(\d{3})+(?!\d))/g, props.separator)
  }

  return `${props.prefix}${formatted}${props.suffix}`
})

const animateValue = (newValue: number) => {
  if (!props.animate) {
    animatedValue.value = newValue
    return
  }

  startValue.value = animatedValue.value
  endValue.value = newValue
  startTime.value = Date.now()

  const animate = () => {
    if (!startTime.value) return

    const now = Date.now()
    const elapsed = now - startTime.value
    const progress = Math.min(elapsed / props.duration, 1)

    // 使用缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    animatedValue.value = startValue.value + (endValue.value - startValue.value) * easeOutQuart

    if (progress < 1) {
      animationFrame.value = requestAnimationFrame(animate)
    } else {
      animatedValue.value = endValue.value
    }
  }

  // 取消之前的动画
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }

  animate()
}

watch(() => props.value, (newValue) => {
  animateValue(newValue)
})

onMounted(() => {
  animateValue(props.value)
})
</script>

<style scoped>
.animated-number {
  display: inline-block;
  font-variant-numeric: tabular-nums;
}

.animate-count-up {
  animation: countUp 0.5s ease-out;
}
</style>