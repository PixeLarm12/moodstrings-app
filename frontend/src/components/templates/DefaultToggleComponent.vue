<template>
  <div class="w-full">
    <div
      @click="toggle"
      class="flex justify-between items-center px-4 py-3 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors border border-sky-500"
    >
      <h3 class="font-semibold">
        <slot name="header"></slot>
      </h3>

      <svg
        :class="['w-5 h-5 transition-transform duration-300', { 'rotate-180': isOpen }]"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    </div>

    <transition name="slide-fade">
      <div v-if="isOpen" class="border border-t-0 border-gray-700 rounded-b-lg p-4">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: "DefaultToggleComponent",
  data() {
    return {
      isOpen: false,
    };
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen;
    },
  },
};
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
