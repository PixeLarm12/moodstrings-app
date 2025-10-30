<template>
    <AIModelModal 
        :show="showAIModal" 
        :evaluation="modalEvaluation" 
        :model-name="modalModelName" 
        @close="showAIModal = false"
    />

  <div class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">emotions</b> related to your sequence:
      </template>

        <button 
            type="button" 
            class="hover:text-sky-400 hover:cursor-pointer"
            @click="openAIModelModal(emotion)"
        >
            {{ emotion.content }} ({{ emotion.model_used }})
        </button> 
    </DefaultToggleComponent>
  </div>
</template>

<script>
import DefaultToggleComponent from "../templates/DefaultToggleComponent.vue";
import AIModelModal from "../modal/AIModelModal.vue";

export default {
  name: "EmotionsComponent",
  components: { 
    DefaultToggleComponent,
    AIModelModal
  },
  props: {
    emotion: {
      type: Object,
      default: () => {}
    },
  },
  data() {
    return {
      showAIModal: false,
      modalEvaluation: [],
      modalModelName: "",
    }
  },
  methods: {
    openAIModelModal(emotion) {
      this.showAIModal = true
      this.modalEvaluation = emotion.evaluation
      this.modalModelName = emotion.model_used
    },
  }
};
</script>
