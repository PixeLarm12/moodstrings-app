<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-white">
    <div class="w-full max-w-md md:max-w-2xl text-center space-y-6">
      <img src="/logo.png" alt="Logo" class="w-24 h-24 mx-auto rounded-full shadow-lg" />

      <h1 class="text-3xl font-bold">Upload de Arquivo</h1>

      <Loading v-if="loading"></Loading>
      <p v-else-if="message" class="mt-4 font-medium">
        <span :class="success">{{ message }}</span>
      </p>

      <ChordModal :show="showChordModal" :notes="modalNotes" :chord-name="modalChordName" @close="showChordModal = false" />
      <ScalesModal :show="showScalesModal" :relative-scales="relativeScales" @close="showScalesModal = false" />
      <AIModelModal :show="showAIModal" :evaluation="modalEvaluation" :model-name="modalModelName" @close="showAIModal = false" />      

      <!-- INFO CONTENT -->
      <div v-if="chordProgression.length > 0 && !showUploadForm" class="bg-gray-800 p-4 rounded-lg text-left space-y-1">
        <h2 class="text-2xl font-bold mb-2">Principais informações</h2>

        <span class="font-semibold text-blue-400">Sequência tocada: </span> 
        
        <p>
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

        <hr class="my-4">

        <span class="font-semibold text-blue-400">Emoção relacionada ao trecho: </span> 
        
        <p>
          <ul v-for="(emotion, index) in emotions" :key="index">
            <li class="list-none">
              <button 
                type="button" 
                v-if="emotion.model_used != 'KNN'"
                class="hover:text-blue-400 hover:cursor-pointer"
                @click="openAIModelModal(emotion)"
              >
              {{ ++index }} - {{ emotion.content }} ({{ emotion.model_used }})
              </button> 
              <span v-else>{{ ++index }} - {{ emotion.content }} ({{ emotion.model_used }})</span>
              <span v-if="index < chordProgression.length - 1">, </span>
            </li>
          </ul>
        </p>  

        <h2 class="text-2xl font-bold mt-8 mb-2">Secundárias</h2>

        <p><span class="font-semibold text-blue-400">Tom:</span> {{ key }}</p>
        <p><span class="font-semibold text-blue-400">Andamento:</span> {{ tempo }} BPM (<i>{{ tempoName }}</i>)</p>
        <p><span class="font-semibold text-blue-400">Tônica:</span> {{ tonic }}</p>
        <p><span class="font-semibold text-blue-400">Modo:</span> {{ mode }}</p>

        <div class="flex justify-between my-4">
          <button
            type="button"
            class="py-2 mx-2 w-1/3 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700"
            @click="showScalesModal = true"
          >
            Ver escalas relativas
          </button>

          <button
            type="button"
            class="py-2 mx-2 w-1/3 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700"
          >
            Download arquivo midi
          </button>  
          
          <button
            type="button"
            class="py-2 mx-2 w-1/3 bg-gray-700 rounded-lg font-semibold hover:bg-gray-600"
            @click="showAndCleanForm()"
          >
            Enviar outro arquivo
          </button>  
        </div>
      </div>
      <!-- END INFO CONTENT -->
      
      <!-- FORM -->
      <form v-if="showUploadForm" @submit.prevent="handleSubmit" class="space-y-4">
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
      <!-- END FORM -->

    </div>
  </div>
</template>

<script>
import axios from "axios"
import Loading from "../components/utils/Loading.vue"
import ChordModal from "../components/music/ChordModal.vue"
import ScalesModal from "../components/music/ScalesModal.vue"
import AIModelModal from "../components/ai/AIModelModal.vue"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      loading: false,
      showUploadForm: true,
      showChordModal: false,
      showScalesModal: false,
      showAIModal: false,
      modalNotes: [],
      modalEvaluation: [],
      chordProgression: [],
      emotions: [],
      relativeScales: [],
      message: "",
      modalChordName: "",
      modalModelName: "",
      key: "",
      tempoName: "",
      tempo: "",
      tonic: "",
      mode: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  components: {
    Loading,
    ChordModal,
    ScalesModal,
    AIModelModal
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
        this.showUploadForm = false

        const response = await axios.post(`${this.API_URL}/upload-file`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.error) {
          this.loading = false
          this.showUploadForm = false
          this.message = "Veja as informações extraídas:"

          this.chordProgression = response.data.chord_progression || []
          this.relativeScales = response.data.relative_scales || []
          this.key = response.data.key || ""
          this.emotions = response.data.emotions || ""
          this.tempoName = response.data.tempo_name || ""
          this.tempo = response.data.tempo || ""
          this.tonic = response.data.tonic || ""
          this.mode = response.data.mode || ""
        } else {
          this.loading = false
          this.message = `Error: ${response.data.error}`
          this.showUploadForm = true
        }
        
      } catch (error) {
        this.loading = false
        this.message = `Error: ${error.message}`
        this.showUploadForm = true
      }
    },
    cleanFields() {
      this.message = ""
      this.chordProgression = []
      this.relativeScales = []
      this.key = ""
      this.tempo = ""
      this.tonic = ""
      this.mode = ""
    },
    openChordModal(info) {
      this.showChordModal = true
      this.modalNotes = info.notes
      this.modalChordName = `${info.chord} (${info.name})`
    },
    openAIModelModal(emotion) {
      this.showAIModal = true
      this.modalEvaluation = emotion.evaluation
      this.modalModelName = emotion.model_used
    },
    showAndCleanForm() {
      this.cleanFields()
      this.showUploadForm = true
    }
  },
  computed: {
    success() {
      return this.chordProgression.length > 0 ? "text-green-600" : "text-red-500"
    }
  }
}
</script>
