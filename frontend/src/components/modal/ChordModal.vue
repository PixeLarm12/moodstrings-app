<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      <h1 class="text-2xl text-sky-400 font-bold mb-4">{{ chordName }}</h1>
    </template>

    <h2 v-if="chordFunction" class="text-xl">Harmonic function based on scale: </h2>
    <p v-if="chordFunction" class="my-2 text-sky-400">
      {{ chordFunction }}
    </p>

    <h3 v-if="notes.length > 0" class="text-xl mt-4 mb-2">The chord were created by these notes:</h3>

    <div v-if="notes.length > 0" class="flex flex-row justify-start text-sky-400">
      <span v-for="(note, index) in notes" :key="index" class="text-xl font-semibold">
        {{ note }}<span v-if="index < notes.length - 1">-</span>
      </span>
    </div>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';

export default {
  components: { DefaultModal },
  props: {
    notes: {
      type: Array,
      default: () => []
    },
    chordName: {
      type: String,
      default: ""
    },
    chordFunction: {
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
