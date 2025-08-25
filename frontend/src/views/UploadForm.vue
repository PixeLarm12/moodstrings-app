<template>
  <div class="p-4 max-w-md mx-auto">
    <h1 class="text-xl font-bold mb-4">Upload de Arquivo</h1>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <input type="file" @change="handleFileChange" />

      <button
        type="submit"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Enviar
      </button>
    </form>

    <p v-if="message" class="mt-4 text-green-600">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const file = ref(null);
const message = ref("");
const API_URL = import.meta.env.VITE_API_URL;

const handleFileChange = (event) => {
  file.value = event.target.files[0];
};

const handleSubmit = async () => {
  if (!file.value) {
    message.value = "Selecione um arquivo primeiro!";
    return;
  }

  const formData = new FormData();
  formData.append("uploaded_file", file.value);

  try {
    const response = await axios.post(`${API_URL}/upload-file`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    message.value = `Arquivo enviado com sucesso: ${response.data.filename || ''}`;
  } catch (error) {
    message.value = `Erro ao enviar: ${error.message}`;
  }
};
</script>
