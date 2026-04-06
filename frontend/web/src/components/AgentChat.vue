<template>
  <div class="agent-container" :style="{ right: position.right + 'px', bottom: position.bottom + 'px' }">
    <!-- Floating Button -->
    <div 
      class="agent-fab" 
      @mousedown="handleMouseDown"
      @click="handleClick"
      :class="{ 'active': isChatOpen, 'dragging': isDragging }"
    >
      <img v-if="!isChatOpen" src="https://img.icons8.com/color/96/bot.png" class="fab-robot-icon" />
      <el-icon v-else :size="28"><Close /></el-icon>
    </div>

    <!-- Chat Box -->
    <transition name="chat-fade">
      <div v-if="isChatOpen" class="agent-window">
        <div class="agent-header">
          <div class="header-left">
            <el-avatar :size="32" src="https://img.icons8.com/color/48/bot.png" />
            <div class="header-info">
              <span class="bot-name">小宠 (AI 助手)</span>
              <span class="bot-status"><span class="dot"></span> 在线中</span>
            </div>
          </div>
          <el-icon class="close-btn" @click="isChatOpen = false"><SemiSelect /></el-icon>
        </div>

        <el-scrollbar ref="scrollbar" class="agent-body">
          <div class="chat-messages" ref="messageList">
            <!-- Welcome Message -->
            <div class="message-row bot">
              <el-avatar :size="32" src="https://img.icons8.com/color/48/bot.png" />
              <div class="message-bubble bot" v-html="renderMarkdown('你好呀！我是你的掌上宠物管家“小宠”🐾。我可以帮你挑选宠物粮、建议养宠知识，或者直接搜罗商城的宝贝。如果你还没有建立宠物档案，一定要去[这里](/#/pets)完善信息哦！有什么能帮到你的吗？')"></div>
            </div>

            <!-- Chat History -->
            <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
              <template v-if="msg.role === 'assistant'">
                <el-avatar :size="32" src="https://img.icons8.com/color/48/bot.png" />
                <div class="message-bubble assistant" v-html="renderMarkdown(msg.content)"></div>
              </template>
              <template v-else-if="msg.role === 'user'">
                <div class="message-bubble user">{{ msg.content }}</div>
                <el-avatar :size="32" src="https://img.icons8.com/fluency/48/user-male-circle.png" />
              </template>
            </div>

            <!-- Loading Indicator -->
            <div v-if="loading" class="message-row bot">
              <el-avatar :size="32" src="https://img.icons8.com/color/48/bot.png" />
              <div class="message-bubble bot loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          </div>
        </el-scrollbar>
        
        <!-- Suggestions Area -->
        <div v-if="suggestions.length > 0 && !loading" class="suggestion-area">
          <div class="suggestion-chips">
            <span 
              v-for="sug in suggestions" 
              :key="sug" 
              class="chip"
              @click="handleSuggestion(sug)"
            >
              {{ sug }}
            </span>
          </div>
        </div>

        <div class="agent-footer">
          <el-input
            v-model="userInput"
            placeholder="问问我‘有什么好的金毛犬粮推荐？’"
            @keyup.enter="handleSend"
            :disabled="loading"
          >
            <template #append>
              <el-button @click="handleSend" :disabled="loading || !userInput.trim()">
                发送
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import axios from '@/axios'
import { Close, SemiSelect } from '@element-plus/icons-vue'
import marked from 'marked'

