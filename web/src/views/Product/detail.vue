<template>
  <div class="product-detail-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-text">校园二手</span>
        </div>
        <div class="nav-links">
          <span @click="$router.push('/')">首页</span>
          <span @click="$router.push('/product')">商品列表</span>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main container" v-if="product">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/product' }">商品列表</el-breadcrumb-item>
          <el-breadcrumb-item>{{ product.title }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- 商品详情 -->
      <div class="product-detail">
        <!-- 图片区域 -->
        <div class="product-images">
          <div class="main-image">
            <img :src="currentImage || 'https://picsum.photos/600/600'" :alt="product.title" />
          </div>
          <div class="thumbnail-list" v-if="product.images && product.images.length > 0">
            <div
              v-for="(img, index) in product.images"
              :key="index"
              class="thumbnail"
              :class="{ active: currentImage === img.image_url }"
              @click="currentImage = img.image_url"
            >
              <img :src="img.image_url" alt="" />
            </div>
          </div>
        </div>

        <!-- 商品信息 -->
        <div class="product-info">
          <h1 class="product-title">{{ product.title }}</h1>

          <div class="product-price">
            <span class="price-label">售价</span>
            <span class="price-current">¥{{ product.price }}</span>
            <span v-if="product.original_price" class="price-original">
              原价 ¥{{ product.original_price }}
            </span>
            <span v-if="product.original_price" class="discount">
              省{{ Math.round((1 - product.price / product.original_price) * 100) }}%
            </span>
          </div>

          <div class="product-stats">
            <span class="stat-item">
              <el-icon><View /></el-icon>
              {{ product.view_count }} 浏览
            </span>
            <span class="stat-item">
              <el-icon><Star /></el-icon>
              {{ product.favorite_count }} 收藏
            </span>
            <span class="stat-item">
              <el-icon><ChatDotRound /></el-icon>
              {{ product.chat_count }} 咨询
            </span>
          </div>

          <div class="product-attrs">
            <div class="attr-item">
              <span class="attr-label">成色：</span>
              <span class="attr-value">{{ conditionMap[product.condition] || '其他' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">分类：</span>
              <span class="attr-value">{{ product.category_name }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">交易方式：</span>
              <span class="attr-value">{{ tradeTypeMap[product.trade_type] || '面交' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">位置：</span>
              <span class="attr-value">{{ product.location || '未填写' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">发布时间：</span>
              <span class="attr-value">{{ formatDate(product.create_time) }}</span>
            </div>
          </div>

          <div class="seller-info">
            <div class="seller-avatar">
              <el-avatar :size="48" :src="product.seller?.avatar">
                {{ product.seller?.nickname?.charAt(0) || product.seller?.username?.charAt(0) }}
              </el-avatar>
            </div>
            <div class="seller-detail">
              <div class="seller-name">{{ product.seller?.nickname || product.seller?.username }}</div>
              <div class="seller-level">
                <el-tag size="small" type="success">
                  {{ product.seller?.is_real_name ? '已实名认证' : '未认证' }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="action-buttons">
            <el-button size="large" @click="handleChat">
              <el-icon><ChatDotRound /></el-icon>
              联系卖家
            </el-button>
            <el-button size="large" type="primary" @click="handleBuy">
              立即购买
            </el-button>
            <el-button size="large" @click="handleFavorite">
              <el-icon>
                <Star v-if="!isFavorite" />
                <StarFilled v-else style="color: #f56c6c" />
              </el-icon>
              {{ isFavorite ? '已收藏' : '收藏' }}
            </el-button>
            <el-button size="large" @click="handleAddCart">
              <el-icon><ShoppingCart /></el-icon>
              加入购物车
            </el-button>
          </div>
        </div>
      </div>

      <!-- 商品描述 -->
      <div class="product-description">
        <h3 class="section-title">商品描述</h3>
        <div class="description-content" v-html="product.description"></div>
      </div>

      <!-- 相似推荐 -->
      <div class="similar-products">
        <h3 class="section-title">相似推荐</h3>
        <div class="product-grid">
          <div
            v-for="item in similarProducts"
            :key="item.id"
            class="product-card"
            @click="$router.push(`/product/${item.id}`)"
          >
            <div class="product-image">
              <img :src="item.cover_image || 'https://picsum.photos/300/300'" :alt="item.title" />
            </div>
            <div class="product-info">
              <h4 class="product-title">{{ item.title }}</h4>
              <div class="product-price">
                <span class="price-current">¥{{ item.price }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi, recommendApi, orderApi } from '@/api'
import { ElMessage } from 'element-plus'
import {
  View, Star, StarFilled, ChatDotRound, ShoppingCart
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const currentImage = ref('')
const isFavorite = ref(false)
const similarProducts = ref([])

const conditionMap = {
  1: '全新',
  2: '九成新',
  3: '八成新',
  4: '七成新',
  5: '其他'
}

const tradeTypeMap = {
  1: '面交',
  2: '邮寄',
  3: '面交+邮寄'
}

const formatDate = (date) => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadProduct = async () => {
  const productId = route.params.id
  try {
    const data = await productApi.getProductDetail(productId)
    product.value = data
    isFavorite.value = data.is_favorite || false

    // 设置主图
    if (data.images && data.images.length > 0) {
      const cover = data.images.find(img => img.is_cover === 1)
      currentImage.value = cover ? cover.image_url : data.images[0].image_url
    }
  } catch (error) {
    console.error('加载商品详情失败:', error)
  }
}

const loadSimilarProducts = async () => {
  const productId = route.params.id
  try {
    const data = await recommendApi.getSimilarProducts(productId, 8)
    similarProducts.value = data
  } catch (error) {
    console.error('加载相似商品失败:', error)
  }
}

const handleChat = () => {
  if (!product.value?.seller?.id) return
  router.push(`/chat/${product.value.seller.id}`)
}

const handleBuy = async () => {
  try {
    const data = await orderApi.createOrder({
      product_id: product.value.id,
      quantity: 1
    })
    router.push(`/order/${data.id}`)
  } catch (error) {
    console.error('创建订单失败:', error)
  }
}

const handleFavorite = async () => {
  try {
    await productApi.toggleFavorite(product.value.id)
    isFavorite.value = !isFavorite.value
    ElMessage.success(isFavorite.value ? '收藏成功' : '取消收藏')
  } catch (error) {
    console.error('收藏失败:', error)
  }
}

const handleAddCart = async () => {
  try {
    await orderApi.addToCart({
      product_id: product.value.id,
      quantity: 1
    })
    ElMessage.success('已加入购物车')
  } catch (error) {
    console.error('加入购物车失败:', error)
  }
}

onMounted(() => {
  loadProduct()
  loadSimilarProducts()
})
</script>

<style lang="scss" scoped>
.product-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

// 头部
.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .container {
    display: flex;
    align-items: center;
    height: 64px;
    gap: 40px;
  }

  .logo {
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;

    .logo-text {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }

  .nav-links {
    display: flex;
    gap: 24px;

    span {
      cursor: pointer;
      color: #666;
      transition: color 0.3s;

      &:hover {
        color: #409eff;
      }
    }
  }
}

// 主要内容
.main {
  padding: 24px 20px;
}

// 面包屑
.breadcrumb {
  margin-bottom: 20px;
}

// 商品详情
.product-detail {
  display: flex;
  gap: 40px;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

// 图片区域
.product-images {
  width: 480px;
  flex-shrink: 0;

  .main-image {
    width: 100%;
    height: 480px;
    border-radius: 8px;
    overflow: hidden;
    background: #f5f5f5;
    margin-bottom: 16px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .thumbnail-list {
    display: flex;
    gap: 12px;
    overflow-x: auto;
  }

  .thumbnail {
    width: 80px;
    height: 80px;
    border-radius: 6px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    flex-shrink: 0;

    &.active {
      border-color: #409eff;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}

// 商品信息
.product-info {
  flex: 1;

  .product-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 16px;
    line-height: 1.4;
  }

  .product-price {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 16px;
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    border-radius: 8px;
    margin-bottom: 20px;

    .price-label {
      font-size: 14px;
      color: #999;
    }

    .price-current {
      font-size: 36px;
      font-weight: bold;
      color: #f56c6c;
    }

    .price-original {
      font-size: 14px;
      color: #999;
      text-decoration: line-through;
    }

    .discount {
      padding: 2px 8px;
      background: #f56c6c;
      color: #fff;
      font-size: 12px;
      border-radius: 4px;
    }
  }

  .product-stats {
    display: flex;
    gap: 24px;
    padding: 16px 0;
    border-top: 1px solid #f0f0f0;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 20px;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #666;
    }
  }

  .product-attrs {
    margin-bottom: 24px;

    .attr-item {
      display: flex;
      margin-bottom: 12px;
      font-size: 14px;

      .attr-label {
        width: 80px;
        color: #999;
        flex-shrink: 0;
      }

      .attr-value {
        color: #333;
      }
    }
  }

  .seller-info {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: #f9f9f9;
    border-radius: 8px;
    margin-bottom: 24px;

    .seller-detail {
      flex: 1;
    }

    .seller-name {
      font-size: 16px;
      font-weight: 500;
      color: #333;
      margin-bottom: 4px;
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
  }
}

// 商品描述
.product-description {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }

  .description-content {
    font-size: 14px;
    line-height: 1.8;
    color: #666;
    white-space: pre-wrap;
  }
}

// 相似推荐
.similar-products {
  background: #fff;
  border-radius: 12px;
  padding: 24px;

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 20px;
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.product-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  .product-image {
    width: 100%;
    padding-top: 100%;
    background: #f5f5f5;
    position: relative;

    img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .product-info {
    padding: 12px;
    background: #fff;

    .product-title {
      font-size: 14px;
      color: #333;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      min-height: 40px;
    }

    .product-price {
      .price-current {
        font-size: 16px;
        font-weight: bold;
        color: #f56c6c;
      }
    }
  }
}

// 响应式
@media (max-width: 1024px) {
  .product-detail {
    flex-direction: column;
  }

  .product-images {
    width: 100%;
  }

  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
