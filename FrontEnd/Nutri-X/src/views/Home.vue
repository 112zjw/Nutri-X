<template>
  <div class="home-container">
    <!-- Top Section: Upload and Image Display -->
    <el-card class="upload-card animate__animated animate__fadeInDown">
      <template #header>
        <div class="card-header">
          <span>📸 上传食材图片</span>
          <el-button
            type="primary"
            @click="startIdentify"
            :loading="loading"
            :disabled="!file"
          >
            {{ loading ? "正在识别中..." : "开始识别" }}
          </el-button>
        </div>
      </template>

      <div class="upload-area" v-if="!imageUrl">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="false"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
        </el-upload>
      </div>

      <div v-else class="image-display-container">
        <div class="image-wrapper" ref="imageWrapper">
          <img :src="imageUrl" alt="Uploaded Image" class="target-image" />
        </div>

        <div class="re-upload-btn">
          <el-button link type="info" @click="clearImage">重新上传</el-button>
        </div>
      </div>

      <!-- Non-food Warning -->
      <el-alert
        v-if="hasNonFoodItems"
        title="注意：检测到非食材物体，已自动过滤。"
        type="warning"
        show-icon
        style="margin-top: 10px"
      />
    </el-card>

    <!-- Bottom Section: Results Table -->
    <el-card
      class="result-card animate__animated animate__fadeInUp"
      v-if="store.ingredients.length > 0"
      style="margin-top: 20px"
    >
      <template #header>
        <div class="card-header">
          <span>🥦 识别结果与营养分析</span>
          <el-button type="success" link @click="$router.push('/recipes')"
            >去生成菜谱 <el-icon><ArrowRight /></el-icon
          ></el-button>
        </div>
      </template>

      <el-table :data="store.nutritionData" style="width: 100%" stripe>
        <el-table-column prop="name" label="食材" width="150" />
        <el-table-column prop="calories" label="卡路里 (kcal)" />
        <el-table-column prop="protein" label="蛋白质 (g)" />
        <el-table-column prop="fat" label="脂肪 (g)" />
        <el-table-column prop="carbs" label="碳水 (g)" />
        <el-table-column
          prop="benefit"
          label="主要益处"
          show-overflow-tooltip
        />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { UploadFilled, ArrowRight } from "@element-plus/icons-vue";
import { identifyIngredients } from "../api";
import { store } from "../store";
import { ElMessage } from "element-plus";

const file = ref(null);
const imageUrl = ref("");
const loading = ref(false);

const hasNonFoodItems = computed(() => {
  return store.itemsWithLoc.some((item) => !item.is_food);
});

const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw;
  imageUrl.value = URL.createObjectURL(uploadFile.raw);
  // Reset results on new file
  store.setIngredients([]);
  store.setNutritionData([]);
  store.setItemsWithLoc([]);
};

const clearImage = () => {
  file.value = null;
  imageUrl.value = "";
  store.setIngredients([]);
  store.setNutritionData([]);
  store.setItemsWithLoc([]);
};

const startIdentify = async () => {
  if (!file.value) return;

  loading.value = true;
  const formData = new FormData();
  formData.append("file", file.value);

  try {
    const res = await identifyIngredients(formData);
    if (res.data.status === "success") {
      store.setIngredients(res.data.ingredients);
      store.setNutritionData(res.data.nutrition);
      // Assuming backend returns items_with_loc
      if (res.data.items_with_loc) {
        store.setItemsWithLoc(res.data.items_with_loc);
      }

      ElMessage.success(`成功识别出 ${res.data.ingredients.length} 种食材！`);
    } else {
      ElMessage.error("识别失败: " + res.data.message);
    }
  } catch (error) {
    ElMessage.error("请求出错: " + error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.image-display-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.target-image {
  display: block;
  max-width: 100%;
  max-height: 600px;
  border-radius: 8px;
}

.re-upload-btn {
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
