<template>
  <div
    ref="chatPageRef"
    :class="['app-container tavern-chat', mobileView === 'list' ? 'mobile-list' : 'mobile-detail']"
  >
    <el-aside class="side">
      <div class="mobile-list-title">角色对话</div>
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
              <div class="side-row">
                <div class="side-title">{{ item.title || '未命名会话' }}</div>
                <el-button
                  class="side-edit"
                  link
                  icon="Edit"
                  title="编辑对话提示词"
                  @click.stop="openConversationSettings(item.id)"
                />
              </div>
              <div class="side-desc">{{ item.characterName || '角色' }} · {{ item.totalMessageCount || 0 }} 条消息</div>
              <div v-if="item.conversationPrompt" class="side-prompt">已设置对话提示词</div>
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
        <el-button class="mobile-back" text icon="ArrowLeft" @click="backToList" />
        <div class="chat-heading">
          <div class="chat-title">{{ currentConversation?.title || 'AI 酒馆角色聊天' }}</div>
          <div class="chat-subtitle" v-if="currentConversation">
            {{ currentConversation.characterName || '角色' }} · 摘要版本 {{ currentConversation.summaryVersion || 0 }}
          </div>
        </div>
        <el-button text icon="MoreFilled" class="header-more" @click="toggleActionPanel" />
      </div>

      <div ref="messageBoxRef" class="messages">
        <div v-if="!currentConversationId" class="empty">
          <el-icon size="44"><ChatDotRound /></el-icon>
          <p>选择角色或会话开始聊天</p>
        </div>

        <div v-for="item in messages" :key="item.id || item.localId" :class="['message', item.role]">
          <div v-if="item.role !== 'user'" class="avatar assistant-avatar">{{ assistantInitial }}</div>
          <div class="bubble-wrap">
            <div class="message-meta">
              <span>{{ item.role === 'user' ? '我' : currentConversation?.characterName || '角色' }}</span>
              <span v-if="item.role === 'assistant' && item.latencyMs" class="latency">
                生成耗时 {{ formatLatency(item.latencyMs) }} 秒
              </span>
              <span v-if="item.isEdited" class="edited">已编辑</span>
              <el-button
                v-if="editMode && item.id"
                link
                size="small"
                icon="Edit"
                class="inline-edit"
                @click="openEditMessage(item)"
              >
                编辑
              </el-button>
            </div>
            <div class="bubble">
              <div class="message-content">{{ item.content }}</div>
            </div>
          </div>
          <div v-if="item.role === 'user'" class="avatar user-avatar">我</div>
        </div>

        <div v-if="sending" class="message assistant">
          <div class="avatar assistant-avatar">{{ assistantInitial }}</div>
          <div class="bubble-wrap">
            <div class="message-meta">角色</div>
            <div class="bubble">
              <div class="message-content">正在回复...</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="actionPanelOpen" class="action-panel">
        <button v-for="action in actionItems" :key="action.key" class="action-item" type="button" @click="runAction(action.key)">
          <span class="action-icon">
            <el-icon><component :is="action.icon" /></el-icon>
          </span>
          <span>{{ action.label }}</span>
        </button>
      </div>

      <div class="composer">
        <div class="composer-row">
          <el-input
            v-model="input"
            type="textarea"
            :rows="2"
            resize="none"
            placeholder="输入消息，Enter 发送，Shift + Enter 换行"
            :disabled="!currentConversationId || sending"
            @keydown.enter.exact.prevent="send"
          />
          <el-button
            class="plus-button"
            circle
            icon="Plus"
            :disabled="!currentConversationId"
            @click="toggleActionPanel"
          />
        </div>
        <div class="composer-actions">
          <span class="hint" v-if="lastSummaryTriggered">刚刚已触发长期摘要更新</span>
          <span class="hint edit-hint" v-else-if="editMode">历史消息编辑已开启</span>
          <el-button
            type="primary"
            icon="Promotion"
            :loading="sending"
            :disabled="!input.trim() || !currentConversationId"
            @click="send"
          >
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

    <el-dialog v-model="settingsDialogOpen" title="对话设置" width="640px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="会话标题">
          <el-input v-model="conversationForm.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="对话专属提示词">
          <el-input
            v-model="conversationForm.conversationPrompt"
            type="textarea"
            :rows="8"
            resize="vertical"
            placeholder="只影响当前这一个会话。适合写本次对话规则、剧情方向、称呼、禁忌等。"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settingsDialogOpen = false">取消</el-button>
        <el-button type="primary" @click="saveConversationSettings">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="summaryDialogOpen" title="会话摘要" width="700px" append-to-body>
      <el-alert
        title="摘要会作为长期剧情记忆发送给 AI。你可以手动修改，也可以重新生成。"
        type="info"
        show-icon
        :closable="false"
      />
      <el-input
        v-model="summaryForm.summary"
        class="dialog-textarea"
        type="textarea"
        :rows="12"
        resize="vertical"
        placeholder="当前会话还没有摘要"
      />
      <template #footer>
        <el-button :loading="summaryRebuilding" icon="Refresh" @click="manualSummary">重建摘要</el-button>
        <el-button @click="summaryDialogOpen = false">取消</el-button>
        <el-button type="primary" @click="saveSummary">保存摘要</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="memoryDialogOpen" title="强制记忆" width="640px" append-to-body>
      <el-alert
        title="强制记忆会以最高优先级提示词发给 AI，用于固定事实、关系、设定或纠正记忆错误。"
        type="warning"
        show-icon
        :closable="false"
      />
      <el-input
        v-model="memoryForm.forcedMemory"
        class="dialog-textarea"
        type="textarea"
        :rows="10"
        resize="vertical"
        placeholder="例如：必须记住，用户叫……；角色和用户的关系是……；之前某个回复是错误的，正确设定是……"
      />
      <template #footer>
        <el-button @click="memoryDialogOpen = false">取消</el-button>
        <el-button type="primary" @click="saveMemory">保存强制记忆</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="messageDialogOpen" title="编辑消息内容" width="640px" append-to-body>
      <el-input
        v-model="messageForm.content"
        type="textarea"
        :rows="10"
        resize="vertical"
        placeholder="修改这条历史消息内容"
      />
      <template #footer>
        <el-button @click="messageDialogOpen = false">取消</el-button>
        <el-button type="primary" @click="saveMessage">保存消息</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AiTavernChat">
