<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-white">
    <div class="w-full max-w-md md:max-w-2xl text-center space-y-6">
      <img src="/logo.png" alt="Logo" class="w-24 h-24 mx-auto rounded-full shadow-lg" />

      <h1 class="text-3xl font-bold">Upload de Arquivo</h1>

      <h2 v-if="file && file.name && (progression.chords.length > 0 || progression.notes.length > 0)" class="text-lg font-semibold italic mb-2 text-gray-500">
        Arquivo: {{ file.name }}
      </h2>


      <Loading v-if="loading" :file-name="file ? file.name : ''"></Loading>
      <p v-else-if="message" class="mt-4 font-medium">
        <span :class="success">{{ message }}</span>
      </p>

      <ScalesModal :show="showScalesModal" :relative-scales="relativeScales" @close="showScalesModal = false" />
      <AIModelModal :show="showAIModal" :evaluation="modalEvaluation" :model-name="modalModelName" @close="showAIModal = false" />      

      <!-- INFO CONTENT -->
      <div v-if="(progression.chords.length > 0 || progression.notes.length > 0) && !showUploadForm" class="bg-gray-800 p-4 rounded-lg text-left space-y-1">

        <div class="flex justify-between">
          <h2 class="text-2xl font-bold mb-2">Principais informações</h2>

          <button
            type="button"
            class="py-2 px-2 1/2 bg-cyan-700 rounded-lg font-semibold hover:bg-cyan-900"
            @click="downloadMidi"
          >
            Download arquivo midi
          </button>  
          
          <button
            type="button"
            class="py-2 px-2 1/2 bg-cyan-700 rounded-lg font-semibold hover:bg-cyan-900"
            @click="downloadMusicalSheet"
          >
            Download partitura
          </button>
        </div>

        <div v-if="progression.chords.length > 0" class="my-2">
          <ChordsPlayedComponent :progression="progression.chords"></ChordsPlayedComponent>
        </div>

        <div v-if="progression.notes.length > 0" class="my-2">
          <NotesPlayedComponent :progression="progression.notes"></NotesPlayedComponent>
        </div>

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
              <span v-if="index < progression.chords.length - 1">, </span>
            </li>
          </ul>
        </p>  

        <h2 class="text-2xl font-bold mt-8 mb-2">Secundárias</h2>

        <p><span class="font-semibold text-blue-400">Tom:</span> {{ key }}</p>
        <p><span class="font-semibold text-blue-400">Andamento:</span> {{ tempo.time }} BPM (<i>{{ tempo.name }}</i>)</p>
        <p><span class="font-semibold text-blue-400">Tônica:</span> {{ tonic }}</p>

        <div class="flex justify-around my-4">
          <button
            type="button"
            class="py-2 px-12 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700"
            @click="showScalesModal = true"
          >
            Ver escalas relativas
          </button>

          <button
            type="button"
            class="py-2 px-12 bg-gray-700 rounded-lg font-semibold hover:bg-gray-600"
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
import ChordsPlayedComponent from "../components/music/ChordsPlayedComponent.vue"
import NotesPlayedComponent from "../components/music/NotesPlayedComponent.vue"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      loading: false,
      showUploadForm: true,
      showScalesModal: false,
      showAIModal: false,
      modalEvaluation: [],
      progression: {
        chords: [],
        notes: [],
      },
      emotions: [],
      relativeScales: [],
      message: "",
      modalModelName: "",
      key: "",
      tempo: [],
      tonic: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  components: {
    Loading,
    ChordModal,
    ScalesModal,
    AIModelModal,
    ChordsPlayedComponent,
    NotesPlayedComponent
  },  
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0]
    },
    async handleSubmit() {
      if (!this.file) {
        this.message = "Select file first!"
        this.cleanFields()
        this.loading = false
        return
      }

      const formData = new FormData()
      formData.append("uploaded_file", this.file)

      try {
        this.loading = true
        this.showUploadForm = false

        const response = await axios.post(`${this.API_URL}/upload-file`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.error) {
          this.loading = false
          this.showUploadForm = false
          this.message = "Veja as informações extraídas:"

          this.emotions = response.data.emotions || []
          this.key = response.data.key || ""
          this.relativeScales = response.data.relative_scales || []
          this.tonic = response.data.tonic || ""
          this.tempo = response.data.tempo || []
          this.progression = response.data.progression || []
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
      this.progression = {
        chords: [],
        notes: [],
      },
      this.relativeScales = []
      this.key = ""
      this.tempo = []
      this.tonic = ""
      this.file = null
    },
    openAIModelModal(emotion) {
      this.showAIModal = true
      this.modalEvaluation = emotion.evaluation
      this.modalModelName = emotion.model_used
    },
    showAndCleanForm() {
      this.cleanFields()
      this.showUploadForm = true
    },
    async downloadMidi() {
      if (!this.file) {
        alert("Select a file first!");
        return;
      }

      const formData = new FormData();
      formData.append("uploaded_file", this.file);

      const response = await axios.post(`${this.API_URL}/download-midi`, formData, {
        responseType: "blob"
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, "_");
      link.href = url;
      link.setAttribute("download", `${date}_played_progression.mid`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    },
    async downloadMusicalSheet() {
      if (!this.file) {
        alert("Select a file first!");
        return;
      }

      const formData = new FormData();
      formData.append("uploaded_file", this.file);

      const response = await axios.post(`${this.API_URL}/download-sheet`, formData, {
        responseType: "blob"
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, "_");
      link.href = url;
      link.setAttribute("download", `${date}_musical_sheet.xml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  },
  computed: {
    success() {
      let isSuccess = false;

      if(this.progression.chords.length > 0 || this.progression.notes.length > 0){
        isSuccess = true;
      }

      return isSuccess ? "text-green-600" : "text-red-500"
    }
  }
}
</script>
