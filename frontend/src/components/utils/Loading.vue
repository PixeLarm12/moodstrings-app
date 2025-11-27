<template>
  <div class="text-lg flex justify-center items-center space-x-1 italic">
    <span v-if="!isLyrics">Reading information about&nbsp;<i class="font-semibold">"{{ fileName }}"</i></span>
    <span v-else>Trying to get lyrics from&nbsp;<i class="font-semibold">"{{ fileName }}"</i></span>
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
    isLyrics: {
      type: Boolean,
      default: false
    }
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
