<template>
  <view class="page">
    <scroll-view class="messages" scroll-y :scroll-top="scrollTop">
      <view v-for="item in messages" :key="item.id || item.seqNo" :class="['msg', item.role === 'user' ? 'user' : 'assistant']">
        <view class="bubble">{{ item.content }}</view>
      </view>
      <view v-if="loading" class="msg assistant"><view class="bubble">正在回复...</view></view>
    </scroll-view>
    <view class="composer">
      <textarea v-model="content" class="input" auto-height placeholder="输入消息" />
      <button class="send" :disabled="loading || !content.trim()" @click="submit">发送</button>
    </view>
  </view>
</template>

<script setup>
import { listMessages, sendChat } from "@/api/ai-tavern";

const conversationId = ref(null);
const messages = ref([]);
const content = ref("");
const loading = ref(false);
const scrollTop = ref(0);

onLoad((options) => {
  conversationId.value = Number(options.conversationId);
  loadMessages();
});

function loadMessages() {
  listMessages(conversationId.value).then((res) => {
    messages.value = res.data || [];
    scrollToBottom();
  });
}

function scrollToBottom() {
  nextTick(() => {
    scrollTop.value = messages.value.length * 1000;
  });
}

function submit() {
  const text = content.value.trim();
  if (!text) return;
  messages.value.push({ role: "user", content: text, seqNo: Date.now() });
  content.value = "";
  loading.value = true;
  scrollToBottom();
  sendChat({ conversationId: conversationId.value, content: text })
    .then((res) => {
      if (res.data?.message) {
        messages.value.push(res.data.message);
      }
      scrollToBottom();
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: #f6f7f9; }
.messages { flex: 1; padding: 24rpx; box-sizing: border-box; }
.msg { display: flex; margin-bottom: 18rpx; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 74%; padding: 20rpx 24rpx; border-radius: 8rpx; background: #fff; color: #222; white-space: pre-wrap; word-break: break-word; }
.user .bubble { background: #1677ff; color: #fff; }
.composer { display: flex; gap: 16rpx; padding: 18rpx; background: #fff; border-top: 1px solid #eee; }
.input { flex: 1; min-height: 72rpx; max-height: 180rpx; padding: 18rpx; border-radius: 8rpx; background: #f3f4f6; font-size: 28rpx; box-sizing: border-box; }
.send { width: 140rpx; height: 72rpx; line-height: 72rpx; background: #1677ff; color: #fff; border-radius: 8rpx; font-size: 28rpx; }
</style>
