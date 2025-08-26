<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-white">
    <div class="w-full max-w-md text-center space-y-6">
      <img src="/logo.png" alt="Logo" class="w-24 h-24 mx-auto rounded-full shadow-lg" />

      <h1 class="text-3xl font-bold">Upload de Arquivo</h1>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <input
          type="file"
          @change="handleFileChange"
          class="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 
                 file:rounded-lg file:border-0 file:text-sm file:font-semibold 
                 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />

        <button
          type="submit"
          class="w-full py-2 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700"
        >
          Enviar
        </button>
      </form>

      <p v-if="message" class="mt-4 text-red-400 font-medium">
        {{ message }}
      </p>

      <div v-if="chordProgression" class="bg-gray-800 p-4 rounded-lg text-left space-y-1">
        <p><span class="font-semibold">Progressão:</span> {{ chordProgression }}</p>
        <p><span class="font-semibold">Tom:</span> {{ key }}</p>
        <p><span class="font-semibold">Andamento (BPM):</span> {{ tempo }}</p>
        <p><span class="font-semibold">Tônica:</span> {{ tonic }}</p>
        <p><span class="font-semibold">Modo:</span> {{ mode }}</p>
      </div>

    </div>
  </div>
</template>

<script>
import { ref } from "vue"
import axios from "axios"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      message: "",
      chordProgression: "",
      key: "",
      tempo: "",
      tonic: "",
      mode: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0]
    },
    async handleSubmit() {
      if (!this.file) {
        this.message = "Selecione um arquivo primeiro!"
        return
      }

      const formData = new FormData()
      formData.append("uploaded_file", this.file)

      try {
        const response = await axios.post(`${this.API_URL}/upload-file`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        this.message = 'Veja as informações extraídas:'
        this.chordProgression = response.data.chordProgression || ""
        this.key = response.data.key || ""
        this.tempo = response.data.tempo || ""
        this.tonic = response.data.tonic || ""
        this.mode = response.data.mode || ""
      } catch (error) {
        this.message = `Erro: ${error.message}`
      }
    }
  }
}
</script>