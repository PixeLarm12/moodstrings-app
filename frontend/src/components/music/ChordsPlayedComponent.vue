<template>
  <ChordModal 
    :show="showChordModal" 
    :notes="modalNotes" 
    :chord-name="modalChordName" 
    :chord-function="modalChordFunction" 
    @close="showChordModal = false" 
  />

  <div v-if="!lockChordModal" class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">chords sequence</b> that you played:
      </template>

      <div class="w-full flex flex-wrap justify-start gap-2">
        <Card
          :show-full-name="true"
          v-for="(item, index) in progression"
          class="hover:bg-gray-500 hover:cursor-pointer"
          @click="openChordModal(item)"
        >
          <template #name>
            {{ item.chord }} 
          </template>
          <template #full-name>
            {{ item.name }}
          </template>
        </Card>
      </div>
    </DefaultToggleComponent>
  </div>

  <div v-else class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">chords sequence</b> that you played:
      </template>

      <div class="w-full flex flex-wrap justify-start gap-2">
        <Card
          :show-full-name="true"
          v-for="(item, index) in progression"
        >
          <template #name>
            {{ item.chord }} 
          </template>
          <template #full-name>
            {{ item.name }}
          </template>
        </Card>
      </div>
    </DefaultToggleComponent>
  </div>
</template>

<script>
import DefaultToggleComponent from "../templates/DefaultToggleComponent.vue";
import ChordModal from "../modal/ChordModal.vue";
import Card from "../utils/Card.vue";

export default {
  name: "ChordsPlayedComponent",
  components: { 
    DefaultToggleComponent,
    ChordModal,
    Card
  },
  props: {
    progression: {
      type: Array,
      default: () => []
    },
    lockChordModal: {
      type: Boolean,
      default: false
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
