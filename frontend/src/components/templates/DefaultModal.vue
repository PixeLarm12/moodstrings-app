<template>
  <div v-if="show" class="text-black fixed inset-0 bg-white/30 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-lg w-96 relative">
      
      <h2 v-if="$slots.header" class="text-xl mb-4">
        <slot name="header"></slot>
      </h2>

      <div>
        <slot></slot>
      </div>

      <button
        @click="$emit('close')"
        class="absolute top-2 right-2 text-gray-700 hover:font-bold hover:cursor-pointer"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: {
      type: Boolean,
      default: false
    }
  }
}
</script>
