<script setup lang="ts">
import { computed, ref } from 'vue'
import { useWordLists } from '@/composables/useWordLists'

const props = defineProps<{
  title: string
  listKey: 'exceptions' | 'garbagePostsList' | 'garbagePrasesList'
}>()

const { 
  exceptions, 
  garbagePostsList, 
  garbagePrasesList, 
  removeFromExceptions, 
  removeFromGarbagePosts, 
  removeFromGarbagePrases,
  clearExceptions,
  clearGarbagePosts,
  clearGarbagePrases,
  addToExceptions,
  addToGarbagePosts,
  addToGarbagePrases
} = useWordLists()

const listMap = {
  exceptions: {
    items: exceptions,
    remove: removeFromExceptions,
    clear: clearExceptions,
    add: addToExceptions
  },
  garbagePostsList: {
    items: garbagePostsList,
    remove: removeFromGarbagePosts,
    clear: clearGarbagePosts,
    add: addToGarbagePosts
  },
  garbagePrasesList: {
    items: garbagePrasesList,
    remove: removeFromGarbagePrases,
    clear: clearGarbagePrases,
    add: addToGarbagePrases
  }
}

const currentList = computed(() => listMap[props.listKey])
const newItem = ref('')

function handleAddItem() {
  if (newItem.value) {
    // Unescape special characters so that what the user types is what is stored.
    // For example, if the user types the two characters \ and n,
    // we want to store a single newline character.
    const unescapedItem = newItem.value
      .replace(/\\n/g, '\n')
      .replace(/\\r/g, '\r')
      .replace(/\\t/g, '\t')
      .replace(/\\\\/g, '\\'); // Important: handle escaped backslash last

    currentList.value.add(unescapedItem);
    newItem.value = '';
  }
}
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold text-gray-100">{{ title }}</h1>
      <button v-if="currentList.items.value.length > 0" @click="currentList.clear" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
        Clear All
      </button>
    </div>

    <div class="mb-8 max-w-3xl mx-auto">
      <form @submit.prevent="handleAddItem" class="flex space-x-2">
        <input 
          type="text" 
          v-model="newItem" 
          class="bg-neutral-700 border border-neutral-600 text-white text-lg rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5"
          :placeholder="`Add new item to ${title}`"
        >
        <button 
          type="submit" 
          class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
        >
          Add
        </button>
      </form>
    </div>

    <div v-if="currentList.items.value.length === 0" class="text-center text-gray-500">
      <p>This list is empty.</p>
    </div>

    <div v-else class="bg-neutral-900 shadow-2xl rounded-xl p-6 max-w-3xl mx-auto">
      <ul class="space-y-3">
        <li v-for="(item, index) in currentList.items.value" :key="index" class="flex justify-between items-center border-b border-neutral-700 pb-3 last:border-b-0">
          <span class="text-lg text-gray-300">{{ JSON.stringify(item).slice(1, -1) }}</span>
          <button @click="currentList.remove(item)" class="bg-red-800 hover:bg-red-900 text-white font-bold py-1 px-3 rounded-md text-sm transition-colors">
            Remove
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>