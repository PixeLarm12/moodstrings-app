<template>
  <div class="flex items-center justify-center py-8 px-4">
      <ScalesModal :show="showScalesModal" :scales="scales" @close="showScalesModal = false" />

      <div v-if="(progression.chords.length > 0 || progression.notes.length > 0)" class="bg-gray-800 p-4 rounded-lg text-left space-y-1">

        <div class="grid grid-cols-1 md:grid-cols-12 gap-2">
            <div class="w-full md:col-span-7">
                <div class="w-full flex flex-col gap-2">
                    <p><span class="font-semibold text-sky-400">Key:</span> {{ keyName }}</p>
                    <p><span class="font-semibold text-sky-400">Tempo:</span> {{ tempo.time }} BPM (<i>{{ tempo.name }}</i>)</p>
                    <p><span class="font-semibold text-sky-400">Tonic:</span> {{ tonic }}</p>
                </div>
            </div>

            <div class="w-full md:col-span-5 flex flex-col justify-start gap-2 md:gap-4">
              <!-- <button
                  v-if="(progression.chords.length > 0)"
                  type="button"
                  class="py-2 px-2 1/2 bg-sky-700 rounded-lg font-semibold hover:bg-sky-900"
                  @click="downloadMidi"
              >
                  Download midi file
              </button>   -->
              
              <!-- <button
                  type="button"
                  class="py-2 px-2 1/2 bg-sky-700 rounded-lg font-semibold hover:bg-sky-900"
                  @click="downloadMusicalSheet"
              >
                  Download music sheet
              </button> -->
            </div>
        </div>

        <div v-if="progression.chords.length > 0 && !(progression.chords.length <= 0 && progression.notes.length > 0)" class="my-2">
            <ChordsPlayedComponent :progression="progression.chords"></ChordsPlayedComponent>
        </div>

        <div v-if="progression.chords.length <= 0 && progression.notes.length > 0" class="my-2">
            <NotesPlayedComponent :progression="progression.notes"></NotesPlayedComponent>
        </div>

        <div v-if="emotion" class="my-2">
            <EmotionsComponent :emotion="emotion"></EmotionsComponent>
        </div>

        <div class="flex justify-around my-4">
            <button
              type="button"
              class="py-2 px-12 bg-sky-600 rounded-lg font-semibold hover:bg-sky-700"
              @click="showScalesModal = true"
            >
            See scales
            </button>

            <button
              type="button"
              class="py-2 px-12 bg-gray-700 rounded-lg font-semibold hover:bg-gray-600"
              @click="reset()"
            >
            Send new file
            </button>  
        </div>
      </div>
  </div>
</template>

<script>
import axios from "axios"
import ScalesModal from "../modal/ScalesModal.vue"
import EmotionsComponent from "../music/EmotionsComponent.vue"
import ChordsPlayedComponent from "../music/ChordsPlayedComponent.vue"
import NotesPlayedComponent from "../music/NotesPlayedComponent.vue"

export default {
  name: "ProgressionInfo",
  data() {
    return {
      showScalesModal: false,
      API_URL: import.meta.env.VITE_API_URL
    }
  },
  props: {
    progression: {
      type: Object,
      default: () => {}
    },
    emotion: {
      type: Object,
      default: () => []
    },
    scales: {
      type: Array,
      default: () => []
    },
    tempo: {
      type: Object,
      default: () => []
    },
    keyName: {
      type: String,
      default: ""
    },
    tonic: {
      type: String,
      default: ""
    }
  },
  components: {
    ScalesModal,
    EmotionsComponent,
    ChordsPlayedComponent,
    NotesPlayedComponent
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0]
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
    },
    reset(){
      this.$emit("reset");
    }
  },
}
</script>