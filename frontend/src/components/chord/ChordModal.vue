<template>
  <div v-if="show" class="text-black fixed inset-0 bg-white/30 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-lg w-96 relative">
      <h2 class="text-xl mb-4">Acorde: <b>{{ chordName }}</b></h2>

      <h3 class="text-xl mb-4">Notas que o compõe: </h3>

      <p class="list-disc space-y-1">
        <ul v-for="(note, index) in notes" :key="index" class="mr-2 list-none">
          <li>{{ note }}</li>
        </ul>
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
    notes: {
      type: Array,
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
