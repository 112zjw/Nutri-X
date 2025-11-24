<template>
  <div class="recipes-container">
    <el-card class="selection-card animate__animated animate__fadeInDown">
      <template #header>
        <div class="card-header">
          <span>🍳 选择食材生成菜谱</span>
        </div>
      </template>

      <div v-if="store.ingredients.length > 0">
        <p>请选择您想使用的食材：</p>
        <el-checkbox-group v-model="selectedIngredients" size="large">
          <el-checkbox-button
            v-for="ing in store.ingredients"
            :key="ing"
            :value="ing"
          >
            {{ ing }}
          </el-checkbox-button>
        </el-checkbox-group>

        <el-divider content-position="center">个性化设置 (可选)</el-divider>

        <el-form :inline="true" class="profile-form">
          <el-form-item label="身高 (cm)">
            <el-input-number v-model="height" :min="50" :max="250" />
          </el-form-item>
          <el-form-item label="体重 (kg)">
            <el-input-number v-model="weight" :min="20" :max="200" />
          </el-form-item>
          <el-form-item label="膳食目标">
            <el-select
              v-model="goal"
              placeholder="请选择目标"
              style="width: 150px"
            >
              <el-option label="均衡饮食" value="均衡饮食" />
              <el-option label="减脂" value="减脂" />
              <el-option label="增肌" value="增肌" />
              <el-option label="低碳水" value="低碳水" />
              <el-option label="高蛋白" value="高蛋白" />
            </el-select>
          </el-form-item>
        </el-form>

        <div v-if="bmi" class="bmi-display">
          您的 BMI: <strong>{{ bmi }}</strong> ({{ bmiStatus }})
        </div>

        <div class="actions">
          <el-button
            type="primary"
            @click="generateRecipes"
            :loading="loading"
            round
            size="large"
          >
            ✨ 生成推荐菜谱
          </el-button>
        </div>
      </div>
      <el-empty v-else description="请先在首页识别食材" />
    </el-card>

    <div class="recipes-list" v-if="store.recommendations.length > 0">
      <el-divider content-position="center">推荐结果</el-divider>

      <el-row :gutter="20">
        <el-col
          :span="8"
          v-for="(recipe, index) in store.recommendations"
          :key="index"
        >
          <el-card
            class="recipe-card animate__animated animate__fadeInUp"
            :style="{ animationDelay: `${index * 0.2}s` }"
          >
            <template #header>
              <div class="recipe-header">
                <h3>{{ recipe.name }}</h3>
                <el-tag type="warning" effect="dark">推荐</el-tag>
              </div>
            </template>

            <p class="description">{{ recipe.description }}</p>

            <el-alert
              v-if="recipe.recommendation_reason"
              :title="recipe.recommendation_reason"
              type="success"
              :closable="false"
              class="reason-alert"
            />

            <div class="tags">
              <el-tag
                v-for="ing in recipe.ingredients"
                :key="ing"
                size="small"
                class="ing-tag"
                >{{ ing }}</el-tag
              >
            </div>

            <el-collapse accordion>
              <el-collapse-item title="详细做法步骤">
                <el-steps direction="vertical" :active="recipe.steps.length">
                  <el-step
                    v-for="(step, idx) in recipe.steps"
                    :key="idx"
                    :title="`步骤 ${idx + 1}`"
                    :description="step"
                  />
                </el-steps>
              </el-collapse-item>
              <el-collapse-item title="营养与口感评价">
                <p><strong>营养:</strong> {{ recipe.nutrition_eval }}</p>
                <p><strong>口感:</strong> {{ recipe.taste_eval }}</p>
              </el-collapse-item>
            </el-collapse>

            <div class="footer-actions">
              <el-link
                :href="`https://search.bilibili.com/all?keyword=${
                  recipe.video_keyword || recipe.name
                }`"
                target="_blank"
                type="primary"
              >
                <el-icon><VideoPlay /></el-icon> 观看视频教程
              </el-link>

              <el-dropdown
                split-button
                type="success"
                @command="(cmd) => addToPlan(cmd, recipe.name)"
              >
                加入规划
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="早餐">早餐</el-dropdown-item>
                    <el-dropdown-item command="午餐">午餐</el-dropdown-item>
                    <el-dropdown-item command="晚餐">晚餐</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { store } from "../store";
import { recommendRecipes } from "../api";
import { ElMessage, ElNotification } from "element-plus";
import { VideoPlay } from "@element-plus/icons-vue";

const selectedIngredients = ref([]);
const loading = ref(false);
const height = ref(null);
const weight = ref(null);
const goal = ref("均衡饮食");

const bmi = computed(() => {
  if (height.value && weight.value) {
    const h = height.value / 100;
    return (weight.value / (h * h)).toFixed(1);
  }
  return null;
});

const bmiStatus = computed(() => {
  if (!bmi.value) return "";
  const val = parseFloat(bmi.value);
  if (val < 18.5) return "偏瘦";
  if (val < 24) return "正常";
  if (val < 28) return "超重";
  return "肥胖";
});

const generateRecipes = async () => {
  if (selectedIngredients.value.length === 0) {
    ElMessage.warning("请至少选择一种食材");
    return;
  }

  loading.value = true;
  try {
    const userProfile = {
      height: height.value,
      weight: weight.value,
      bmi: bmi.value,
      goal: goal.value,
    };
    const res = await recommendRecipes(selectedIngredients.value, userProfile);
    if (res.data.status === "success") {
      store.setRecommendations(res.data.data);
      ElMessage.success("菜谱生成成功！");
    } else {
      ElMessage.error("生成失败: " + res.data.message);
    }
  } catch (error) {
    ElMessage.error("请求出错: " + error.message);
  } finally {
    loading.value = false;
  }
};

const addToPlan = (meal, dishName) => {
  store.addToMealPlan(meal, dishName);
  ElNotification({
    title: "添加成功",
    message: `已将 ${dishName} 添加到 ${meal}`,
    type: "success",
  });
};
</script>

<style scoped>
.recipes-container {
  padding: 20px;
}
.selection-card {
  margin-bottom: 30px;
}
.profile-form {
  margin-top: 20px;
  text-align: center;
}
.bmi-display {
  text-align: center;
  margin-bottom: 10px;
  color: #666;
}
.reason-alert {
  margin-bottom: 15px;
}
.actions {
  margin-top: 20px;
  text-align: center;
}
.recipe-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}
.recipe-card:hover {
  transform: translateY(-5px);
}
.recipe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.recipe-header h3 {
  margin: 0;
  font-size: 1.1rem;
}
.description {
  color: #666;
  font-style: italic;
  margin-bottom: 15px;
}
.tags {
  margin-bottom: 15px;
}
.ing-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
.footer-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
  padding-top: 15px;
}
</style>
