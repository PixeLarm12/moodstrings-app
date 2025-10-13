<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-white">
    <div class="w-full max-w-md text-center space-y-6">
      <img src="/logo.png" alt="Logo" class="w-24 h-24 mx-auto rounded-full shadow-lg" />

      <h1 class="text-3xl font-bold">Upload de Arquivo</h1>

      <ChordModal :show="showChordModal" :notes="modalNotes" :chord-name="modalChordName" @close="showChordModal = false" />

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

      <Loading v-if="loading"></Loading>
      <p v-else-if="message" class="mt-4 font-medium">
        <span :class="success">{{ message }}</span>
      </p>

      <div v-if="chordProgression.length > 0" class="bg-gray-800 p-4 rounded-lg text-left space-y-1">
        <p><span class="font-semibold text-blue-400">Tom:</span> {{ key }}</p>
        <p><span class="font-semibold text-blue-400">Emoção:</span> {{ emotion }}</p>
        <p>
          <span class="font-semibold text-blue-400">Progressão: </span> 
          <span v-for="(info, index) in chordProgression" :key="index">
            <button 
              type="button" 
              class="hover:text-blue-400 hover:cursor-pointer"
              @click="openChordModal(info)"
            >
            {{ info.chord }}
            </button> 
            <span v-if="index < chordProgression.length - 1">, </span>
          </span>
        </p>  
        <p><span class="font-semibold text-blue-400">Andamento:</span> {{ tempo }} BPM (<i>{{ tempoName }}</i>)</p>
        <p><span class="font-semibold text-blue-400">Tônica:</span> {{ tonic }}</p>
        <p><span class="font-semibold text-blue-400">Modo:</span> {{ mode }}</p>
      </div>

    </div>
  </div>
</template>

<script>
import axios from "axios"
import Loading from "../components/utils/Loading.vue"
import ChordModal from "../components/chord/ChordModal.vue"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      loading: false,
      showChordModal: false,
      modalNotes: [],
      message: "",
      chordProgression: [],
      modalChordName: "",
      key: "",
      emotion: "",
      tempoName: "",
      tempo: "",
      tonic: "",
      mode: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  components: {
    Loading,
    ChordModal
  },  
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0]
    },
    async handleSubmit() {
      if (!this.file) {
        this.message = "Selecione um arquivo primeiro!"
        this.cleanFields()
        this.loading = false
        return
      }

      const formData = new FormData()
      formData.append("uploaded_file", this.file)

      try {
        this.cleanFields()
        this.loading = true

        const response = await axios.post(`${this.API_URL}/upload-file`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.error) {
          this.loading = false
          this.message = "Veja as informações extraídas:"

          this.chordProgression = response.data.chord_progression || []
          this.key = response.data.key || ""
          this.emotion = response.data.emotion || ""
          this.tempoName = response.data.tempo_name || ""
          this.tempo = response.data.tempo || ""
          this.tonic = response.data.tonic || ""
          this.mode = response.data.mode || ""
        } else {
          this.loading = false
          this.message = `Error: ${response.data.error}`
        }
        
      } catch (error) {
        this.loading = false
        this.message = `Error: ${error.message}`
      }
    },
    cleanFields() {
      this.message = ""
      this.chordProgression = []
      this.key = ""
      this.tempo = ""
      this.tonic = ""
      this.mode = ""
    },
    openChordModal(info) {
      this.showChordModal = true
      this.modalNotes = info.notes
      this.modalChordName = `${info.chord} (${info.name})`
    }
  },
  computed: {
    success() {
      return this.chordProgression.length > 0 ? "text-green-600" : "text-red-500"
    }
  }
}
</script>
