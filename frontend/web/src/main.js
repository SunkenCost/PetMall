import { createApp } from 'vue'
import VueAxios from 'vue-axios'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from './axios'
import base from './components/Base'
import footer from './components/Footer'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入所有图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/style.css' // 全局现代 CSS

// 创建Vue对象
const app = createApp(App)

// 注册 Element Plus 和所有图标
app.use(ElementPlus)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册组件
app.component('base-page', base)
app.component('footer-page', footer)
// 将路由对象绑定到Vue对象
app.use(router)
app.use(store)
// 将vue-axios与axios关联并绑定到Vue对象
app.use(VueAxios, axios)
// 挂载使用Vue对象
app.mount('#app')
