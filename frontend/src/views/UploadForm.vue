<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-white">
    <div class="w-full max-w-md md:max-w-2xl text-center space-y-6">
      <img src="/logo.png" alt="Logo" class="w-32 h-32 md:w-52 md:h-52 mx-auto shadow-lg mb-12" />

      <h1 class="text-3xl font-bold">Chord and Emotion Recognizer</h1>

      <h2 v-if="file && file.name && (progression.chords.length > 0)" class="text-lg font-semibold italic mb-2 text-gray-500">
        File name: {{ file.name }}
      </h2>

      <button
        v-show="!loading && !showProgressionInfo && !showValidationForm"
        @click="optionRecordMic = !optionRecordMic"
        class="px-4 py-2 rounded bg-teal-600 text-white hover:bg-sky-700"
      >
        {{ optionRecordMic ? 'Want to upload my file!' : 'Try record from your browser!' }}
      </button>

      <!-- MIC RECORDER -->
      <MicRecorder 
        v-if="optionRecordMic"
        @audio-recorded="handleRecordedAudio"
      />
      <!-- END MIC RECORDER -->

      <p v-if="errors.length > 0" class="mt-4 font-medium">
        <span class="text-xl text-red-500">{{ message }}</span>
        <ul class="list-none text-red-300" v-for="(error, index) in errors">
          <li>{{ (index+1) }}: {{ error.message }}</li>
        </ul>
      </p>

      <Loading v-show="loading" :file-name="file ? file.name : ''"></Loading>

      <!-- UPLOAD FORM -->
      <form v-if="showUploadForm" @submit.prevent="handleSubmit" class="space-y-4">
        <audio
          v-if="uploadedFileUrl"
          :src="uploadedFileUrl"
          controls
          class="mt-4 w-full"
        ></audio>

        <input
          v-if="!optionRecordMic"
          type="file"
          @change="handleFileChange"
          class="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 
                 file:rounded-lg file:border-0 file:text-sm file:font-semibold 
                 file:bg-sky-600 file:text-white hover:file:bg-sky-700"
        />

        <button
          v-if="submitReadOnlyChecker"
          type="submit"
          class="w-full py-2 bg-sky-600 rounded-lg font-semibold hover:bg-sky-700"
        >
          Send
        </button>
      </form>
      <!-- END UPLOAD FORM -->

      <!-- VALIDATION FORM -->
      <ValidationForm
        v-if="showValidationForm"
        :progression="progression"
        :tempo="tempo"
        @confirm="handleConfirmedProgression"
        @edit="handleEditedProgression"
      />
      <!-- END VALIDATION FORM -->

      <!-- MUSIC INFORMATION -->
      <ProgressionInfo
        v-if="showProgressionInfo"
        :progression="progression"
        :emotion="emotion" 
        :scales="scales"
        :tempo="tempo" 
        :key-name="keyName" 
        :tonic="tonic"
        @reset="handleFormReset"
      />
      <!-- END MUSIC INFORMATION -->

      <div class="text-gray-600 italic flex flex-col justify-center">
        <p>Developed by: Lucas & Guilherme</p>
        2025
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"
import Loading from "../components/utils/Loading.vue"
import MicRecorder from "../components/utils/MicRecorder.vue"
import ProgressionInfo from "../components/sections/ProgressionInfo.vue"
import ValidationForm from "../components/sections/ValidationForm.vue"

