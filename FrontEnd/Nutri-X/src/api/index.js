import axios from "axios";
import { store } from "../store";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
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

export const recommendRecipes = (ingredients) => {
  return api.post("/recommend", { ingredients });
};

export const evaluateMealPlan = (plan) => {
  return api.post("/evaluate", { plan });
};

export default api;
