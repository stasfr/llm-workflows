<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
import { useWordLists } from '@/composables/useWordLists'

const { garbagePrasesList, garbagePostsList, exceptions, wordOffset } = useWordLists()

function exportToJson() {
  const dataToExport = {
    garbagePrasesList: garbagePrasesList.value,
    garbagePostsList: garbagePostsList.value,
    exceptions: exceptions.value,
    wordOffset: wordOffset.value
  }

  const jsonString = JSON.stringify(dataToExport, null, 2)
  const blob = new Blob([jsonString], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'analyzer-settings.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="bg-neutral-800 min-h-screen text-white font-sans">
    <header class="bg-neutral-900 shadow-lg">
      <nav class="container mx-auto px-8 py-4 flex justify-between items-center">
        <RouterLink to="/" class="text-2xl font-bold text-white hover:text-indigo-400 transition-colors">Analyzer</RouterLink>
        <ul class="flex items-center space-x-6">
          <li><RouterLink to="/" class="text-lg text-gray-300 hover:text-white transition-colors">Main</RouterLink></li>
          <li><RouterLink to="/exceptions" class="text-lg text-gray-300 hover:text-white transition-colors">Exceptions</RouterLink></li>
          <li><RouterLink to="/garbage-posts" class="text-lg text-gray-300 hover:text-white transition-colors">Garbage Posts</RouterLink></li>
          <li><RouterLink to="/garbage-prases" class="text-lg text-gray-300 hover:text-white transition-colors">Garbage Phrases</RouterLink></li>
          <li>
            <button @click="exportToJson" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Export JSON
            </button>
          </li>
        </ul>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>
