<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      See related scales to your progression:
    </template>

    <h2 class="font-semibold text-lg text-sky-400">Scale: {{ scales.actual.key }}</h2>
    <ChordsPlayedComponent :progression="scales.actual.chords" :lock-chord-modal="true"></ChordsPlayedComponent>

    <hr class="my-10 text-sky-700">
    
    <h2 class="font-semibold text-lg text-sky-400">Relative: {{ scales.relatives.key }}</h2>
    <ChordsPlayedComponent :progression="scales.relatives.chords" :lock-chord-modal="true"></ChordsPlayedComponent>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';
import ChordsPlayedComponent from '../music/ChordsPlayedComponent.vue';

export default {
  components: { DefaultModal, ChordsPlayedComponent },
  props: {
    scales: {
      type: Object,
      default: () => {}
    },
    show: {
      type: Boolean,
      default: false
    }
  }
}
</script>
