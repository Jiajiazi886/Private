<template>
  <view class="page">
    <button class="primary" @click="goCharacters">选择角色开始聊天</button>
    <view v-if="conversations.length === 0" class="empty">暂无会话</view>
    <view v-for="item in conversations" :key="item.id" class="row" @click="goChat(item.id)">
      <view class="title">{{ item.title || "未命名会话" }}</view>
      <view class="desc">{{ item.characterName || "角色" }} · {{ item.totalMessageCount || 0 }} 条消息</view>
    </view>
  </view>
</template>

<script setup>
import { listConversations } from "@/api/ai-tavern";

const conversations = ref([]);

function loadList() {
  listConversations({ pageNum: 1, pageSize: 100, status: "0" }).then((res) => {
    conversations.value = res.rows || [];
  });
}

function goCharacters() {
  uni.navigateTo({ url: "/pages/character/list" });
}

function goChat(id) {
  uni.navigateTo({ url: `/pages/chat/index?conversationId=${id}` });
}

onShow(loadList);
</script>

<style scoped>
.page { min-height: 100vh; padding: 24rpx; background: #f6f7f9; }
.primary { margin-bottom: 20rpx; background: #1677ff; color: #fff; border-radius: 8rpx; }
.empty { margin-top: 120rpx; text-align: center; color: #999; }
.row { padding: 24rpx; margin-bottom: 16rpx; background: #fff; border-radius: 8rpx; }
.title { font-size: 31rpx; font-weight: 600; color: #222; }
.desc { margin-top: 8rpx; color: #777; font-size: 25rpx; }
</style>
