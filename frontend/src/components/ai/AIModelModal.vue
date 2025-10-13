<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Modelo usado: <b>{{ modelName }}</b>
    </template>

    <h3 class="text-xl mb-4">Informações:</h3>
    <ul class="list-disc pl-5">
      <li class="list-none">Acurácia: <b>{{ evaluation.accuracy }}</b></li>
      <li class="list-none">Número de amostras: <b>{{ evaluation.samples }}</b></li>
    </ul>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';

export default {
  components: { DefaultModal },
  props: {
    evaluation: {
      type: Array,
      default: () => []
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
