import { createApp } from 'vue'
import App from './App.vue'
import { config } from './config';

const app = createApp(App)
app.provide('api_url', config.api_url)
app.mount('#app')

console.log(app.config)
