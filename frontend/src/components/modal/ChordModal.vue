<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Acorde: <b>{{ chordName }}</b>
    </template>

    <h2 class="text-xl">Função do acorde na escala: </h2>
    <p class="mb-4">
      {{ chordFunction }}
    </p>

    <h3 class="text-xl mb-4">Notas que formam o acorde:</h3>
    <ul class="list-disc pl-5">
      <li v-for="(note, index) in notes" :key="index" class="list-none">{{ note }}</li>
    </ul>
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
