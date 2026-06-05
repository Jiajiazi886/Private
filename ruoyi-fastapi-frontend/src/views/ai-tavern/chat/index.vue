<template>
  <div ref="chatPageRef" class="app-container tavern-chat">
    <el-aside class="side">
      <div class="side-header">
        <el-button type="primary" icon="Plus" @click="openConversationDialog">新建会话</el-button>
      </div>
      <el-tabs v-model="sideTab" stretch>
        <el-tab-pane label="会话" name="conversation">
          <div v-loading="conversationLoading" class="side-list">
            <div
              v-for="item in conversations"
              :key="item.id"
              :class="['side-item', currentConversationId === item.id ? 'active' : '']"
              @click="selectConversation(item.id)"
            >
              <div class="side-title">{{ item.title || '未命名会话' }}</div>
              <div class="side-desc">{{ item.characterName || '角色' }} · {{ item.totalMessageCount || 0 }} 条消息</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="角色" name="character">
          <div v-loading="characterLoading" class="side-list">
            <div v-for="item in characters" :key="item.id" class="side-item" @click="createByCharacter(item)">
              <div class="side-title">{{ item.name }}</div>
              <div class="side-desc">{{ item.description || '点击开始新会话' }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-aside>

    <el-main class="main">
      <div class="chat-header">
        <div>
          <div class="chat-title">{{ currentConversation?.title || 'AI 酒馆角色聊天' }}</div>
          <div class="chat-subtitle" v-if="currentConversation">
            {{ currentConversation.characterName || '角色' }} · 摘要版本 {{ currentConversation.summaryVersion || 0 }}
          </div>
        </div>
        <el-button :disabled="!currentConversationId || sending" icon="Refresh" @click="manualSummary">重建摘要</el-button>
      </div>

      <div ref="messageBoxRef" class="messages">
        <div v-if="!currentConversationId" class="empty">
          <el-icon size="44"><ChatDotRound /></el-icon>
          <p>选择角色或会话开始聊天</p>
        </div>
        <div v-for="item in messages" :key="item.id || item.localId" :class="['message', item.role]">
          <div class="bubble">
            <div class="message-meta">
              <span>{{ item.role === 'user' ? '我' : currentConversation?.characterName || '角色' }}</span>
              <span v-if="item.role === 'assistant' && item.latencyMs" class="latency">
                生成耗时 {{ formatLatency(item.latencyMs) }} 秒
              </span>
            </div>
            <div class="message-content">{{ item.content }}</div>
          </div>
        </div>
        <div v-if="sending" class="message assistant">
          <div class="bubble">
            <div class="message-meta">角色</div>
            <div class="message-content">正在回复...</div>
          </div>
        </div>
      </div>

      <div class="composer">
        <el-input
          v-model="input"
          type="textarea"
          :rows="3"
          resize="none"
          placeholder="输入消息，Enter 发送，Shift + Enter 换行"
          :disabled="!currentConversationId || sending"
          @keydown.enter.exact.prevent="send"
        />
        <div class="composer-actions">
          <span class="hint" v-if="lastSummaryTriggered">刚刚已触发长期摘要更新</span>
          <el-button type="primary" icon="Promotion" :loading="sending" :disabled="!input.trim() || !currentConversationId" @click="send">
            发送
          </el-button>
        </div>
      </div>
    </el-main>

    <el-dialog v-model="conversationDialogOpen" title="选择角色创建会话" width="560px" append-to-body>
      <el-table :data="characters" v-loading="characterLoading" @row-click="createByCharacter">
        <el-table-column label="角色" prop="name" width="140" />
        <el-table-column label="设定" prop="description" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <el-button class="scroll-top-float" type="primary" icon="ArrowUp" circle @click="scrollToTop" />
  </div>
</template>

<script setup name="AiTavernChat">
import {
  createConversation,
  listCharacters,
  listConversations,
  listMessages,
  rebuildSummary,
  sendChat,
} from '@/api/ai-tavern/tavern'

const { proxy } = getCurrentInstance()
const route = useRoute()

const sideTab = ref('conversation')
const characters = ref([])
const conversations = ref([])
const messages = ref([])
const input = ref('')
const sending = ref(false)
const characterLoading = ref(false)
const conversationLoading = ref(false)
const conversationDialogOpen = ref(false)
const currentConversationId = ref(undefined)
const chatPageRef = ref(null)
const messageBoxRef = ref(null)
const lastSummaryTriggered = ref(false)

const currentConversation = computed(() => conversations.value.find((item) => item.id === currentConversationId.value))

function loadCharacters() {
  characterLoading.value = true
  return listCharacters({ pageNum: 1, pageSize: 100, status: '0' }).then((response) => {
    characters.value = response.rows || []
    characterLoading.value = false
  })
}

function loadConversations() {
  conversationLoading.value = true
  return listConversations({ pageNum: 1, pageSize: 100, status: '0' }).then((response) => {
    conversations.value = response.rows || []
    conversationLoading.value = false
  })
}

function loadMessages(id) {
  if (!id) return
  listMessages(id).then((response) => {
    messages.value = response.data || []
    scrollToBottom()
  })
}

function selectConversation(id) {
  currentConversationId.value = id
  lastSummaryTriggered.value = false
  loadMessages(id)
}

function openConversationDialog() {
  conversationDialogOpen.value = true
  if (!characters.value.length) loadCharacters()
}

function createByCharacter(row) {
  if (!row?.id) return
  createConversation({ characterId: row.id }).then((response) => {
    conversationDialogOpen.value = false
    currentConversationId.value = response.data.id
    return loadConversations().then(() => loadMessages(response.data.id))
  })
}

function send() {
  const text = input.value.trim()
  if (!text || !currentConversationId.value) return
  const localMessage = { role: 'user', content: text, localId: Date.now() }
  messages.value.push(localMessage)
  input.value = ''
  sending.value = true
  lastSummaryTriggered.value = false
  scrollToBottom()
  sendChat({ conversationId: currentConversationId.value, content: text })
    .then((response) => {
      const data = response.data || {}
      if (data.message) messages.value.push(data.message)
      lastSummaryTriggered.value = Boolean(data.summaryTriggered)
      loadConversations()
      scrollToBottom()
    })
    .finally(() => {
      sending.value = false
    })
}

function manualSummary() {
  rebuildSummary(currentConversationId.value).then(() => {
    proxy.$modal.msgSuccess('摘要已更新')
    loadConversations()
  })
}

function formatLatency(latencyMs) {
  return (Number(latencyMs || 0) / 1000).toFixed(1)
}

function scrollToBottom() {
  nextTick(() => {
    if (messageBoxRef.value) {
      messageBoxRef.value.scrollTop = messageBoxRef.value.scrollHeight
    }
  })
}

function scrollToTop() {
  nextTick(() => {
    messageBoxRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
    const appMain = chatPageRef.value?.closest('.app-main')
    appMain?.scrollTo?.({ top: 0, behavior: 'smooth' })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })
}

onMounted(async () => {
  await Promise.all([loadCharacters(), loadConversations()])
  const id = Number(route.query.conversationId)
  if (id) {
    selectConversation(id)
  } else if (conversations.value.length) {
    selectConversation(conversations.value[0].id)
  }
})
</script>

<style scoped>
.tavern-chat {
  height: calc(100vh - 84px);
  padding: 0;
  display: flex;
  background: var(--el-bg-color-page);
}

.side {
  width: clamp(240px, 22vw, 320px);
  flex: 0 0 clamp(240px, 22vw, 320px);
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  overflow: hidden;
}

.side-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
}

