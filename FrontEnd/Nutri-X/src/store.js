import { reactive } from "vue";

export const store = reactive({
  apiKey: localStorage.getItem("nutri_x_api_key") || "",
  ingredients: [],
  itemsWithLoc: [], // 新增：带位置信息的食材
  nutritionData: [],
  selectedIngredients: [],
  recommendations: [],
  mealPlan: {
    早餐: [],
    午餐: [],
    晚餐: [],
  },

  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem("nutri_x_api_key", key);
  },
  setIngredients(data) {
    this.ingredients = data;
  },
  setItemsWithLoc(data) {
    // 新增
    this.itemsWithLoc = data;
  },
  setNutritionData(data) {
    this.nutritionData = data;
  },
  setRecommendations(data) {
    this.recommendations = data;
  },
  addToMealPlan(meal, dish) {
    if (!this.mealPlan[meal].includes(dish)) {
      this.mealPlan[meal].push(dish);
    }
  },
  removeFromMealPlan(meal, dish) {
    const index = this.mealPlan[meal].indexOf(dish);
    if (index > -1) {
      this.mealPlan[meal].splice(index, 1);
    }
  },
});
