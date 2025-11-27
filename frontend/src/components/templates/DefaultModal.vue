<template>
  <div v-if="show" class="min-w-[40vw] min-h-[40vh] text-black fixed inset-0 bg-white/20 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="min-w-[40vw] max-w-[20vw] min-h-[40vh] text-white bg-gray-800 p-6 rounded-xl shadow-lg shadow-gray-400 relative flex flex-col justify-start">
      <h2 v-if="$slots.header" class="text-xl mb-4">
        <slot name="header"></slot>
      </h2>

      <div class="flex flex-col justify-center">
        <slot></slot>
      </div>

      <button
        @click="$emit('close')"
        class="absolute top-2 right-2 text-xl text-sky-400 font-bold hover:font-bold hover:cursor-pointer"
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
