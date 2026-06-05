<template>
  <div class="app-container">
    <el-row :gutter="12" class="mb8">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never">
          <div class="metric-label">总 Token</div>
          <div class="metric-value">{{ dashboard.totalTokens || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never">
          <div class="metric-label">今日 Token</div>
          <div class="metric-value">{{ dashboard.todayTokens || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never">
          <div class="metric-label">估算费用</div>
          <div class="metric-value">¥{{ dashboard.estimatedCostYuan || "0" }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never">
          <div class="metric-label">失败请求</div>
          <div class="metric-value">{{ dashboard.failedRequests || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="用户ID" prop="userId">
        <el-input v-model="queryParams.userId" placeholder="请输入用户ID" clearable style="width: 180px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="模型" prop="model">
        <el-input v-model="queryParams.model" placeholder="请输入模型" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="类型" prop="requestType">
        <el-select v-model="queryParams.requestType" placeholder="请求类型" clearable style="width: 160px">
          <el-option label="聊天" value="chat" />
          <el-option label="摘要" value="summary" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="success">
        <el-select v-model="queryParams.success" placeholder="成功状态" clearable style="width: 160px">
          <el-option label="成功" :value="true" />
          <el-option label="失败" :value="false" />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间" style="width: 320px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="usageList">
      <el-table-column label="ID" prop="id" width="80" align="center" />
      <el-table-column label="用户" min-width="150">
        <template #default="scope">
          <span>{{ scope.row.nickName || scope.row.userName || scope.row.userId }}</span>
        </template>
      </el-table-column>
      <el-table-column label="模型" prop="model" min-width="160" show-overflow-tooltip />
      <el-table-column label="类型" prop="requestType" width="100" align="center" />
      <el-table-column label="输入" prop="promptTokens" width="100" align="right" />
      <el-table-column label="缓存命中" prop="promptCacheHitTokens" width="110" align="right" />
      <el-table-column label="缓存未命中" prop="promptCacheMissTokens" width="120" align="right" />
      <el-table-column label="输出" prop="completionTokens" width="100" align="right" />
      <el-table-column label="总计" prop="totalTokens" width="100" align="right" />
      <el-table-column label="费用(元)" prop="estimatedCostYuan" width="110" align="right" />
      <el-table-column label="耗时(ms)" prop="latencyMs" width="110" align="right" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.success ? 'success' : 'danger'">
            {{ scope.row.success ? "成功" : "失败" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="错误信息" prop="errorMessage" min-width="180" show-overflow-tooltip />
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />
  </div>
</template>

<script setup name="AiTavernTokenUsage">
import { getTavernDashboard, listTokenUsage } from "@/api/ai-tavern/tokenUsage";

const { proxy } = getCurrentInstance();

const usageList = ref([]);
const loading = ref(false);
const showSearch = ref(true);
const total = ref(0);
const dateRange = ref([]);
const dashboard = reactive({});

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  userId: undefined,
  model: undefined,
  requestType: undefined,
  success: undefined,
});

function getDashboard() {
  getTavernDashboard().then((res) => {
    Object.assign(dashboard, res.data || {});
  });
}

function getList() {
  loading.value = true;
  listTokenUsage(proxy.addDateRange(queryParams, dateRange.value)).then((response) => {
    usageList.value = response.rows || [];
    total.value = response.total || 0;
    loading.value = false;
  });
}

function handleQuery() {
  queryParams.pageNum = 1;
  getList();
  getDashboard();
}

function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

onMounted(() => {
  getDashboard();
  getList();
});
</script>

<style scoped>
.metric-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.metric-value {
  color: var(--el-text-color-primary);
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}
</style>
