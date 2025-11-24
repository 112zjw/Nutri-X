import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Recipes from "../views/Recipes.vue";
import MealPlan from "../views/MealPlan.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: Home,
    },
    {
      path: "/recipes",
      name: "recipes",
      component: Recipes,
    },
    {
      path: "/meal-plan",
      name: "meal-plan",
      component: MealPlan,
    },
  ],
});

export default router;
