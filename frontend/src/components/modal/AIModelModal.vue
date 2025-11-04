<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      <h1 class="text-2xl text-sky-400 font-bold mb-4">{{ modelName }}</h1>
    </template>

    <div class="flex flex-col justify-start text-lg">
      <span>Accuracy: <b class="font-semibold text-sky-400">{{ evaluation.accuracy }}%</b></span>
      <span>Samples: <b class="font-semibold text-sky-400">{{ evaluation.samples }}</b></span>
    </div>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';

export default {
  components: { DefaultModal },
  props: {
    evaluation: {
      type: Object,
      default: () => {}
    },
    modelName: {
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
