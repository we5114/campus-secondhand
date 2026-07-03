<template>
  <div class="ai-service-page">
    <div class="chat-container">
      <!-- 头部 -->
      <header class="chat-header">
        <div class="header-left">
          <el-button text @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <div class="avatar">
            <span class="avatar-icon">🤖</span>
          </div>
          <div class="info">
            <h3>智能客服助手</h3>
            <span class="status">在线</span>
          </div>
        </div>
      </header>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-avatar">
            <span v-if="msg.role === 'user'" class="avatar-icon">👤</span>
            <span v-else class="avatar-icon">🤖</span>
          </div>
          <div class="message-content">
            <div class="message-bubble">
              {{ msg.content }}
            </div>
            <div class="message-time">
              {{ msg.time }}
            </div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="message-item ai">
          <div class="message-avatar">
            <span class="avatar-icon">🤖</span>
          </div>
          <div class="message-content">
            <div class="message-bubble loading">
              <span class="dot">.</span>
              <span class="dot">.</span>
              <span class="dot">.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <footer class="chat-input">
        <el-input
          v-model="inputMessage"
          placeholder="输入您的问题，按 Enter 发送..."
          size="large"
          :disabled="sending"
          @keyup.enter="sendMessage"
        >
          <template #append>
            <el-button
              type="primary"
              :disabled="!inputMessage.trim() || sending"
              @click="sendMessage"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </template>
        </el-input>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { llmApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Promotion } from '@element-plus/icons-vue'

const messageListRef = ref(null)
const loading = ref(false)
const sending = ref(false)
const inputMessage = ref('')

const messages = reactive([
  {
    role: 'ai',
    content: '您好！我是校园二手交易平台的智能客服助手，有什么可以帮您的吗？😊',
    time: getCurrentTime()
  }
])

function getCurrentTime() {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

async function sendMessage() {
  if (!inputMessage.value.trim() || sending.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.push({
    role: 'user',
    content: userMessage,
    time: getCurrentTime()
  })
  scrollToBottom()

  // 调用 AI 接口
  loading.value = true
  sending.value = true

  try {
    const data = await llmApi.chatWithAI({
      message: userMessage,
      history: messages.filter(m => m.role !== 'system').map(m => ({
        role: m.role === 'ai' ? 'assistant' : m.role,
        content: m.content
      }))
    })

    messages.push({
      role: 'ai',
      content: data.content || '抱歉，我现在无法回答您的问题。',
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('AI 对话失败:', error)
    messages.push({
      role: 'ai',
      content: '抱歉，连接失败了，请稍后再试。',
      time: getCurrentTime()
    })
  } finally {
    loading.value = false
    sending.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style lang="scss" scoped>
.ai-service-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.chat-container {
  max-width: 800px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .avatar {
    .avatar-icon {
      font-size: 32px;
    }
  }

  .info {
    h3 {
      margin: 0;
      font-size: 16px;
      color: #333;
    }

    .status {
      font-size: 12px;
      color: #67c23a;
    }
  }
}

.message-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;

  &.user {
    flex-direction: row-reverse;

    .message-bubble {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
    }

    .message-content {
      align-items: flex-end;
    }
  }

  &.ai {
    .message-bubble {
      background: #f0f2f5;
      color: #333;
    }
  }

  .avatar-icon {
    font-size: 28px;
    flex-shrink: 0;
  }

  .message-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-width: 70%;

    .message-bubble {
      padding: 12px 16px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.6;
      word-wrap: break-word;

      &.loading {
        display: flex;
        gap: 4px;
        padding: 16px 20px;

        .dot {
          animation: bounce 1.4s infinite;
          font-size: 18px;
          color: #999;
        }

        .dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .dot:nth-child(3) {
          animation-delay: 0.4s;
        }
      }
    }

    .message-time {
      font-size: 12px;
      color: #999;
    }
  }
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: #fff;

  :deep(.el-input-group__append) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: #fff;
  }
}
</style>
