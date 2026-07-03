<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <h1>校园二手交易平台</h1>
          <p>安全、便捷、实惠的校园二手交易体验</p>
        </div>
        <div class="features">
          <div class="feature-item">
            <el-icon size="24"><Goods /></el-icon>
            <span>海量商品</span>
          </div>
          <div class="feature-item">
            <el-icon size="24"><MagicStick /></el-icon>
            <span>智能推荐</span>
          </div>
          <div class="feature-item">
            <el-icon size="24"><ChatDotRound /></el-icon>
            <span>AI客服</span>
          </div>
          <div class="feature-item">
            <span>安全交易</span>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-form">
          <h2>欢迎回来</h2>
          <p class="subtitle">登录您的账号</p>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名/手机号/邮箱"
                size="large"
                prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                <a href="#" class="forgot-password">忘记密码？</a>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="register-link">
            还没有账号？
            <router-link to="/register">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Goods, MagicStick, ChatDotRound, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
  } catch (error) {
    return
  }

  loading.value = true
  try {
    const data = await userApi.login(loginForm)
    userStore.setToken(data.token)
    userStore.setUserInfo(data.user_info)

    ElMessage.success('登录成功')

    // 跳转到之前的页面或首页
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .brand {
    h1 {
      font-size: 28px;
      margin-bottom: 12px;
    }

    p {
      font-size: 14px;
      opacity: 0.9;
    }
  }

  .features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 14px;
    }
  }
}

.login-right {
  flex: 1;
  padding: 60px 40px;
}

.login-form {
  h2 {
    font-size: 24px;
    margin-bottom: 8px;
    color: #333;
  }

  .subtitle {
    color: #999;
    margin-bottom: 32px;
    font-size: 14px;
  }

  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .forgot-password {
      color: #409eff;
      font-size: 14px;
    }
  }

  .login-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
  }

  .register-link {
    text-align: center;
    margin-top: 24px;
    color: #666;
    font-size: 14px;

    a {
      color: #409eff;
      margin-left: 4px;
    }
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-left {
    padding: 40px 30px;

    .features {
      display: none;
    }
  }

  .login-right {
    padding: 40px 30px;
  }
}
</style>
