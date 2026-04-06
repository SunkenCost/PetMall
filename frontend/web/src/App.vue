<template>
  <el-config-provider>
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <!-- 全局 AI 助手 -->
    <AgentChat />
  </el-config-provider>
</template>

<script>
import AgentChat from './components/AgentChat.vue'

export default {
  name: 'App',
  components: {
    AgentChat
  }
}
</script>

<style>
/* CSS handled globally in style.css */
</style>