import {
  ChatLineSquare,
  CollectionTag,
  EditPen,
  Memo,
  Plus,
  Refresh,
  Setting,
  Top,
} from '@element-plus/icons-vue'
import {
  createConversation,
  getConversation,
  listCharacters,
  listConversations,
  listMessages,
  rebuildSummary,
  sendChat,
  updateConversation,
  updateMessage,
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
const conversationDetail = ref(null)
const chatPageRef = ref(null)
const messageBoxRef = ref(null)
const lastSummaryTriggered = ref(false)
const actionPanelOpen = ref(false)
const mobileView = ref('list')
const editMode = ref(false)
const summaryRebuilding = ref(false)
const settingsTargetConversationId = ref(undefined)
const immersiveBodyClass = 'ai-tavern-mobile-chat-immersive'

const settingsDialogOpen = ref(false)
const summaryDialogOpen = ref(false)
const memoryDialogOpen = ref(false)
const messageDialogOpen = ref(false)

const conversationForm = reactive({
  title: '',
  conversationPrompt: '',
})
const summaryForm = reactive({
  summary: '',
})
const memoryForm = reactive({
  forcedMemory: '',
})
const messageForm = reactive({
  id: undefined,
  content: '',
})

const currentConversation = computed(() => {
  if (conversationDetail.value?.id === currentConversationId.value) return conversationDetail.value
  return conversations.value.find((item) => item.id === currentConversationId.value)
})

const assistantInitial = computed(() => (currentConversation.value?.characterName || 'AI').slice(0, 1))

const actionItems = computed(() => [
  { key: 'settings', label: '提示词', icon: Setting },
  { key: 'summary', label: '摘要', icon: Memo },
  { key: 'memory', label: '强制记忆', icon: CollectionTag },
  { key: 'edit-last', label: '改AI回复', icon: EditPen },
  { key: 'edit-mode', label: editMode.value ? '关闭编辑' : '历史编辑', icon: ChatLineSquare },
  { key: 'rebuild-summary', label: '重建摘要', icon: Refresh },
  { key: 'new-chat', label: '新建会话', icon: Plus },
  { key: 'top', label: '回到顶部', icon: Top },
])

function loadCharacters() {
  characterLoading.value = true
  return listCharacters({ pageNum: 1, pageSize: 100, status: '0' })
    .then((response) => {
      characters.value = response.rows || []
    })
    .finally(() => {
      characterLoading.value = false
    })
}

function loadConversations() {
  conversationLoading.value = true
  return listConversations({ pageNum: 1, pageSize: 100, status: '0' })
    .then((response) => {
      conversations.value = response.rows || []
      if (currentConversationId.value) {
        const latest = conversations.value.find((item) => item.id === currentConversationId.value)
        if (latest && conversationDetail.value) {
          conversationDetail.value = { ...conversationDetail.value, ...latest }
        }
      }
    })
    .finally(() => {
      conversationLoading.value = false
    })
}

function loadConversationDetail(id) {
  if (!id) return Promise.resolve()
  return getConversation(id).then((response) => {
    conversationDetail.value = response.data || null
  })
}

function loadMessages(id) {
  if (!id) return Promise.resolve()
  return listMessages(id).then((response) => {
    messages.value = response.data || []
    scrollToBottom()
  })
}

function selectConversation(id) {
  currentConversationId.value = id
  mobileView.value = 'detail'
  actionPanelOpen.value = false
  lastSummaryTriggered.value = false
  return Promise.all([loadConversationDetail(id), loadMessages(id)])
}

function backToList() {
  mobileView.value = 'list'
  actionPanelOpen.value = false
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
    return loadConversations().then(() => selectConversation(response.data.id))
  })
}

