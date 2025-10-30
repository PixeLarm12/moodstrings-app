<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Model used: <b>{{ modelName }}</b>
    </template>

    <h3 class="text-xl mb-4">Infos:</h3>
    <ul class="list-disc pl-5">
      <li class="list-none">Accuracy: <b>{{ evaluation.accuracy }}</b></li>
      <li class="list-none">Amount of samples: <b>{{ evaluation.samples }}</b></li>
    </ul>
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
