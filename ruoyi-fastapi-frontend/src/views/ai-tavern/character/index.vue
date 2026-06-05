<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="72px">
      <el-form-item label="角色名" prop="name">
        <el-input v-model="queryParams.name" placeholder="请输入角色名" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 160px">
          <el-option label="正常" value="0" />
          <el-option label="禁用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd">新增</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="characterList">
      <el-table-column label="ID" prop="id" width="90" align="center" />
      <el-table-column label="角色" min-width="160">
        <template #default="scope">
          <div class="role-cell">
            <el-avatar :size="32" :src="scope.row.avatarUrl">{{ firstChar(scope.row.name) }}</el-avatar>
            <span>{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="设定" prop="description" min-width="260" show-overflow-tooltip />
      <el-table-column label="性格" prop="personality" min-width="180" show-overflow-tooltip />
      <el-table-column label="状态" prop="status" width="90" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'info'">
            {{ scope.row.status === "0" ? "正常" : "禁用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" prop="updateTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.updateTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="210" align="center" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="ChatDotRound" @click="startChat(scope.row)">聊天</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)">修改</el-button>
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

    <el-dialog :title="title" v-model="open" width="760px" append-to-body>
      <el-form ref="characterRef" :model="form" :rules="rules" label-width="96px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="form.name" placeholder="例如：扶摇" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="头像地址" prop="avatarUrl">
              <el-input v-model="form.avatarUrl" placeholder="可选 URL" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="角色设定" prop="description">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="角色背景、身份、关系等" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性格" prop="personality">
              <el-input v-model="form.personality" type="textarea" :rows="3" placeholder="说话风格、情绪倾向" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前场景" prop="scenario">
              <el-input v-model="form.scenario" type="textarea" :rows="3" placeholder="故事发生的地点和状态" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="开场白" prop="firstMessage">
              <el-input v-model="form.firstMessage" type="textarea" :rows="2" placeholder="新建会话时角色说的第一句话" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="补充提示词" prop="systemPrompt">
              <el-input v-model="form.systemPrompt" type="textarea" :rows="3" placeholder="额外规则，可为空" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确定</el-button>
          <el-button @click="cancel">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AiTavernCharacter">
import {
  addCharacter,
  createConversation,
  delCharacter,
  getCharacter,
  listCharacters,
  updateCharacter,
} from "@/api/ai-tavern/tavern";

const { proxy } = getCurrentInstance();
const router = useRouter();

const characterList = ref([]);
const loading = ref(false);
const showSearch = ref(true);
const total = ref(0);
const open = ref(false);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    name: undefined,
    status: "0",
  },
  rules: {
    name: [{ required: true, message: "角色名称不能为空", trigger: "blur" }],
  },
});

const { queryParams, form, rules } = toRefs(data);

function firstChar(name) {
  return (name || "?").slice(0, 1);
}

function getList() {
  loading.value = true;
  listCharacters(queryParams.value).then((response) => {
    characterList.value = response.rows || [];
    total.value = response.total || 0;
    loading.value = false;
  });
}

function reset() {
  form.value = {
    id: undefined,
    name: "",
    avatarUrl: "",
    description: "",
    personality: "",
    scenario: "",
    firstMessage: "",
    systemPrompt: "",
    exampleDialogues: "",
    status: "0",
  };
  proxy.resetForm("characterRef");
}

function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增角色";
}

function handleUpdate(row) {
  reset();
  getCharacter(row.id).then((response) => {
    form.value = response.data || {};
    open.value = true;
    title.value = "修改角色";
  });
}

function submitForm() {
  proxy.$refs.characterRef.validate((valid) => {
    if (!valid) return;
    const request = form.value.id ? updateCharacter(form.value.id, form.value) : addCharacter(form.value);
    request.then(() => {
      proxy.$modal.msgSuccess("保存成功");
      open.value = false;
      getList();
    });
  });
}

function handleDelete(row) {
  proxy.$modal
    .confirm(`确认删除角色「${row.name}」吗？`)
    .then(() => delCharacter(row.id))
    .then(() => {
      proxy.$modal.msgSuccess("删除成功");
      getList();
    })
    .catch(() => {});
}

function startChat(row) {
  createConversation({ characterId: row.id }).then((response) => {
    router.push({ path: "/ai-tavern/chat", query: { conversationId: response.data.id } });
  });
}

function cancel() {
  open.value = false;
  reset();
}

getList();
</script>

<style scoped>
.role-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