export default {
  name: 'AgentChat',
  components: { Close, SemiSelect },
  setup() {
    const isChatOpen = ref(false)
    const userInput = ref('')
    const loading = ref(false)
    const messages = ref([]) 
    const scrollbar = ref(null)

    // Position & Dragging state
    const position = ref({ right: 30, bottom: 30 })
    const isDragging = ref(false)
    let startMousePos = { x: 0, y: 0 }
    let startFabPos = { right: 0, bottom: 0 }
    let hasMoved = false

    const suggestions = ref([
      '有哪些热销猫粮推荐？',
      '我家金毛子适合吃什么？',
      '如何推荐一款宠物零食？',
      '如何给狗狗剪指甲？',
      '三月大的边牧如何喂养？'
    ])

    const handleMouseDown = (e) => {
      isDragging.value = true
      hasMoved = false
      startMousePos = { x: e.clientX, y: e.clientY }
      startFabPos = { right: position.value.right, bottom: position.value.bottom }
      
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }

    const handleMouseMove = (e) => {
      const dx = e.clientX - startMousePos.x
      const dy = e.clientY - startMousePos.y
      
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        hasMoved = true
      }

      // Calculate new right/bottom
      let newRight = startFabPos.right - dx
      let newBottom = startFabPos.bottom - dy

      // Boundary checks
      const margin = 20
      newRight = Math.max(margin, Math.min(window.innerWidth - 80, newRight))
      newBottom = Math.max(margin, Math.min(window.innerHeight - 80, newBottom))

      position.value = { right: newRight, bottom: newBottom }
    }

    const handleMouseUp = () => {
      isDragging.value = false
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    const handleClick = () => {
      if (!hasMoved) {
        toggleChat()
      }
    }

    const handleSuggestion = (text) => {
      userInput.value = text
      handleSend()
    }

    const toggleChat = () => {
      isChatOpen.value = !isChatOpen.value
      if (isChatOpen.value) {
        scrollToBottom()
      }
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (scrollbar.value) {
          const wrap = scrollbar.value.$el.querySelector('.el-scrollbar__wrap')
          wrap.scrollTop = wrap.scrollHeight
        }
      })
    }

    const renderMarkdown = (text) => {
      try {
        return marked(text)
      } catch {
        return text
      }
    }

    const handleSend = async () => {
      if (!userInput.value.trim() || loading.value) return

      const text = userInput.value
      messages.value.push({ role: 'user', content: text })
      userInput.value = ''
      loading.value = true
      scrollToBottom()

      try {
        const history = messages.value.map(m => ({ 
          role: m.role === 'assistant' ? 'assistant' : 'user', 
          content: m.content 
        }))

        const res = await axios.post('/api/agent/chat/', {
          message: text,
          history: history.slice(0, -1) // Send history excluding the latest user msg
        })

        if (res.data && res.data.reply) {
          messages.value.push({ role: 'assistant', content: res.data.reply })
        }
      } catch (err) {
        console.error('Agent chat error:', err)
        messages.value.push({ 
          role: 'assistant', 
          content: '😭 对不起，我的网络连接好像被打断了，请检查网络或稍后再试。' 
        })
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    return {
      isChatOpen, userInput, loading, messages, scrollbar,
      position, isDragging, suggestions,
      handleMouseDown, handleClick, handleSuggestion, handleSend, renderMarkdown
    }
  }
}
</script>

<style scoped>
/* Container & FAB */
.agent-container {
  position: fixed;
  z-index: 5000;
  width: 65px;
  height: 65px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica;
  user-select: none;
}

.agent-fab {
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 10px 25px rgba(118, 75, 162, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
  color: white;
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s, background 0.3s;
}

.agent-fab:active {
  cursor: grabbing;
}

.agent-fab.dragging {
  transition: none;
}

.fab-robot-icon {
  width: 45px;
  height: 45px;
  object-fit: contain;
}

.agent-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 15px 30px rgba(118, 75, 162, 0.6);
}

.agent-fab.active {
  background: #ff5e5e;
  cursor: pointer;
}

/* Chat Window */
.agent-window {
  position: absolute;
  right: 0;
  bottom: 80px;
  width: 380px;
  height: 550px;
  background: white;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 15px 50px rgba(0,0,0,0.15);
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

/* Header */
.agent-header {
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.bot-name {
  font-weight: bold;
  font-size: 15px;
  color: #333;
}

.bot-status {
  font-size: 12px;
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  background: #67c23a;
  border-radius: 50%;
  box-shadow: 0 0 5px #67c23a;
}

.close-btn {
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #333;
}

/* Body */
.agent-body {
  flex: 1;
  padding: 20px;
  background: #f9fafb;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-row {
  display: flex;
  gap: 12px;
  max-width: 90%;
}

.message-row :deep(.el-avatar) {
  flex-shrink: 0;
}

.message-row.user {
  align-self: flex-end;
  justify-content: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  word-break: break-word;
}

.message-bubble.bot, .message-bubble.assistant {
  background: white;
  color: #444;
  border-bottom-left-radius: 4px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.03);
  border: 1px solid #eee;
}

.message-bubble.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

/* Suggestions */
.suggestion-area {
  padding: 8px 15px;
  background: #f9fafb;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 5px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 12px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chip:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  transform: translateY(-1px);
}

/* Footer */
.agent-footer {
  padding: 15px 20px;
  background: white;
  border-top: 1px solid #f5f5f5;
}

/* Transitions */
.chat-fade-enter-active, .chat-fade-leave-active {
  transition: all 0.3s ease;
}

.chat-fade-enter-from, .chat-fade-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

/* Markdown Styling */
:deep(.message-bubble) p {
  margin: 0 0 10px 0;
}
:deep(.message-bubble) p:last-child {
  margin: 0;
}
:deep(.message-bubble) strong {
  color: #000;
}
:deep(.message-bubble.user) strong {
  color: #fff;
}

:deep(.message-bubble) a {
  color: #667eea;
  text-decoration: underline;
  font-weight: bold;
}

:deep(.message-bubble) a:hover {
  color: #764ba2;
}

/* Loading Dots Animation */
.loading-dots span {
  animation: loading-fade 1s infinite alternate;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes loading-fade {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
