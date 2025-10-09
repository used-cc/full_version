import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// 确保使用createApp创建实例
const app = createApp(App)
app.config.globalProperties.$router = router
app.use(ElementPlus)
app.use(router)
app.mount('#app')
