import { createRouter, createWebHistory } from 'vue-router'
import Result from '@/views/Result.vue'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
  { path: '/result', name: 'result', component: Result },
  {path: '/home', name:'home', component: Home},
],
})
export default router
