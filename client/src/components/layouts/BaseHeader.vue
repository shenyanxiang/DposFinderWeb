
<template>
  <el-menu class="el-menu-demo" mode="horizontal" :router="true" default-active="/home" :ellipsis="false" background-color="#e1f3d8">
    <el-menu-item>
      <h1 class="ml-20">DposFinder</h1>
    </el-menu-item>
    <div class="flex-grow" />
    <el-menu-item index="/home"><el-icon color="#409EFC"><HomeFilled /></el-icon>Home</el-menu-item>
    <el-menu-item index="/analysis"><el-icon color="#409EFC"><TrendCharts /></el-icon>Analysis</el-menu-item>
    <el-sub-menu index="">
      <template #title><el-icon><Grid /></el-icon>Database</template>
      <el-menu-item index="/browsemain">browse</el-menu-item>
      <el-menu-item index="/statistics">statistics</el-menu-item>
    </el-sub-menu>
    <el-menu-item index="/help"><el-icon color="#409EFC"><QuestionFilled /></el-icon>Help</el-menu-item>
    <el-menu-item index="/download"><el-icon color="#409EFC"><BrushFilled /></el-icon>Download</el-menu-item>
    <el-menu-item index="/contact"><el-icon color="#409EFC"><Comment /></el-icon>Contact</el-menu-item>
  </el-menu>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import {
  HomeFilled,
  Grid,
  TrendCharts,
  BrushFilled,
  QuestionFilled,
  Comment
} from "@element-plus/icons-vue";
</script>