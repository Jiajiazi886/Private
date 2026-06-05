<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="queryParams.title" placeholder="请输入会话标题" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="conversationList">
      <el-table-column label="ID" prop="id" width="90" align="center" />
      <el-table-column label="标题" prop="title" min-width="180" show-overflow-tooltip />
      <el-table-column label="角色" prop="characterName" width="140" />
      <el-table-column label="消息数" prop="totalMessageCount" width="100" align="right" />
      <el-table-column label="总轮数" prop="totalTurnCount" width="100" align="right" />
      <el-table-column label="摘要版本" prop="summaryVersion" width="100" align="right" />
      <el-table-column label="摘要状态" prop="summaryStatus" width="110" align="center" />
      <el-table-column label="更新时间" prop="updateTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.updateTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="ChatDotRound" @click="goChat(scope.row)">聊天</el-button>
          <el-button link type="primary" icon="View" @click="viewMessages(scope.row)">消息</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <el-dialog v-model="messageOpen" title="会话消息" width="860px" append-to-body>
      <div class="message-list" v-loading="messageLoading">
        <div v-for="item in messages" :key="item.id" :class="['message-row', item.role]">
          <div class="message-meta">
            <span>{{ item.role === "user" ? "用户" : "角色" }}</span>
            <span>{{ parseTime(item.createTime) }}</span>
          </div>
          <div class="message-content">{{ item.content }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="AiTavernConversation">
import { delConversation, listConversations, listMessages } from "@/api/ai-tavern/tavern";

const { proxy } = getCurrentInstance();
const router = useRouter();

const conversationList = ref([]);
const loading = ref(false);
const showSearch = ref(true);
const total = ref(0);
const messageOpen = ref(false);
const messageLoading = ref(false);
const messages = ref([]);

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  title: undefined,
  status: "0",
});

function getList() {
  loading.value = true;
  listConversations(queryParams).then((response) => {
    conversationList.value = response.rows || [];
    total.value = response.total || 0;
    loading.value = false;
  });
}

function handleQuery() {
  queryParams.pageNum = 1;
  getList();
}

function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

function goChat(row) {
  router.push({ path: "/ai-tavern/chat", query: { conversationId: row.id } });
}

function viewMessages(row) {
  messageOpen.value = true;
  messageLoading.value = true;
  listMessages(row.id).then((response) => {
    messages.value = response.data || [];
    messageLoading.value = false;
  });
}

function handleDelete(row) {
  proxy.$modal
    .confirm(`确认删除会话「${row.title || row.id}」吗？`)
    .then(() => delConversation(row.id))
    .then(() => {
      proxy.$modal.msgSuccess("删除成功");
      getList();
    })
    .catch(() => {});
}

getList();
</script>

<style scoped>
.message-list {
  max-height: 560px;
  overflow-y: auto;
}

.message-row {
  margin-bottom: 14px;
}

.message-meta {
  display: flex;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.message-content {
  white-space: pre-wrap;
  line-height: 1.6;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.message-row.user .message-content {
  background: var(--el-color-primary-light-9);
}
</style>
