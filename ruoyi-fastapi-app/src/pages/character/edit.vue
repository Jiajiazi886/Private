<template>
  <view class="page">
    <view class="form">
      <input v-model="form.name" class="input" placeholder="角色名称" />
      <textarea v-model="form.description" class="textarea" placeholder="角色设定" />
      <textarea v-model="form.personality" class="textarea" placeholder="性格设定" />
      <textarea v-model="form.scenario" class="textarea" placeholder="当前场景" />
      <textarea v-model="form.firstMessage" class="textarea" placeholder="开场白" />
      <button class="primary" :disabled="saving" @click="submit">保存角色</button>
    </view>
  </view>
</template>

<script setup>
import { addCharacter } from "@/api/ai-tavern";

const saving = ref(false);
const form = reactive({
  name: "",
  description: "",
  personality: "",
  scenario: "",
  firstMessage: "",
});

function submit() {
  if (!form.name.trim()) {
    uni.showToast({ title: "请输入角色名称", icon: "none" });
    return;
  }
  saving.value = true;
  addCharacter(form)
    .then(() => {
      uni.showToast({ title: "保存成功" });
      setTimeout(() => uni.navigateBack(), 300);
    })
    .finally(() => {
      saving.value = false;
    });
}
</script>

<style scoped>
.page { min-height: 100vh; padding: 24rpx; background: #f6f7f9; }
.form { display: flex; flex-direction: column; gap: 20rpx; }
.input, .textarea { box-sizing: border-box; width: 100%; padding: 22rpx; background: #fff; border-radius: 8rpx; font-size: 28rpx; }
.textarea { min-height: 160rpx; }
.primary { margin-top: 12rpx; background: #1677ff; color: #fff; border-radius: 8rpx; }
</style>
