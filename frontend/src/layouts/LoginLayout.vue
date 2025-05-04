<template>
  <div class="min-h-screen w-full bg-dotted-pattern bg-dot-grid flex items-center justify-center">
    <div class="ring-1 w-1/3 p-3 ring-gray-300 flex flex-col items-center rounded-md">
      <div class="brand">
        <img src="@/assets/images/favicon.svg" class="brand-image" />
        <div class="flex flex-col">
          <div class="brand-title">Finexia</div>
          <div class="brand-subtitle">Predictive Market Analytics</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
</script>
<style lang="postcss" scoped>
.brand {
  @apply flex items-center space-x-2;

  .brand-image {
    @apply w-12 h-12;
  }

  .brand-title {
    @apply text-xl font-medium;
  }

  .brand-subtitle {
    @apply text-sm;
  }
}
</style>