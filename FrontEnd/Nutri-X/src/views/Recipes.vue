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
import { ref } from "vue";
import { store } from "../store";
import { recommendRecipes } from "../api";
import { ElMessage, ElNotification } from "element-plus";
import { VideoPlay } from "@element-plus/icons-vue";

const selectedIngredients = ref([]);
const loading = ref(false);

const generateRecipes = async () => {
  if (selectedIngredients.value.length === 0) {
    ElMessage.warning("请至少选择一种食材");
    return;
  }

  loading.value = true;
  try {
    const res = await recommendRecipes(selectedIngredients.value);
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
