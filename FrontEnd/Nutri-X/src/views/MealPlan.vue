<template>
  <div class="plan-container">
    <div class="content-wrapper">
      <!-- Top Section: Meal Plan -->
      <el-card class="plan-card animate__animated animate__fadeInDown">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="title">📅 今日三餐规划</span>
              <span class="subtitle" v-if="!isEmptyPlan">
                合理搭配，营养均衡
              </span>
            </div>
            <el-button
              type="primary"
              @click="evaluate"
              :loading="loading"
              :disabled="isEmptyPlan"
              size="large"
              round
            >
              📊 生成膳食评估报告
            </el-button>
          </div>
        </template>

        <div class="meals-grid">
          <div
            class="meal-column"
            v-for="(items, meal) in store.mealPlan"
            :key="meal"
          >
            <el-card shadow="hover" class="meal-inner-card">
              <template #header>
                <div class="meal-title">
                  <el-tag
                    :type="getMealTagType(meal)"
                    effect="dark"
                    size="large"
                    round
                  >
                    {{ meal }}
                  </el-tag>
                </div>
              </template>
              <div class="meal-items">
                <transition-group name="list">
                  <el-tag
                    v-for="item in items"
                    :key="item"
                    closable
                    class="meal-item"
                    size="default"
                    @close="store.removeFromMealPlan(meal, item)"
                  >
                    {{ item }}
                  </el-tag>
                </transition-group>
                <div v-if="items.length === 0" class="empty-text">暂无安排</div>
              </div>
            </el-card>
          </div>
        </div>
      </el-card>

      <!-- Bottom Section: Assessment Report -->
      <div
        v-if="report"
        class="report-section animate__animated animate__fadeInUp"
      >
        <el-divider content-position="center">
          <span class="report-divider-title">📋 营养评估报告</span>
        </el-divider>

        <el-card class="report-card" shadow="never">
          <div class="markdown-body" v-html="renderedReport"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { store } from "../store";
import { evaluateMealPlan } from "../api";
import { ElMessage } from "element-plus";
import { marked } from "marked";

const loading = ref(false);
const report = ref("");

const isEmptyPlan = computed(() => {
  return Object.values(store.mealPlan).every((items) => items.length === 0);
});

const renderedReport = computed(() => {
  return marked(report.value);
});

const getMealTagType = (meal) => {
  const map = {
    早餐: "warning",
    午餐: "danger",
    晚餐: "success",
  };
  return map[meal] || "info";
};

const evaluate = async () => {
  loading.value = true;
  try {
    const res = await evaluateMealPlan(store.mealPlan);
    if (res.data.status === "success") {
      report.value = res.data.report;
      ElMessage.success("评估完成");
      // Scroll to report
      setTimeout(() => {
        const reportEl = document.querySelector(".report-section");
        if (reportEl) {
          reportEl.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    } else {
      ElMessage.error("评估失败: " + res.data.message);
    }
  } catch (error) {
    ElMessage.error("请求出错: " + error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.plan-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.title {
  font-size: 1.2rem;
  font-weight: bold;
}

.subtitle {
  font-size: 0.9rem;
  color: #909399;
}

/* Meals Grid Layout */
.meals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 10px 0;
}

.meal-inner-card {
  height: 100%;
  border: 1px solid #ebeef5;
  transition: transform 0.3s;
}

.meal-inner-card:hover {
  transform: translateY(-5px);
}

.meal-title {
  text-align: center;
}

.meal-items {
  min-height: 100px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-content: flex-start;
}

.meal-item {
  margin: 0;
}

.empty-text {
  width: 100%;
  text-align: center;
  color: #c0c4cc;
  font-size: 0.9rem;
  margin-top: 20px;
}

/* Report Section */
.report-section {
  margin-top: 10px;
}

.report-divider-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #409eff;
}

.report-card {
  background-color: #fcfcfc;
  border-radius: 8px;
}

.markdown-body {
  line-height: 1.8;
  color: #2c3e50;
  padding: 10px;
}

/* Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