function send() {
  const text = input.value.trim()
  if (!text || !currentConversationId.value) return
  const localMessage = { role: 'user', content: text, localId: Date.now() }
  messages.value.push(localMessage)
  input.value = ''
  sending.value = true
  actionPanelOpen.value = false
  lastSummaryTriggered.value = false
  scrollToBottom()
  sendChat({ conversationId: currentConversationId.value, content: text })
    .then((response) => {
      const data = response.data || {}
      if (data.userMessage?.id) {
        const index = messages.value.findIndex((item) => item.localId === localMessage.localId)
        if (index >= 0) messages.value[index] = data.userMessage
      }
      if (data.message) messages.value.push(data.message)
      lastSummaryTriggered.value = Boolean(data.summaryTriggered)
      loadConversations()
      loadConversationDetail(currentConversationId.value)
      scrollToBottom()
    })
    .finally(() => {
      sending.value = false
    })
}

function toggleActionPanel() {
  if (!currentConversationId.value) return
  actionPanelOpen.value = !actionPanelOpen.value
}

function runAction(key) {
  if (key !== 'edit-mode') actionPanelOpen.value = false
  const actionMap = {
    settings: () => openConversationSettings(currentConversationId.value),
    summary: openSummaryDialog,
    memory: openMemoryDialog,
    'edit-last': openEditLastAssistant,
    'edit-mode': toggleEditMode,
    'rebuild-summary': manualSummary,
    'new-chat': openConversationDialog,
    top: scrollToTop,
  }
  actionMap[key]?.()
}

function openConversationSettings(id) {
  const targetId = id || currentConversationId.value
  if (!targetId) return
  settingsTargetConversationId.value = targetId
  loadConversationDetail(targetId).then(() => {
    const detail = conversationDetail.value || {}
    conversationForm.title = detail.title || ''
    conversationForm.conversationPrompt = detail.conversationPrompt || ''
    settingsDialogOpen.value = true
  })
}

function saveConversationSettings() {
  const targetId = settingsTargetConversationId.value || currentConversationId.value
  updateConversation(targetId, {
    title: conversationForm.title,
    conversationPrompt: conversationForm.conversationPrompt,
  }).then(() => {
    proxy.$modal.msgSuccess('对话提示词已保存')
    settingsDialogOpen.value = false
    if (targetId === currentConversationId.value) {
      loadConversationDetail(currentConversationId.value)
    }
    loadConversations()
  })
}

function openSummaryDialog() {
  if (!currentConversationId.value) return
  loadConversationDetail(currentConversationId.value).then(() => {
    summaryForm.summary = conversationDetail.value?.summary || ''
    summaryDialogOpen.value = true
  })
}

function saveSummary() {
  updateConversation(currentConversationId.value, { summary: summaryForm.summary }).then(() => {
    proxy.$modal.msgSuccess('摘要已保存')
    summaryDialogOpen.value = false
    loadConversationDetail(currentConversationId.value)
    loadConversations()
  })
}

