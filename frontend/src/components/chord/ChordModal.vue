<template>
  <div v-if="show" class="text-black fixed inset-0 bg-white/30 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-lg w-96 relative">
      <h2 class="text-xl mb-4">Acorde: <b>{{ chordName }}</b></h2>
      <p class="list-disc pl-5 space-y-1">
        <span v-for="(note, index) in info.notes" :key="index" class="inline-block mr-2">
          {{ note }}
        </span>
      </p>
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
    info: {
      type: Object,
      default: () => []
    },
    chordName: {
      type: String,
      default: ""
    },
    show: {
      type: Boolean,
      default: false
    }
  }
}
</script>