.side-header .el-button {
  width: 100%;
}

.side-list {
  height: calc(100vh - 190px);
  overflow-y: auto;
  padding: 8px;
}

.side-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid transparent;
}

.side-item:hover {
  background: var(--el-fill-color-light);
}

.side-item.active {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
}

.side-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.side-desc {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.main {
  display: flex;
  flex-direction: column;
  padding: 0;
  min-width: 0;
}

.chat-header {
  height: 64px;
  padding: 0 20px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
}

.chat-subtitle {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty {
  height: 100%;
  color: var(--el-text-color-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.message {
  display: flex;
  margin-bottom: 16px;
}

.message.user {
  justify-content: flex-end;
}

.bubble {
  max-width: min(760px, 76%);
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
}

.message.user .bubble {
  background: var(--el-color-primary);
  color: #fff;
  border-color: var(--el-color-primary);
}

.message-meta {
  font-size: 12px;
  opacity: 0.72;
  margin-bottom: 6px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.latency {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.message.user .latency {
  color: rgba(255, 255, 255, 0.78);
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.65;
}

.composer {
  padding: 16px 20px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color);
}

.composer-actions {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: var(--el-color-success);
  font-size: 13px;
}

.scroll-top-float {
  position: fixed;
  right: 24px;
  bottom: 96px;
  z-index: 2000;
  width: 44px;
  height: 44px;
  box-shadow: var(--el-box-shadow-light);
}

@media (max-width: 980px) {
  .tavern-chat {
    height: auto;
    min-height: calc(100vh - 84px);
    flex-direction: column;
  }

  .side {
    width: 100%;
    flex: none;
    border-right: 0;
    border-bottom: 1px solid var(--el-border-color);
  }

  .side-header {
    padding: 12px;
  }

  .side-list {
    height: auto;
    max-height: 220px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 8px;
    overflow-y: auto;
  }

  .side-item {
    min-width: 0;
  }

  .main {
    min-height: 560px;
  }
}

@media (max-width: 640px) {
  .side-list {
    grid-template-columns: 1fr;
    max-height: 240px;
  }

  .chat-header {
    height: auto;
    min-height: 64px;
    padding: 12px;
    align-items: flex-start;
    gap: 10px;
  }

  .messages {
    padding: 12px;
  }

  .bubble {
    max-width: 92%;
  }

  .composer {
    padding: 12px;
  }

  .scroll-top-float {
    right: 16px;
    bottom: 76px;
  }
}
</style>
