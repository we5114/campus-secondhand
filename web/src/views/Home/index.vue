<template>
  <MainLayout>
    <!-- Banner -->
    <div class="home-page">
      <section class="banner-section">
        <el-carousel height="360px" :interval="5000" arrow="always">
          <el-carousel-item>
            <div class="banner banner-1">
              <div class="banner-content">
                <h2>校园二手交易平台</h2>
                <p>安全 · 便捷 · 实惠 · 智能推荐</p>
                <el-button type="primary" size="large" @click="$router.push('/product')">
                  开始逛商品
                </el-button>
              </div>
            </div>
          </el-carousel-item>
          <el-carousel-item>
            <div class="banner banner-2">
              <div class="banner-content">
                <h2>🤖 AI 智能推荐</h2>
                <p>基于大数据的个性化商品推荐</p>
                <el-button type="primary" size="large" @click="$router.push('/product?sort=hot')">
                  查看热门商品
                </el-button>
              </div>
            </div>
          </el-carousel-item>
          <el-carousel-item>
            <div class="banner banner-3">
              <div class="banner-content">
                <h2>📱 随时随地交易</h2>
                <p>手机发布 · 面交邮寄 · 安全交易</p>
                <el-button type="primary" size="large" @click="$router.push('/register')">
                  立即注册
                </el-button>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </section>

      <!-- Stats Bar -->
      <section class="stats-bar">
        <div class="stat-item">
          <span class="stat-num">{{ hotProducts.length || 5 }}</span>
          <span class="stat-label">在售商品</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ newProducts.length || 3 }}</span>
          <span class="stat-label">今日新增</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">100%</span>
          <span class="stat-label">实名认证</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">7×24h</span>
          <span class="stat-label">AI客服在线</span>
        </div>
      </section>

      <!-- Hot Products -->
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <span class="title-icon">🔥</span>
            <h3>热门商品</h3>
          </div>
          <el-button text @click="$router.push('/product?sort=hot')">
            查看更多 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="product-grid">
          <div
            v-for="product in hotProducts"
            :key="product.id"
            class="product-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <div class="product-image">
              <img :src="product.cover_image || 'https://picsum.photos/300/300'" :alt="product.title" />
              <div v-if="product.is_top" class="badge badge-hot">置顶</div>
              <div v-if="product.is_recommend" class="badge badge-rec">推荐</div>
            </div>
            <div class="product-detail">
              <h4 class="title">{{ product.title }}</h4>
              <div class="price-row">
                <span class="price">¥{{ product.price }}</span>
                <span v-if="product.original_price" class="original">¥{{ product.original_price }}</span>
              </div>
              <div class="meta">
                <span class="seller">{{ product.seller_name }}</span>
                <span class="views">
                  <el-icon><View /></el-icon>
                  {{ product.view_count }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- New Products -->
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <span class="title-icon">✨</span>
            <h3>最新上架</h3>
          </div>
          <el-button text @click="$router.push('/product?sort=new')">
            查看更多 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="product-grid">
          <div
            v-for="product in newProducts"
            :key="product.id"
            class="product-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <div class="product-image">
              <img :src="product.cover_image || 'https://picsum.photos/300/300'" :alt="product.title" />
              <div class="badge badge-new">NEW</div>
            </div>
            <div class="product-detail">
              <h4 class="title">{{ product.title }}</h4>
              <div class="price-row">
                <span class="price">¥{{ product.price }}</span>
              </div>
              <div class="meta">
                <span class="category">{{ product.category_name }}</span>
                <span class="location">{{ product.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recommend -->
      <section v-if="userStore.isLogin" class="section">
        <div class="section-header">
          <div class="section-title">
            <span class="title-icon">💡</span>
            <h3>为你推荐</h3>
          </div>
        </div>
        <div class="product-grid">
          <div
            v-for="product in recommendProducts"
            :key="product.id"
            class="product-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <div class="product-image">
              <img :src="product.cover_image || 'https://picsum.photos/300/300'" :alt="product.title" />
            </div>
            <div class="product-detail">
              <h4 class="title">{{ product.title }}</h4>
              <div class="price-row">
                <span class="price">¥{{ product.price }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { productApi, recommendApi } from '@/api'
import { ArrowRight, View } from '@element-plus/icons-vue'
import MainLayout from '@/components/MainLayout.vue'

const router = useRouter()
const userStore = useUserStore()

const hotProducts = ref([])
const newProducts = ref([])
const recommendProducts = ref([])

const loadHot = async () => {
  try {
    const data = await productApi.getHotProducts(8)
    hotProducts.value = data || []
  } catch (e) {
    console.error(e)
  }
}

const loadNew = async () => {
  try {
    const data = await productApi.getNewProducts(8)
    newProducts.value = data || []
  } catch (e) {
    console.error(e)
  }
}

const loadRecommend = async () => {
  if (!userStore.isLogin) return
  try {
    const data = await recommendApi.getHomeRecommend(8)
    recommendProducts.value = data?.list || []
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadHot()
  loadNew()
  loadRecommend()
})
</script>

<style lang="scss" scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

// Banner
.banner-section {
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.banner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;

  &.banner-1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  &.banner-2 {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }
  &.banner-3 {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  .banner-content {
    text-align: center;
    max-width: 600px;

    h2 {
      font-size: 42px;
      font-weight: 700;
      margin-bottom: 16px;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    p {
      font-size: 18px;
      opacity: 0.9;
      margin-bottom: 24px;
    }
  }
}

// Stats Bar
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  }

  .stat-num {
    display: block;
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }

  .stat-label {
    font-size: 14px;
    color: #999;
  }
}

// Section
.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;

    .title-icon {
      font-size: 24px;
    }

    h3 {
      font-size: 20px;
      font-weight: 600;
      color: #333;
    }
  }
}

// Product Grid
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.product-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.18);

    .product-image img {
      transform: scale(1.05);
    }
  }

  .product-image {
    position: relative;
    width: 100%;
    padding-top: 100%;
    background: #f8f8fa;
    overflow: hidden;

    img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.5s;
    }

    .badge {
      position: absolute;
      top: 8px;
      left: 8px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      color: #fff;

      &.badge-hot {
        background: linear-gradient(135deg, #f56c6c, #e85d5d);
      }
      &.badge-rec {
        background: linear-gradient(135deg, #e6a23c, #d99529);
      }
      &.badge-new {
        background: linear-gradient(135deg, #67c23a, #5ab832);
      }
    }
  }

  .product-detail {
    padding: 14px;

    .title {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 10px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      line-height: 1.5;
      min-height: 42px;
    }

    .price-row {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 10px;

      .price {
        font-size: 20px;
        font-weight: 700;
        color: #f56c6c;
      }

      .original {
        font-size: 12px;
        color: #ccc;
        text-decoration: line-through;
      }
    }

    .meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #999;

      .views {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

// Responsive
@media (max-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .banner-content h2 {
    font-size: 28px;
  }
}
</style>
