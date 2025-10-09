<template>
  <div class="login-body">
    <div class="bg"></div>
    <div class="login-panel">
      <el-form
          class="login-register"
          :model="formData"
          :rules="rules"
          ref="formDataRef"
          @submit.prevent
      >
        <div class="login-title">餐厅客流量预测系统</div>

        <!-- 账号输入 -->
        <el-form-item prop="account">
          <el-input
              size="large"
              clearable
              placeholder="请输入账号"
              v-model.trim="formData.account"
          >
            <template #prefix>
              <span class="iconfont icon-account"></span>
            </template>
          </el-input>
        </el-form-item>

        <!-- 密码输入 -->
        <el-form-item prop="password">
          <el-input
              type="password"
              size="large"
              placeholder="请输入密码"
              v-model.trim="formData.password"
              show-password
          >
            <template #prefix>
              <span class="iconfont icon-password"></span>
            </template>
          </el-input>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
              type="primary"
              class="op-btn"
              size="large"
              :loading="isLoading"
              @click="handleFakeLogin"
          >
            立即登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import {ElMessage} from "element-plus";

const router = useRouter();

// 表单数据
const formData = reactive({
  account: "",
  password: ""
});

// 加载状态
const isLoading = ref(false);

// 伪登录处理
const handleFakeLogin = () => {
  if (!formData.account || !formData.password) {
    return ElMessage.error("请输入账号和密码");
  }

  isLoading.value = true;

  // 模拟登录延迟
  setTimeout(() => {
    localStorage.setItem("isLoggedIn", "true");
    isLoading.value = false;
    router.push("/main");
  }, 1500); // 延迟 1.5 秒
};
</script>

<style lang="scss" scoped>
.login-body {
  height: 100vh;
  background: url("../assets/login-bg.jpg") no-repeat center/cover;
  display: flex;
  align-items: center;
  justify-content: center;

  .login-panel {
    width: 400px;
    padding: 30px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);

    .login-title {
      text-align: center;
      font-size: 24px;
      color: #409EFF;
      margin-bottom: 30px;
      font-weight: 600;
    }

    .op-btn {
      width: 100%;
      margin-top: 20px;
      background: #409EFF;
      transition: all 0.3s;

      &:hover {
        opacity: 0.9;
        transform: translateY(-2px);
      }
    }

    :deep(.el-input__wrapper) {
      border-radius: 6px;
      padding: 8px 15px;
    }
  }
}
</style>