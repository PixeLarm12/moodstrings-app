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

      <!-- VALIDATION FORM -->
      <ValidationForm
        v-if="showValidationForm"
        :progression="progression"
        @confirm="handleConfirmedProgression"
        @edit="handleEditedProgression"
      />
      <!-- END VALIDATION FORM -->

      <!-- MUSIC INFORMATION -->
      <ProgressionInfo
        v-if="showProgressionInfo"
        :progression="progression"
        :emotion="emotion" 
        :relative-scale="relativeScales"
        :tempo="tempo" 
        :key="key" 
        :tonic="tonic"
      />
      <!-- END MUSIC INFORMATION -->
      
      <!-- UPLOAD FORM -->
      <form v-if="showUploadForm" @submit.prevent="handleSubmit" class="space-y-4">
        <input
          type="file"
          @change="handleFileChange"
          class="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 
                 file:rounded-lg file:border-0 file:text-sm file:font-semibold 
                 file:bg-sky-600 file:text-white hover:file:bg-sky-700"
        />

        <button
          type="submit"
          class="w-full py-2 bg-sky-600 rounded-lg font-semibold hover:bg-sky-700"
        >
          Enviar
        </button>
      </form>
      <!-- END UPLOAD FORM -->

    </div>
  </div>
</template>

<script>
import axios from "axios"
import Loading from "../components/utils/Loading.vue"
import ProgressionInfo from "../components/sections/ProgressionInfo.vue"
import ValidationForm from "../components/sections/ValidationForm.vue"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      loading: false,
      showUploadForm: true,
      showProgressionInfo: false,
      showValidationForm: false,
      progression: {
        chords: [],
        notes: [],
      },
      emotion: [],
      relativeScales: [],
      message: "",
      key: "",
      tempo: [],
      tonic: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  components: {
    Loading,
    ProgressionInfo,
    ValidationForm
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
          this.showValidationForm = true
          this.message = "Check your progression:"

          this.progression = response.data.progression || []
        } else {
          this.loading = false
          this.message = `Error: ${response.data.error}`
          this.showUploadForm = true
          this.showValidationForm = false
        }
        
      } catch (error) {
        this.loading = false
        this.message = `Error: ${error.message}`
        this.showUploadForm = true
        this.showValidationForm = false
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
    showAndCleanForm() {
      this.cleanFields()
      this.showUploadForm = true
    },
    async getProgressionInfo(progression){
      try {
        this.loading = true
        this.showUploadForm = false
        this.showValidationForm = false

        const formData = new FormData()
        formData.append("chordProgression", JSON.stringify(progression.chordProgression))
        formData.append("noteProgression", JSON.stringify(progression.noteProgression))
        formData.append("uploaded_file", this.file)

        const response = await axios.post(`${this.API_URL}/get-progression-info`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.error) {
          this.loading = false
          this.showUploadForm = false
          this.showProgressionInfo = true
          this.message = "Check your informations:"
          
          this.emotion = response.data.emotion || []
          this.key = response.data.key || ""
          this.relativeScales = response.data.relative_scales || []
          this.tonic = response.data.tonic || ""
          this.tempo = response.data.tempo || []
          this.progression = response.data.progression || []
        } else {
          this.loading = false
          this.message = `Error: ${response.data.error}`
          this.showUploadForm = false
          this.showValidationForm = true
          this.showProgressionInfo = false
        }
        
      } catch (error) {
        this.loading = false
        this.message = `Error: ${error.message}`
        this.showUploadForm = false
        this.showValidationForm = true
        this.showProgressionInfo = false
      }
    },
    formatProgressionStrings(progression) {
      if (!progression || typeof progression !== "object") {
        return { noteProgression: "", chordProgression: "" };
      }

      const chordProgression = Array.isArray(progression.chords)
        ? progression.chords.map(ch => ch.chord).join(" ")
        : "";

      const noteProgression = Array.isArray(progression.notes)
        ? progression.notes.join(" ")
        : "";

      return { chordProgression, noteProgression };
    },
    handleConfirmedProgression(progression) {
      const formatted = this.formatProgressionStrings(progression)
      this.getProgressionInfo(formatted)
    },
    handleEditedProgression(progression) {
      const formatted = this.formatProgressionStrings(progression)
      this.getProgressionInfo(formatted)
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