function manualSummary() {
  if (!currentConversationId.value) return
  summaryRebuilding.value = true
  rebuildSummary(currentConversationId.value)
    .then((response) => {
      const summary = response.data?.summary || ''
      summaryForm.summary = summary
      proxy.$modal.msgSuccess('摘要已更新')
      loadConversationDetail(currentConversationId.value)
      loadConversations()
      if (!summaryDialogOpen.value) {
        summaryDialogOpen.value = true
      }
    })
    .finally(() => {
      summaryRebuilding.value = false
    })
}

function openMemoryDialog() {
  if (!currentConversationId.value) return
  loadConversationDetail(currentConversationId.value).then(() => {
    memoryForm.forcedMemory = conversationDetail.value?.forcedMemory || ''
    memoryDialogOpen.value = true
  })
}

function saveMemory() {
  updateConversation(currentConversationId.value, { forcedMemory: memoryForm.forcedMemory }).then(() => {
    proxy.$modal.msgSuccess('强制记忆已保存')
    memoryDialogOpen.value = false
    loadConversationDetail(currentConversationId.value)
  })
}

function openEditLastAssistant() {
  const lastAssistant = [...messages.value].reverse().find((item) => item.role === 'assistant' && item.id)
  if (!lastAssistant) {
    proxy.$modal.msgWarning('还没有可编辑的 AI 回复')
    return
  }
  openEditMessage(lastAssistant)
}

function toggleEditMode() {
  editMode.value = !editMode.value
}

function openEditMessage(item) {
  if (!item?.id) return
  messageForm.id = item.id
  messageForm.content = item.content || ''
  messageDialogOpen.value = true
}

function saveMessage() {
  updateMessage(messageForm.id, { content: messageForm.content }).then((response) => {
    const updated = response.data || {}
    const index = messages.value.findIndex((item) => item.id === updated.id)
    if (index >= 0) messages.value[index] = { ...messages.value[index], ...updated }
    proxy.$modal.msgSuccess('消息已保存')
    messageDialogOpen.value = false
    loadConversationDetail(currentConversationId.value)
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
  })
}

watch(
  () => mobileView.value === 'detail' && Boolean(currentConversationId.value),
  (enabled) => {
    document.body.classList.toggle(immersiveBodyClass, enabled)
  },
  { immediate: true }
)

onMounted(async () => {
  await Promise.all([loadCharacters(), loadConversations()])
  const id = Number(route.query.conversationId)
  if (id) {
    selectConversation(id)
  } else if (conversations.value.length) {
    selectConversation(conversations.value[0].id)
    mobileView.value = 'list'
  }
})

onUnmounted(() => {
  document.body.classList.remove(immersiveBodyClass)
})
</script>

<style scoped>
.tavern-chat {
  height: calc(100vh - 84px);
  padding: 0;
  display: flex;
  background: #ededed;
  overflow: hidden;
}

.side {
  width: clamp(260px, 24vw, 340px);
  flex: 0 0 clamp(260px, 24vw, 340px);
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  overflow: hidden;
}

