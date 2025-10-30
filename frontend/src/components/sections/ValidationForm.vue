<template>
  <div class="min-h-screen flex flex-col items-center justify-center text-white bg-gray-900 py-8 px-4">
    <div v-if="progression && (progression.chords?.length || progression.notes?.length)"
         class="w-full max-w-3xl bg-gray-800 rounded-xl p-6 shadow-lg space-y-6">
      
      <!-- Title -->
      <div class="text-center space-y-1">
        <h2 class="text-2xl font-bold text-sky-400">🎶 Confirme a Progressão Detectada</h2>
        <p class="text-gray-300">Verifique se a sequência abaixo corresponde ao que você tocou.</p>
      </div>

      <!-- Detected Chords -->
      <div v-if="progression.chords?.length" class="space-y-2">
        <h3 class="text-lg font-semibold text-sky-300">Acordes Detectados:</h3>
        <div class="flex flex-wrap gap-2">
          <span v-for="(ch, index) in progression.chords" :key="index"
                class="px-3 py-2 bg-gray-700 rounded-xl border border-sky-600 text-sky-100 text-sm hover:bg-gray-600">
            {{ ch.chord }} <span class="text-gray-400 text-xs">({{ ch.name }})</span>
          </span>
        </div>
      </div>

      <!-- Detected Notes -->
      <div v-if="progression.notes?.length" class="space-y-2">
        <h3 class="text-lg font-semibold text-sky-300">Notas Detectadas:</h3>
        <div class="flex flex-wrap gap-2">
          <span v-for="(n, index) in progression.notes" :key="index"
                class="px-2 py-1 bg-gray-700 rounded-md border border-gray-600 text-gray-200 text-xs">
            {{ n }}
          </span>
        </div>
      </div>

      <!-- Question -->
      <div class="text-center pt-4">
        <p class="text-lg font-medium text-gray-200">Isso foi o que você tocou?</p>

        <div class="flex justify-center gap-6 mt-4">
          <button
            class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="$emit('confirm', progression)"
          >
            ✅ Sim, está correto
          </button>

          <button
            class="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="toggleEditMode"
          >
            ❌ Não, quero corrigir
          </button>
        </div>
      </div>

      <!-- Edit Mode -->
      <div v-if="editMode" class="mt-6 space-y-4 border-t border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-sky-300">Corrigir Progressão</h3>

        <label class="block text-sm text-gray-300 mb-1">Acordes (separados por espaço):</label>
        <input
          v-model="manualChords"
          type="text"
          placeholder="Exemplo: C G Am F"
          class="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-500 focus:ring-2 focus:ring-sky-500"
        />

        <label class="block text-sm text-gray-300 mb-1">Notas (opcional, separadas por espaço):</label>
        <input
          v-model="manualNotes"
          type="text"
          placeholder="Exemplo: C E G A"
          class="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-500 focus:ring-2 focus:ring-sky-500"
        />

        <div class="flex justify-center gap-6 mt-4">
          <button
            class="bg-sky-700 hover:bg-sky-800 text-white px-6 py-2 rounded-lg font-semibold"
            @click="submitManualProgression"
          >
            💾 Confirmar Correção
          </button>

          <button
            class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="toggleEditMode"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ValidationForm",
  props: {
    progression: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      editMode: false,
      manualChords: "",
      manualNotes: ""
    };
  },
  methods: {
    toggleEditMode() {
      this.editMode = !this.editMode;
    },
    submitManualProgression() {
      const cleaned = {
        chords: this.manualChords
          ? this.manualChords.trim().split(/\s+/).map(chord => ({ chord }))
          : [],
        notes: this.manualNotes ? this.manualNotes.trim().split(/\s+/) : []
      };
      this.$emit("edit", cleaned);
      this.editMode = false;
    }
  }
};
</script>

<style scoped>
/* Optional: simple transition for edit mode */
.edit-enter-active,
.edit-leave-active {
  transition: all 0.3s ease;
}
.edit-enter-from,
.edit-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
