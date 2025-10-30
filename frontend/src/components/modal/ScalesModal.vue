<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      See relative scale:
    </template>

    <p>
      <div v-for="(info, index) in relativeScales" :key="index">
        <h3 v-if="info.key" class="text-lg mb-4 font-semibold">Scale: {{ info.key }}</h3> 

        <ul class="list-disc pl-5">
          <li v-for="(chord, modeIndex) in info.chords" :key="modeIndex" class="list-none">
            {{ chord.chord }} <i>{{ chord.function }}</i>
          </li>
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
