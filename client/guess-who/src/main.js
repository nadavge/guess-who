import { createApp } from 'vue'
import App from './App.vue'
import { config } from './config';

const app = createApp(App)
    .provide('api_url', config.api_url)
    .mount("#app")

console.log(app.config)