.mobile-list-title {
  display: none;
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
  padding: 13px 12px;
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

.side-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-title {
  min-width: 0;
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.side-edit {
  opacity: 0.6;
}

.side-desc,
.side-prompt {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.side-prompt {
  color: var(--el-color-primary);
}

.main {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0;
  min-width: 0;
  background: #ededed;
}

.chat-header {
  height: 64px;
  padding: 0 18px;
  background: #f7f7f7;
  border-bottom: 1px solid #ddd;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mobile-back {
  display: none;
}

.chat-heading {
  min-width: 0;
  flex: 1;
  text-align: center;
}

.chat-title {
  font-size: 18px;
  font-weight: 700;
  color: #111;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.chat-subtitle {
  margin-top: 4px;
  color: #888;
  font-size: 12px;
}

.header-more {
  width: 36px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 22px 20px 18px;
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
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

.message.user {
  justify-content: flex-end;
}

.avatar {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  user-select: none;
}

.assistant-avatar {
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
}

.user-avatar {
  background: #9eea6a;
  color: #1f2b16;
}

.bubble-wrap {
  max-width: min(760px, 72%);
}

.message.user .bubble-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.bubble {
  position: relative;
  padding: 11px 14px;
  border-radius: 6px;
  background: #fff;
  color: #222;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.04);
}

.assistant .bubble::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 13px;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid #fff;
}

.message.user .bubble {
  background: #9eea6a;
}

.message.user .bubble::after {
  content: "";
  position: absolute;
  right: -6px;
  top: 13px;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-left: 6px solid #9eea6a;
}

.message-meta {
  font-size: 12px;
  color: #888;
  margin-bottom: 5px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.latency,
.edited {
  color: #888;
}

.inline-edit {
  padding: 0;
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  font-size: 15px;
}

.composer {
  padding: 10px 20px 12px;
  background: #f7f7f7;
  border-top: 1px solid #ddd;
}

.composer-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.composer-row :deep(.el-textarea__inner) {
  min-height: 42px !important;
  border-radius: 6px;
  background: #fff;
}

.plus-button {
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  font-size: 20px;
}

.composer-actions {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: var(--el-color-success);
  font-size: 13px;
}

.edit-hint {
  color: var(--el-color-warning);
}

.action-panel {
  padding: 18px 24px 22px;
  background: #f6f6f6;
  border-top: 1px solid #ddd;
  display: grid;
  grid-template-columns: repeat(4, minmax(70px, 1fr));
  gap: 20px 18px;
}

.action-item {
  border: 0;
  background: transparent;
  color: #555;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.action-icon {
  width: 58px;
  height: 58px;
  border-radius: 12px;
  background: #fff;
  color: #222;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}

.dialog-textarea {
  margin-top: 14px;
}

@media (max-width: 768px) {
  .tavern-chat {
    height: calc(100vh - 84px);
    min-height: 600px;
    display: block;
  }

  :global(body.ai-tavern-mobile-chat-immersive) {
    overflow: hidden;
  }

  :global(body.ai-tavern-mobile-chat-immersive .fixed-header),
  :global(body.ai-tavern-mobile-chat-immersive #tags-view-container) {
    display: none !important;
  }

  :global(body.ai-tavern-mobile-chat-immersive .main-container.hasTagsView) {
    padding-top: 0 !important;
  }

  :global(body.ai-tavern-mobile-chat-immersive .app-main) {
    min-height: 100vh !important;
    height: 100vh !important;
    overflow: hidden !important;
  }

  :global(body.ai-tavern-mobile-chat-immersive .app-main > .tavern-chat.mobile-detail) {
    height: 100vh;
    min-height: 100vh;
  }

  .mobile-list .main {
    display: none;
  }

  .mobile-detail .side {
    display: none;
  }

  .side {
    width: 100%;
    height: 100%;
    border-right: 0;
  }

  .mobile-list-title {
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    background: #f7f7f7;
    border-bottom: 1px solid #ddd;
  }

  .side-list {
    height: calc(100vh - 252px);
    padding: 10px;
  }

  .side-item {
    padding: 14px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    border-radius: 0;
  }

  .main {
    height: 100%;
  }

  .chat-header {
    height: 56px;
    padding: 0 10px;
    position: sticky;
    top: 0;
    z-index: 12;
  }

  .mobile-back {
    display: inline-flex;
    width: 38px;
    font-size: 22px;
  }

  .chat-title {
    font-size: 17px;
  }

  .chat-subtitle {
    display: none;
  }

  .messages {
    padding: 16px 12px;
  }

  .avatar {
    width: 34px;
    height: 34px;
    flex-basis: 34px;
  }

  .bubble-wrap {
    max-width: 74%;
  }

  .message-content {
    font-size: 16px;
  }

  .composer {
    padding: 8px 10px 10px;
  }

  .composer-actions {
    margin-top: 6px;
  }

  .action-panel {
    grid-template-columns: repeat(4, 1fr);
    gap: 18px 10px;
    padding: 18px 12px 24px;
  }

  .action-icon {
    width: 54px;
    height: 54px;
  }
}

@media (max-width: 420px) {
  .bubble-wrap {
    max-width: 78%;
  }

  .action-panel {
    grid-template-columns: repeat(4, 1fr);
  }

  .action-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
}
</style>

<style>
@media (max-width: 768px) {
  body.ai-tavern-mobile-chat-immersive {
    overflow: hidden;
  }

  body.ai-tavern-mobile-chat-immersive .fixed-header,
  body.ai-tavern-mobile-chat-immersive #tags-view-container {
    display: none !important;
  }

  body.ai-tavern-mobile-chat-immersive .main-container.hasTagsView .app-main {
    margin-top: 0 !important;
    min-height: 100vh !important;
    height: 100vh !important;
    overflow: hidden !important;
  }

  body.ai-tavern-mobile-chat-immersive .app-main > .tavern-chat.mobile-detail {
    height: 100vh !important;
    min-height: 100vh !important;
  }
}
</style>
