<template>
  <DefaultModal :show="show" @close="$emit('close')">
    <template #header>
      <h1 class="text-2xl text-sky-400 font-bold mb-4">Find audio Lyrics</h1>
    </template>

    <button
        v-if="! lyrics && !loading"
        type="button"
        class="py-2 px-2 1/2 bg-sky-700 rounded-lg font-semibold hover:bg-sky-900"
        @click="findLyrics"
    >
        Try to get audio lyrics!
    </button>  

    <div v-if="lyrics && !loading" class="flex flex-row justify-center">
        <p class="text-left whitespace-pre-line break-keep">
          {{ lyrics }}
        </p>
    </div>

    <Loading v-show="loading" :file-name="file ? file.name : ''" :is-lyrics="true"></Loading>
  </DefaultModal>
</template>

<script>
import DefaultModal from '../templates/DefaultModal.vue';
import axios from "axios"
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
    }
  },
  data() {
    return {
        lyrics: "",
        loading: false,
        LYRICS_API_URL: import.meta.env.VITE_LYRICS_API_URL
    }
  },
  methods: {
    async findLyrics() {
      if (!this.file) {
        return
      }

      this.loading = true;

      const formData = new FormData()
      formData.append("uploaded_audio", this.file)

      try {
        const response = await axios.post(`${this.LYRICS_API_URL}/audio`, formData,   {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.errors) {
          this.loading = false
          this.lyrics = response.data.data
        } else {
          this.loading = false
          this.lyrics = "No lyrics"
        }
      } catch (error) {
        this.loading = false
        this.lyrics = "No lyrics" 
      }
    },
  }
}
</script>
