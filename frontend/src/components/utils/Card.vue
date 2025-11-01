<template>
    <span v-if="showFullName" class="px-3 py-2 bg-gray-700 rounded-xl border border-sky-600 text-sky-100 text-sm">
        <slot name="name"></slot> <span class="text-gray-400 text-xs">(<slot name="full-name"></slot>)</span>
    </span>
    
    <span v-else class="px-3 py-2 bg-gray-700 rounded-xl border border-sky-600 text-sky-100 text-sm">
        <slot name="header"></slot>
    </span>
</template>

<script>
export default {
    name: "Card",
    props: {
        showFullName: {
            type: Boolean,
            default: false,
        }
    },
}
</script>