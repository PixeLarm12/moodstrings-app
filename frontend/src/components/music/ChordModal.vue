<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Acorde: <b>{{ chordName }}</b>
    </template>

    <h3 class="text-xl mb-4">Notas que o compõem:</h3>
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
    show: {
      type: Boolean,
      default: false
    }
  }
}
</script>
