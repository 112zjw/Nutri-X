import axios from "axios";
import { store } from "../store";

const api = axios.create({
  baseURL: "/api", // 使用相对路径，配合开发环境代理和生产环境 Nginx 反向代理
  timeout: 60000, // 识别图片可能需要较长时间
});

// 请求拦截器，添加 API Key
api.interceptors.request.use(
  (config) => {
    if (store.apiKey) {
      config.headers["x-api-key"] = store.apiKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const identifyIngredients = (formData) => {
  return api.post("/identify", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const recommendRecipes = (ingredients, userProfile = {}) => {
  return api.post("/recommend", { ingredients, user_profile: userProfile });
};

export const evaluateMealPlan = (plan) => {
  return api.post("/evaluate", { plan });
};

export default api;
