<template>
  <ChordModal 
    :show="showChordModal" 
    :notes="modalNotes" 
    :chord-name="modalChordName" 
    :chord-function="modalChordFunction" 
    @close="showChordModal = false" 
  />

  <div class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">chords sequence</b> that you played:
      </template>

      <span v-for="(item, index) in progression">
        <button 
          type="button" 
          class="hover:text-sky-400 hover:cursor-pointer"
          @click="openChordModal(item)"
        >
          {{ item.chord }}
        </button>
        <span v-if="index < progression.length - 1">- </span>
      </span>
    </DefaultToggleComponent>
  </div>
</template>

<script>
import DefaultToggleComponent from "../templates/DefaultToggleComponent.vue";
import ChordModal from "../modal/ChordModal.vue";

export default {
  name: "ChordsPlayedComponent",
  components: { 
    DefaultToggleComponent,
    ChordModal
  },
  props: {
    progression: {
      type: Array,
      default: () => []
    },
  },
  data() {
    return {
      showChordModal: false,
      modalNotes: [],
      modalChordName: "",
      modalChordFunction: "",
    }
  },
  methods: {
    openChordModal(info) {
      this.showChordModal = true
      this.modalNotes = info.notes
      this.modalChordName = `${info.chord} (${info.name})`
      this.modalChordFunction = info.function
    },
  }
};
</script>
