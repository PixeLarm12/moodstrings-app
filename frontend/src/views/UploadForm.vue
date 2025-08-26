<template>
  <div class="p-4 max-w-md mx-auto">
    <h1 class="text-4xl font-bold text-red-600">Upload de Arquivo</h1>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <input type="file" @change="handleFileChange" />

      <button
        type="submit"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Enviar
      </button>
    </form>

    <br>

    <ul v-if="chordProgression">
      <li>Progressão tocada: {{ chordProgression }}</li>
      <li>Tom: {{ key }}</li>
      <li>Andamento (BPM): {{ tempo }}</li>
      <li>Tônica: {{ tonic }}</li>
      <li>Modo: {{ mode }}</li>
    </ul>
    
    <br>

    <p v-if="message" class="mt-4 text-green-600">{{ message }}</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UploadForm",
  data() {
    return {
      API_URL: "",
      chordProgression: "",
      key: "",
      tempo: "",
      tonic: "",
      mode: "",
      uploadedFile: null,
      message: ""
    }
  },
  methods: {
    handleFileChange(event) {
      this.uploadedFile = event.target.files[0];
    },

    async handleSubmit() {
      if (!this.uploadedFile) {
        this.message = "Selecione um arquivo primeiro!";
        return;
      }

      const formData = new FormData();
      formData.append("uploaded_file", this.uploadedFile);

      try {
        const response = await axios.post(
          `${this.API_URL}/upload-file`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        this.message = `Arquivo enviado com sucesso: ${
          response.data.filename || ""
        }`;

        if (response.data.chordProgression) {
          this.chordProgression = response.data.chordProgression;
          this.key = response.data.key;
          this.tempo = response.data.tempo;
          this.tonic = response.data.tonic;
          this.mode = response.data.mode;
        }
      } catch (error) {
        this.message = `Erro ao enviar: ${error.message}`;
      }
    },
  },
  mounted() {
    this.API_URL = import.meta.env.VITE_API_URL;
  }
}
</script>
