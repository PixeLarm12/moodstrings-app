<template>
  <div class="text-lg font-semibold flex items-center space-x-1">
    <span class="text-blue-700">Carregando</span>
    <span class="dot-animate">.</span>
    <span class="dot-animate" style="animation-delay: 0.2s">.</span>
    <span class="dot-animate" style="animation-delay: 0.4s">.</span>
  </div>
</template>

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
