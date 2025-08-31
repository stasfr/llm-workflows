<script setup lang="ts">
import { ref } from 'vue'
import { useWordLists } from '@/composables/useWordLists'

const data = ref<[string, number][] | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const { 
  garbagePrasesList, 
  garbagePostsList, 
  exceptions, 
  wordOffset, 
  addToGarbagePrases, 
  addToGarbagePosts, 
  addToExceptions 
} = useWordLists()

function handleAddToList(addFunction: (word: string) => void, word: string) {
  addFunction(word)
  if (data.value) {
    data.value = data.value.filter(([itemWord]) => itemWord !== word)
  }
}

async function fetchData(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const body = {
      garbagePrasesList: garbagePrasesList.value,
      garbagePostsList: garbagePostsList.value,
      exceptions: exceptions.value,
      wordOffset: wordOffset.value
    }

    const response = await fetch('http://localhost:3000/filter-parsed-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json = await response.json();
    data.value = json.result;
  } catch (e) {
    console.error('Error fetching data:', e);
    if (e instanceof Error) {
        error.value = e.message;
    } else {
        error.value = 'An unknown error occurred.';
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-neutral-800 h-full text-white font-sans">
    <div class="container mx-auto p-8">
      <div class="flex justify-center items-center mb-8 space-x-4">
        <div>
          <label for="wordOffset" class="block text-sm font-medium text-gray-400 mb-1">Word Offset</label>
          <input type="number" id="wordOffset" v-model.number="wordOffset" class="bg-neutral-700 border border-neutral-600 text-white text-lg rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-24 p-2.5 text-center">
        </div>
        <button @click="fetchData" :disabled="loading" class="self-end bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 disabled:bg-gray-500 disabled:cursor-not-allowed disabled:transform-none">
          {{ loading ? 'Analyzing...' : 'Fetch Word Frequencies' }}
        </button>
      </div>

      <div v-if="loading" class="text-center text-gray-400">
        <p>Loading data from the server...</p>
      </div>

      <div v-if="error" class="bg-red-900 border border-red-400 text-red-100 px-4 py-3 rounded-lg relative text-center" role="alert">
        <strong class="font-bold">Error:</strong>
        <span class="block sm:inline">{{ error }}</span>
      </div>

      <div v-if="!data && !loading && !error" class="text-center text-gray-500">
        <p>Click the button to fetch and display word frequencies.</p>
      </div>

      <div v-if="data && data.length > 0" class="bg-neutral-900 shadow-2xl rounded-xl p-6 max-w-7xl mx-auto">
        <ul class="space-y-3">
          <li v-for="([word, count], index) in data" :key="index" class="flex justify-between items-center border-b border-neutral-700 pb-3 last:border-b-0">
            <div class="flex items-center">
                <span class="text-lg font-semibold bg-indigo-500 text-white rounded-full px-3 py-1 mr-4">{{ count }}</span>
                <span class="text-lg text-gray-300">{{ JSON.stringify(word).slice(1, -1) }}</span>
            </div>
            <div class="flex space-x-2">
                <button @click="handleAddToList(addToGarbagePosts, word)" class="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded-md text-sm transition-colors">To Posts</button>
                <button @click="handleAddToList(addToGarbagePrases, word)" class="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-1 px-3 rounded-md text-sm transition-colors">To Phrases</button>
                <button @click="handleAddToList(addToExceptions, word)" class="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded-md text-sm transition-colors">To Exceptions</button>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="data && data.length === 0" class="text-center text-gray-500 mt-6">
        <p>No data was returned from the server or all items have been categorized.</p>
      </div>

    </div>
  </div>
</template>