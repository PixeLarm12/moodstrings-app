<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      Vejas as escalas relativas:
    </template>

    <p>
      <div v-for="(info, index) in relativeScales" :key="index">
        <b v-if="info.relative_major">Relativa maior: {{ info.relative_major }}</b>

        <ul class="list-disc pl-5">
          <li v-for="(mode, modeIndex) in info.modes" :key="modeIndex" class="list-none">{{ mode }}</li>
        </ul>
      </div>
    </p>

    
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';

export default {
  components: { DefaultModal },
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
