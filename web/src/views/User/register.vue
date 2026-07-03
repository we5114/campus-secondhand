<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-left">
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
            <el-icon size="24"><Lock /></el-icon>
            <span>安全交易</span>
          </div>
        </div>
      </div>
      <div class="register-right">
        <div class="register-form">
          <h2>注册新账号</h2>
          <p class="subtitle">加入校园二手交易平台</p>

          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            @keyup.enter="handleRegister"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名（3-50个字符）"
                size="large"
                prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="手机号（选填）"
                size="large"
                prefix-icon="Phone"
              />
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱（选填）"
                size="large"
                prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="nickname">
              <el-input
                v-model="registerForm.nickname"
                placeholder="昵称（选填）"
                size="large"
                prefix-icon="UserFilled"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（至少6位）"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="register-btn"
                :loading="loading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-link">
            已有账号？
            <router-link to="/login">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Goods, MagicStick, ChatDotRound, User, Lock, Phone, Message, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  phone: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3到50个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
  } catch (error) {
    return
  }

  loading.value = true
  try {
    const data = await userApi.register({
      username: registerForm.username,
      password: registerForm.password,
      phone: registerForm.phone || null,
      email: registerForm.email || null,
      nickname: registerForm.nickname || registerForm.username
    })

    ElMessage.success('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
    const msg = error?.response?.data?.message || error?.message || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.register-left {
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

.register-right {
  flex: 1;
  padding: 60px 40px;
}

.register-form {
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

  .register-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
  }

  .login-link {
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
  .register-container {
    flex-direction: column;
  }

  .register-left {
    padding: 40px 30px;

    .features {
      display: none;
    }
  }

  .register-right {
    padding: 40px 30px;
  }
}
</style>
