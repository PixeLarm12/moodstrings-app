<template>
  <div class="mt-6">
    <DefaultToggleComponent>
      <template #header>
        Check <b class="text-sky-400">notes sequence</b> that you played:
      </template>

      <div class="w-full flex flex-wrap justify-start gap-2">
        <Card
          v-for="(note, index) in progression"
        >
          <template #name>
            {{ note }} 
          </template>
        </Card>
      </div>
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
