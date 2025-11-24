<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">
          <el-icon :size="30" color="#67C23A"><Food /></el-icon>
          <span class="title">Nutri-X 智能膳食助手</span>
        </div>
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          router
          class="nav-menu"
        >
          <el-menu-item index="/">食材识别</el-menu-item>
          <el-menu-item index="/recipes">菜谱推荐</el-menu-item>
          <el-menu-item index="/meal-plan">三餐规划</el-menu-item>
        </el-menu>
        <div class="settings">
          <el-button type="primary" link @click="showSettings = true">
            <el-icon><Setting /></el-icon> 设置 API Key
          </el-button>
        </div>
      </el-header>

      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <el-dialog v-model="showSettings" title="设置 API Key" width="400px">
        <el-form>
          <el-form-item label="DashScope API Key">
            <el-input
              v-model="apiKeyInput"
              placeholder="sk-..."
              type="password"
              show-password
            />
          </el-form-item>
          <p class="hint">
            请输入阿里云 DashScope API Key，将用于所有 AI 功能调用。
          </p>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showSettings = false">取消</el-button>
            <el-button type="primary" @click="saveApiKey">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Setting, Food } from "@element-plus/icons-vue";
import { store } from "./store";
import { ElMessage } from "element-plus";

const route = useRoute();
const activeIndex = ref("/");
const showSettings = ref(false);
const apiKeyInput = ref("");

onMounted(() => {
  apiKeyInput.value = store.apiKey;
  if (!store.apiKey) {
    showSettings.value = true; // 如果没有 key，自动弹出
  }
});

const saveApiKey = () => {
  if (!apiKeyInput.value) {
    ElMessage.warning("请输入 API Key");
    return;
  }
  store.setApiKey(apiKeyInput.value);
  showSettings.value = false;
  ElMessage.success("API Key 已保存");
};

watch(route, (newPath) => {
  activeIndex.value = newPath.path;
});
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #303133;
}

.nav-menu {
  border-bottom: none;
  flex-grow: 1;
  justify-content: flex-end;
  margin-right: 20px;
}

.settings {
  display: flex;
  align-items: center;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: -10px;
}

.el-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
