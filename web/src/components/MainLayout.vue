<template>
  <div class="layout">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-icon">🏫</span>
          <span class="logo-text">校园二手</span>
        </div>
        <div class="nav-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索你想要的宝贝..."
            size="large"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="nav-actions">
          <el-button type="primary" @click="$router.push('/product/publish')">
            <el-icon><Plus /></el-icon>
            发布
          </el-button>
          <template v-if="userStore.isLogin">
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="32" :src="userStore.userInfo.avatar">
                  {{ userStore.userInfo.nickname?.charAt(0) || userStore.userInfo.username?.charAt(0) }}
                </el-avatar>
                <span class="nickname">{{ userStore.userInfo.nickname || userStore.userInfo.username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">👤 个人中心</el-dropdown-item>
                  <el-dropdown-item command="orders">📦 我的订单</el-dropdown-item>
                  <el-dropdown-item command="favorites">❤️ 我的收藏</el-dropdown-item>
                  <el-dropdown-item command="products">🏷️ 我发布的</el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isAdmin" command="admin">🛡️ 管理后台</el-dropdown-item>
                  <el-dropdown-item command="ai-service">🤖 智能客服</el-dropdown-item>
                  <el-dropdown-item divided command="logout">🚪 退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </header>

    <!-- 分类导航 -->
    <nav class="category-bar">
      <div class="container">
        <div class="category-list">
          <span class="category-all" @click="$router.push('/product')">全部商品</span>
          <span
            v-for="cat in categories"
            :key="cat.id"
            class="category-item"
            @click="$router.push(`/product?category_id=${cat.id}`)"
          >
            {{ cat.name }}
          </span>
        </div>
      </div>
    </nav>

    <!-- 主体内容 -->
    <main class="content">
      <slot />
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-col">
            <h4>关于平台</h4>
            <p>校园二手交易智能分析与推荐平台</p>
            <p>安全 · 便捷 · 实惠</p>
          </div>
          <div class="footer-col">
            <h4>快速导航</h4>
            <ul>
              <li><a href="#" @click.prevent="$router.push('/product')">商品分类</a></li>
              <li><a href="#" @click.prevent="$router.push('/product?sort=hot')">热门商品</a></li>
              <li><a href="#" @click.prevent="$router.push('/product?sort=new')">最新上架</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>帮助中心</h4>
            <ul>
              <li><a href="#">交易指南</a></li>
              <li><a href="#">安全须知</a></li>
              <li><a href="#">联系客服</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>联系我们</h4>
            <p>📧 contact@campus-trade.com</p>
            <p>📱 微信公众号: 校园二手</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2024 校园二手交易平台 · All rights reserved</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { productApi } from '@/api'
import { Search, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const searchKeyword = ref('')
const categories = ref([])

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push(`/product?keyword=${encodeURIComponent(searchKeyword.value)}`)
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile': router.push('/user/profile'); break
    case 'orders': router.push('/order'); break
    case 'favorites': router.push('/user/favorites'); break
    case 'products': router.push('/user/products'); break
    case 'admin': router.push('/admin/dashboard'); break
    case 'ai-service': router.push('/ai/service'); break
    case 'logout':
      userStore.logout()
      router.push('/')
      break
  }
}

onMounted(async () => {
  try {
    const data = await productApi.getCategories()
    categories.value = data || []
  } catch (e) {
    console.error('加载分类失败:', e)
  }
})
</script>

<style lang="scss" scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

// ========== Header ==========
.header {
  background: #fff;
  box-shadow: 0 1px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;

  .container {
    display: flex;
    align-items: center;
    height: 60px;
    gap: 24px;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    flex-shrink: 0;

    .logo-icon {
      font-size: 24px;
    }

    .logo-text {
      font-size: 20px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }

  .nav-search {
    flex: 1;
    max-width: 500px;

    :deep(.el-input__wrapper) {
      border-radius: 20px;
    }

    :deep(.el-input-group__append) {
      border-radius: 0 20px 20px 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      color: #fff;
    }
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 16px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      .nickname {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

// ========== Category Bar ==========
.category-bar {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;

  .container {
    padding: 0 20px;
  }

  .category-list {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 10px 0;
    overflow-x: auto;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .category-all {
    font-size: 14px;
    font-weight: 600;
    color: #667eea;
    cursor: pointer;
    flex-shrink: 0;

    &:hover {
      color: #764ba2;
    }
  }

  .category-item {
    font-size: 14px;
    color: #666;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
    padding: 4px 0;
    border-bottom: 2px solid transparent;

    &:hover {
      color: #667eea;
      border-bottom-color: #667eea;
    }
  }
}

// ========== Content ==========
.content {
  flex: 1;
  padding: 24px 0;
}

// ========== Footer ==========
.footer {
  background: #1a1a2e;
  color: #fff;
  padding: 48px 0 24px;
  margin-top: 48px;

  .footer-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 40px;
    margin-bottom: 32px;
  }

  .footer-col {
    h4 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      color: #fff;
    }

    p {
      font-size: 14px;
      color: #999;
      line-height: 1.8;
    }

    ul {
      li {
        margin-bottom: 10px;

        a {
          font-size: 14px;
          color: #999;
          transition: color 0.3s;

          &:hover {
            color: #667eea;
          }
        }
      }
    }
  }

  .footer-bottom {
    padding-top: 24px;
    border-top: 1px solid #2d2d44;
    text-align: center;
    color: #666;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .header .container {
    gap: 12px;
  }

  .nav-search {
    display: none;
  }

  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}
</style>
