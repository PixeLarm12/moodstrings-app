<template>
  <div class="text-lg flex justify-center items-center space-x-1 italic">
    Lendo informações de <i class="font-semibold"> "{{ fileName }}"</i>
    <span class="dot-animate">.</span>
    <span class="dot-animate" style="animation-delay: 0.2s">.</span>
    <span class="dot-animate" style="animation-delay: 0.4s">.</span>
  </div>
</template>

<script>
export default {
  props: {
    fileName: {
      type: String,
      default: ""
    },
  }
}
</script>

<style scoped>
.dot-animate {
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}
</style>
