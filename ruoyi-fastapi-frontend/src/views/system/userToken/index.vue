<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="82px">
      <el-form-item label="用户ID" prop="userId">
        <el-input-number v-model="queryParams.userId" :min="1" controls-position="right" clearable />
      </el-form-item>
      <el-form-item label="用户账号" prop="userName">
        <el-input v-model="queryParams.userName" placeholder="请输入用户账号" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="用户昵称" prop="nickName">
        <el-input v-model="queryParams.nickName" placeholder="请输入用户昵称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="启用状态" prop="enabled">
        <el-select v-model="queryParams.enabled" placeholder="全部" clearable style="width: 140px">
          <el-option label="启用" :value="true" />
          <el-option label="停用" :value="false" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery" v-hasPermi="['system:userToken:list']">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="rows">
      <el-table-column label="用户ID" prop="userId" width="90" />
      <el-table-column label="用户账号" prop="userName" min-width="120" />
      <el-table-column label="用户昵称" prop="nickName" min-width="120" />
      <el-table-column label="今日已用" width="120" align="right">
        <template #default="scope">￥{{ formatMoney(scope.row.usedTodayCostYuan) }}</template>
      </el-table-column>
      <el-table-column label="本月已用" width="120" align="right">
        <template #default="scope">￥{{ formatMoney(scope.row.usedMonthCostYuan) }}</template>
      </el-table-column>
      <el-table-column label="累计已用" width="120" align="right">
        <template #default="scope">￥{{ formatMoney(scope.row.usedTotalCostYuan) }}</template>
      </el-table-column>
      <el-table-column label="每日额度" width="120" align="right">
        <template #default="scope">{{ formatLimit(scope.row.dailyCostLimitYuan) }}</template>
      </el-table-column>
      <el-table-column label="每月额度" width="120" align="right">
        <template #default="scope">{{ formatLimit(scope.row.monthlyCostLimitYuan) }}</template>
      </el-table-column>
      <el-table-column label="总额度" width="120" align="right">
        <template #default="scope">{{ formatLimit(scope.row.totalCostLimitYuan) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="scope">
          <el-tag :type="scope.row.enabled === false ? 'danger' : 'success'">
            {{ scope.row.enabled === false ? '停用' : '启用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" prop="updateTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.updateTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="110" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleEdit(scope.row)" v-hasPermi="['system:userToken:edit']">修改</el-button>
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

    <el-dialog v-model="open" title="用户人民币额度设置" width="540px" append-to-body>
      <el-form ref="formRef" :model="form" label-width="120px">
        <el-form-item label="用户">
          <el-input :model-value="`${form.nickName || ''}（${form.userName || form.userId}）`" disabled />
        </el-form-item>
        <el-form-item label="启用额度限制">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="每日额度">
          <el-input-number v-model="form.dailyCostLimitYuan" :min="0" :precision="2" :step="1" controls-position="right" />
          <span class="form-tip">元，0 表示不限制</span>
        </el-form-item>
        <el-form-item label="每月额度">
          <el-input-number v-model="form.monthlyCostLimitYuan" :min="0" :precision="2" :step="10" controls-position="right" />
          <span class="form-tip">元，0 表示不限制</span>
        </el-form-item>
        <el-form-item label="总额度">
          <el-input-number v-model="form.totalCostLimitYuan" :min="0" :precision="2" :step="10" controls-position="right" />
          <span class="form-tip">元，0 表示不限制</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确定</el-button>
          <el-button @click="open = false">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="UserTokenSetting">
import { listUserTokenSetting, updateUserTokenSetting } from '@/api/system/userToken'

const { proxy } = getCurrentInstance()

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const showSearch = ref(true)
const open = ref(false)
const form = ref({})

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  userId: undefined,
  userName: undefined,
  nickName: undefined,
  enabled: undefined
})

function getList() {
  loading.value = true
  listUserTokenSetting(queryParams).then((response) => {
    rows.value = response.rows || []
    total.value = response.total || 0
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryRef')
  queryParams.userId = undefined
  queryParams.enabled = undefined
  handleQuery()
}

function handleEdit(row) {
  form.value = {
    userId: row.userId,
    userName: row.userName,
    nickName: row.nickName,
    dailyCostLimitYuan: Number(row.dailyCostLimitYuan || 0),
    monthlyCostLimitYuan: Number(row.monthlyCostLimitYuan || 0),
    totalCostLimitYuan: Number(row.totalCostLimitYuan || 0),
    enabled: row.enabled !== false,
    remark: row.remark
  }
  open.value = true
}

function submitForm() {
  updateUserTokenSetting(form.value).then(() => {
    proxy.$modal.msgSuccess('保存成功')
    open.value = false
    getList()
  })
}

function formatMoney(value) {
  return Number(value || 0).toFixed(4)
}

function formatLimit(value) {
  const amount = Number(value || 0)
  return amount > 0 ? `￥${amount.toFixed(2)}` : '不限'
}

getList()
</script>

<style scoped>
.form-tip {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
