<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      See related scales to your progression:
    </template>

    <div v-if="scales.actual && scales.relatives" class="w-full">
      <h2 class="font-semibold text-lg text-sky-400">Scale: {{ scales.actual.key }}</h2>
      <ChordsPlayedComponent :progression="scales.actual.chords"></ChordsPlayedComponent>
      
      <hr class="my-10 text-sky-700">
      
      <h2 class="font-semibold text-lg text-sky-400">Relative: {{ scales.relatives.key }}</h2>
      <ChordsPlayedComponent :progression="scales.relatives.chords"></ChordsPlayedComponent>
    </div>

    <div v-else class="flex flex-col justify-center text-lg italic">
      <p>
        The sequence played aren't related to any Major or Minor scales.
      </p>

      <p>
        In this case, may be an non-diatonic scale or is related to other mode.
      </p>
    </div>
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