export default {
  name: "UploadForm",
  data() {
    return {
      file: null,
      uploadedFileUrl: null,
      isAudioRecorded: false,
      optionRecordMic: false,
      loading: false,
      showUploadForm: true,
      showProgressionInfo: false,
      showValidationForm: false,
      progression: {
        chords: []
      },
      emotion: [],
      scales: [],
      message: "",
      errors: [],
      keyName: "",
      tempo: [],
      tonic: "",
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  components: {
    Loading,
    MicRecorder,
    ProgressionInfo,
    ValidationForm
  },  
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0]
      this.isAudioRecorded = false

      if (this.file) {
        this.uploadedFileUrl = URL.createObjectURL(this.file)
      }
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
      formData.append("is_recorded", this.isAudioRecorded ? 1 : 0)

      try {
        this.loading = true
        this.showUploadForm = false
        this.errors = []
        this.message = ""

        const response = await axios.post(`${this.API_URL}/upload-file`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.errors) {
          this.loading = false
          this.showUploadForm = false
          this.showValidationForm = true

          this.progression = response.data.progression || []
          this.tempo = response.data.tempo || []
        } else {
          this.loading = false
          this.message = "Error uploading file: "
          this.errors = response.data.errors
          this.showUploadForm = true
          this.showValidationForm = false
          this.file = null
          this.uploadedFileUrl = ""
        }
      } catch (error) {
        this.loading = false
        this.message = "Something went wrong uploading file: "
        this.errors = error.message
        this.showUploadForm = true
        this.showValidationForm = false
        this.file = null
        this.uploadedFileUrl = ""
      }
    },
    cleanFields(keepFile = false) {
      this.message = ""
      this.errors = []
      this.progression = {
        chords: []
      },
      this.scales = []
      this.keyName = ""
      this.tempo = []
      this.tonic = ""
      this.isAudioRecorded = false
      
      if(!keepFile){
        this.file = null
        this.uploadedFileUrl = null
      }
    },
    async getProgressionInfo(progression, bpm){
      try {
        this.loading = true
        this.showUploadForm = false
        this.showValidationForm = false

        const formData = new FormData()
        formData.append("chordProgression", progression.chordProgression)
        formData.append("tempo", bpm)
        formData.append("uploaded_file", this.file)

        const response = await axios.post(`${this.API_URL}/get-progression-info`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

        if (!response.data.errors) {
          this.loading = false
          this.showUploadForm = false
          this.showProgressionInfo = true
          
          this.emotion = response.data.emotion || []
          this.keyName = response.data.key_name || ""
          this.scales = response.data.scales || []
          this.tonic = response.data.tonic || ""
          this.tempo = response.data.tempo || []
          this.progression = response.data.progression || []
        } else {
          this.loading = false
          this.message = "Error validating progression: "
          this.errors = response.data.errors
          this.showUploadForm = false
          this.showValidationForm = true
          this.showProgressionInfo = false
        }
      } catch (error) {
        this.loading = false
        this.message = "Something went wrong validating progression: "
        this.errors = error.message
        this.showUploadForm = false
        this.showValidationForm = true
        this.showProgressionInfo = false
      }
    },
    formatProgressionStrings(progression) {
      if (!progression || typeof progression !== "object") {
        return { chordProgression: null };
      }

      const chordProgression = Array.isArray(progression.chords)
        ? progression.chords.map(ch => ch.chord.trim()).join("-") 
        : null;
        
      return { chordProgression };
    },
    handleConfirmedProgression(progression) {
      this.message = ""
      this.errors = []
      const bpm = progression.bpm ? parseInt(progression.bpm) : 0
      const formatted = this.formatProgressionStrings(progression)

      if(progression.bpm && (progression.chords)){
        this.getProgressionInfo(formatted, bpm)
      } else {
        this.message = "Error validating progression: "
        this.loading = false
        this.showUploadForm = false
        this.showValidationForm = true
        this.showProgressionInfo = false

        if (!progression.bpm){
          this.errors.push({"message": "BPM not informed."})
        } else if (!progression.chords){
          this.errors.push({"message": "Progression not informed."})
        } else if(progression.bpm <= 0) {
          this.errors.push({"message": "BPM can't be less or equal than 0."})
        } else if(progression.bpm > 320){
          this.errors.push({"message": "BPM can't be higher than 320."})
        }
      }
    },
    handleEditedProgression(progression) {
      this.message = ""
      this.errors = []
      const bpm = progression.bpm ? parseInt(progression.bpm) : 0
      const formatted = this.formatProgressionStrings(progression)

      if(progression.bpm && (progression.chords)){
        this.getProgressionInfo(formatted, bpm)
      } else {
        this.message = "Error validating progression: "
        this.loading = false
        this.showUploadForm = false
        this.showValidationForm = true
        this.showProgressionInfo = false

        if (!progression.bpm){
          this.errors.push({"message": "BPM not informed."})
        } else if (!progression.chords){
          this.errors.push({"message": "Progression not informed."})
        } else if(progression.bpm <= 0) {
          this.errors.push({"message": "BPM can't be less or equal than 0."})
        } else if(progression.bpm > 320){
          this.errors.push({"message": "BPM can't be higher than 320."})
        }
      }
    },
    handleRecordedAudio(blob) {
      const audioFile = new File([blob], "recording.webm", { type: "audio/webm" })
      this.file = audioFile
      this.isAudioRecorded = true
      this.uploadedFileUrl = URL.createObjectURL(audioFile)
    },
    handleFormReset(){
      this.cleanFields()
      this.showUploadForm = true
      this.optionRecordMic = false
      this.showValidationForm = false
      this.showProgressionInfo = false
    }
  },
  computed: {
    success() {
      let isSuccess = false;

      if(this.progression.chords.length > 0){
        isSuccess = true;
      }

      return isSuccess ? "text-green-600" : "text-red-500"
    },
    submitReadOnlyChecker() {
      return this.file
    }
  },
  watch: {
    optionRecordMic(newVal, oldValue){
      if(oldValue != newVal){  
        this.cleanFields()
      }
    }
  }
}
</script>
