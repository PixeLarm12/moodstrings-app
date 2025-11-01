<template>
  <div class="flex flex-col items-center space-y-4">
    <button
      @click="toggleRecording"
      class="px-4 py-2 rounded bg-sky-600 text-white hover:bg-sky-700"
    >
      {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
    </button>
  </div>
</template>

<script>
export default {
  name: "MicRecorder",
  emits: ["audio-recorded"],  
  data() {
    return {
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      audioUrl: null,
    };
  },
  methods: {
    async toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    },

    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);

        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.audioChunks, { type: "audio/webm" });
          this.audioUrl = URL.createObjectURL(blob);

          this.$emit("audio-recorded", blob)
        }

        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (err) {
        console.error("Microphone access denied or error:", err);
        alert("Please allow microphone access.");
      }
    },

    stopRecording() {
      this.mediaRecorder.stop();
      this.isRecording = false;
    },
  },
};
</script>

<style scoped>
button {
  transition: background 0.2s;
}
</style>
