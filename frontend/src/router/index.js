import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Main from '../views/Main.vue'

const routes = [
    { path: '/', redirect: '/main' },
    { path: '/login', component: Login },
    { path: '/main', component: Main, meta: { requiresAuth: true } }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})



export default router
