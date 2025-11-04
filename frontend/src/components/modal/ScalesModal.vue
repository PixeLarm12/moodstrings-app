<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Relative scale: <b class="text-sky-400">{{ relativeScales.key }}</b>
    </template>

    <ChordsPlayedComponent :progression="relativeScales.chords" :lock-chord-modal="true"></ChordsPlayedComponent>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';
import ChordsPlayedComponent from '../music/ChordsPlayedComponent.vue';

export default {
  components: { DefaultModal, ChordsPlayedComponent },
  props: {
    relativeScales: {
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
