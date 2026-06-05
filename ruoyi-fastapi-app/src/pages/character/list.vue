<template>
  <view class="page">
    <view class="toolbar">
      <button class="primary" @click="goEdit">创建角色</button>
    </view>
    <view v-if="characters.length === 0" class="empty">暂无角色</view>
    <view v-for="item in characters" :key="item.id" class="row" @click="startConversation(item)">
      <view class="avatar">{{ (item.name || "?").slice(0, 1) }}</view>
      <view class="main">
        <view class="title">{{ item.name }}</view>
        <view class="desc">{{ item.description || "还没有角色描述" }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { listCharacters, createConversation } from "@/api/ai-tavern";

const characters = ref([]);

function loadList() {
  listCharacters({ pageNum: 1, pageSize: 100, status: "0" }).then((res) => {
    characters.value = res.rows || [];
  });
}

function goEdit() {
  uni.navigateTo({ url: "/pages/character/edit" });
}

function startConversation(character) {
  createConversation({ characterId: character.id }).then((res) => {
    uni.navigateTo({ url: `/pages/chat/index?conversationId=${res.data.id}` });
  });
}

onShow(loadList);
</script>

<style scoped>
.page { min-height: 100vh; padding: 24rpx; background: #f6f7f9; }
.toolbar { margin-bottom: 20rpx; }
.primary { background: #1677ff; color: #fff; border-radius: 8rpx; }
.empty { margin-top: 120rpx; text-align: center; color: #999; }
.row { display: flex; gap: 20rpx; padding: 24rpx; margin-bottom: 16rpx; background: #fff; border-radius: 8rpx; }
.avatar { width: 72rpx; height: 72rpx; line-height: 72rpx; text-align: center; border-radius: 50%; background: #e8f1ff; color: #1677ff; font-weight: 600; }
.main { flex: 1; min-width: 0; }
.title { font-size: 32rpx; font-weight: 600; color: #222; }
.desc { margin-top: 8rpx; color: #777; font-size: 26rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
