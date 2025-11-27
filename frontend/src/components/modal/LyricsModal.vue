<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      <h1 class="text-2xl text-sky-400 font-bold mb-4">Find audio Lyrics</h1>
    </template>

    <div v-if="lyrics" class="flex flex-row justify-center">
        <p class="text-left whitespace-pre-line break-keep">
          {{ lyrics }}
        </p>
    </div>

    <Loading v-show="!lyrics" :file-name="file ? file.name : ''" :is-lyrics="true"></Loading>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';
import Loading from '../utils/Loading.vue';

export default {
  components: { DefaultModal, Loading },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    file: {
        type: File,
        default: null
    },
    lyrics: {
      type: String,
      default: ""
    },
  },
}
</script>
