// src/router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../components/views/Home.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      name: 'home',
      component: Home
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('../components/views/Analysis.vue')
    },
    {
      path: '/browsemain',
      name: 'browsemain',
      component: () => import('../components/views/Browsemain.vue')
    },
    {
      path: '/browsepre',
      name: 'browsepre',
      component: () => import('../components/views/Browsepre.vue')
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../components/views/Statistics.vue')
    },
    {
      path: '/help',
      name: 'help',
      component: () => import('../components/views/Help.vue')
    },
    {
      path: '/download',
      name: 'download',
      component: () => import('../components/views/Download.vue')
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../components/views/Contact.vue')
    },{
      path: '/result/:job_id',
      name: 'result',
      component: () => import('../components/views/Result.vue'),
      props: true
    },
    {
      path: '/browse/:protein_id',
      name: 'browse',
      component: () => import('../components/views/Browse.vue'),
      props: true
    }
  ]
})

export default router
