<template>
  <div class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">notes sequence</b> that you played:
      </template>

      <span v-for="(note, index) in progression">
        {{ note }}
        <span v-if="index < progression.length - 1">- </span>
      </span>
    </DefaultToggleComponent>
  </div>
</template>

<script>
import DefaultToggleComponent from "../templates/DefaultToggleComponent.vue";

export default {
  name: "NotesPlayedComponent",
  components: { DefaultToggleComponent },
  props: {
    progression: {
      type: Array,
      default: () => []
    },
  }
};
</script>
