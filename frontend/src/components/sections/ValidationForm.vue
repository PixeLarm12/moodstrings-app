<template>
  <div class="flex flex-col items-center justify-center text-white bg-gray-900 py-8 px-4">
    <div v-if="progression && (progression.chords?.length)"
         class="w-full max-w-3xl bg-gray-800 rounded-xl p-6 shadow-lg space-y-6">
      
      <!-- Title -->
      <div class="text-center space-y-1">
        <h2 class="text-2xl font-bold text-sky-400">Confirm progression played:</h2>
        
        <p class="text-gray-300">Check if the sequences below corresponds that what you played.</p>
        <p class="text-sm italic text-gray-300 my-2">Please, use Chord patterns as C (C major) or Cm (C minor). Avoid using non-existing chords to improve info extraction </p>
        <span class="text-xl text-sky-400 mt-2">
          {{ tempo.time }}BPM <i>({{ tempo.name }})</i>
        </span>
      </div>

      <!-- Detected Chords -->
      <div v-if="progression.chords?.length" class="space-y-2">
          <ChordsPlayedComponent :progression="progression.chords" :lock-chord-modal="true"></ChordsPlayedComponent>
      </div>

      <!-- Question -->
      <div class="text-center pt-4">
        <p class="text-lg font-medium text-gray-200">Is that what you played?</p>

        <div class="flex justify-center gap-6 mt-4">
          <button
            class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="emitProgression('confirm', progression)"
          >
            Yes!
          </button>

          <button
            class="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="toggleEditMode"
          >
            No, needs correction
          </button>
        </div>
      </div>

      <!-- Edit Mode -->
      <div v-if="editMode" class="mt-6 space-y-4 border-t border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-sky-300">Progression rewrite</h3>

        <p class="text-sm italic text-gray-300 my-2">We will rewrite given progression by what you write, so use it carefully.</p>

        <label class="block text-sm text-gray-300 mb-1">Tempo (BPM):</label>
        <input
          v-model="manualBpm"
          type="number"
          placeholder="Example: 120"
          class="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-500 focus:ring-2 focus:ring-sky-500"
        />

        <label v-if="progression.chords?.length || !(!progression.chords?.length)" class="block text-sm text-gray-300 mb-1">Chords (separated by hifen "-"):</label>
        <textarea
          v-if="progression.chords?.length || !(!progression.chords?.length)"
          v-model="manualChords"
          type="text"
          placeholder="Example: C G Am F"
          class="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 
                text-white placeholder-gray-500 
                focus:ring-2 focus:ring-sky-500 
                resize-auto"
        ></textarea>


        <div class="flex justify-center gap-6 mt-4">
          <button
            class="bg-sky-700 hover:bg-sky-800 text-white px-6 py-2 rounded-lg font-semibold"
            @click="emitProgression('edit', {})"
          >
            Confirm
          </button>

          <button
            class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold"
            @click="toggleEditMode"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Card from '../utils/Card.vue';
import ChordsPlayedComponent from '../music/ChordsPlayedComponent.vue';

export default {
  name: "ValidationForm",
  components: {
    Card,
    ChordsPlayedComponent
  },
  props: {
    progression: {
      type: Object,
      default: () => {},
      required: true
    },
    tempo: {
      type: Object,
      default: () => {},
      required: true
    }
  },
  data() {
    return {
      editMode: false,
      manualChords: "",
      manualBpm: null,
      errors: "",
    };
  },
  methods: {
    toggleEditMode() {
      this.editMode = !this.editMode;
    },
    emitProgression(emitType, progression){
      if(emitType === 'confirm'){
        const object = {
          chords: this.progression.chords,
          bpm: this.tempo.time
        };

        this.$emit('confirm', object)
      }

      if(emitType === 'edit'){
        const object = {
          chords: this.manualChords
            ? this.manualChords.trim().split(/-/).map(chord => ({ chord }))
            : [],
          bpm: this.manualBpm ? this.manualBpm : null
        };


        this.$emit('edit', object)
        this.editMode = false;
      }
    }
  },
  watch: {
    editMode(newVal, oldVal){
      if (newVal) {
        let chords = ""
        if(this.progression.chords.length > 0){
          for (let index = 0; index < this.progression.chords.length; index++) {
            const ch = this.progression.chords[index];
            
            if(index == 0){
              chords = ch.chord
            } else {
              chords += "-" + ch.chord  
            }
          }
        }

        this.manualChords = chords
        this.manualBpm = this.tempo.time
      }
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
