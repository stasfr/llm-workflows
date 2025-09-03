import { ref, onMounted, watch } from 'vue'

// Helper function to create a ref that syncs with localStorage
function useStorage<T>(key: string, defaultValue: T) {
  const storedValue = localStorage.getItem(key)
  const data = ref<T>(storedValue ? JSON.parse(storedValue) : defaultValue)

  watch(data, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue))
  }, { deep: true })

  return data
}

// The composable that manages all shared state
export function useWordLists() {
  const garbagePrasesList = useStorage<string[]>('garbagePrasesList', [])
  const garbagePostsList = useStorage<string[]>('garbagePostsList', [])
  const exceptions = useStorage<string[]>('exceptions', [])
  const wordOffset = useStorage<number>('wordOffset', 3)

  function addToList(list: ref<string[]>, word: string) {
    if (!list.value.includes(word)) {
      list.value.push(word)
    }
  }

  function removeFromList(list: ref<string[]>, word: string) {
    list.value = list.value.filter(item => item !== word)
  }

  function clearList(list: ref<string[]>) {
    list.value = []
  }

  return {
    garbagePrasesList,
    garbagePostsList,
    exceptions,
    wordOffset,
    addToGarbagePrases: (word: string) => addToList(garbagePrasesList, word),
    addToGarbagePosts: (word: string) => addToList(garbagePostsList, word),
    addToExceptions: (word: string) => addToList(exceptions, word),
    removeFromGarbagePrases: (word: string) => removeFromList(garbagePrasesList, word),
    removeFromGarbagePosts: (word: string) => removeFromList(garbagePostsList, word),
    removeFromExceptions: (word: string) => removeFromList(exceptions, word),
    clearGarbagePrases: () => clearList(garbagePrasesList),
    clearGarbagePosts: () => clearList(garbagePostsList),
    clearExceptions: () => clearList(exceptions),
  }
}
