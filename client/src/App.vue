<template>
  <el-config-provider namespace="ep">
    <BaseHeader />
    <RouterView />
  </el-config-provider>
</template>

<style>
#app {
  color: var(--ep-text-color-primary);
}
</style>
