import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/pages/MainPage.vue'
import ExceptionsList from '@/pages/ExceptionsList.vue'
import GarbagePostsList from '@/pages/GarbagePostsList.vue'
import GarbagePrasesList from '@/pages/GarbagePrasesList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'MainPage',
      component: MainPage
    },
    {
      path: '/exceptions',
      name: 'ExceptionsList',
      component: ExceptionsList
    },
    {
      path: '/garbage-posts',
      name: 'GarbagePostsList',
      component: GarbagePostsList
    },
    {
      path: '/garbage-prases',
      name: 'GarbagePrasesList',
      component: GarbagePrasesList
    }
  ],
})

export default router
