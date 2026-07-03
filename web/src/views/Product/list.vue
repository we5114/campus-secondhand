<template>
  <MainLayout>
    <div class="product-list-page">
      <!-- 筛选区 -->
      <section class="filter-section">
        <div class="filter-row">
          <span class="filter-label">分类</span>
          <div class="filter-tags">
            <span
              class="filter-tag"
              :class="{ active: !queryParams.category_id }"
              @click="handleCategory(null)"
            >全部</span>
            <span
              v-for="cat in categories"
              :key="cat.id"
              class="filter-tag"
              :class="{ active: queryParams.category_id === cat.id }"
              @click="handleCategory(cat.id)"
            >{{ cat.name }}</span>
          </div>
        </div>
        <div class="filter-row">
          <span class="filter-label">价格</span>
          <div class="filter-tags">
            <span
              class="filter-tag"
              :class="{ active: !priceRange }"
              @click="handlePrice(null)"
            >不限</span>
            <span
              v-for="r in priceRanges"
              :key="r.label"
              class="filter-tag"
              :class="{ active: priceRange === r.label }"
              @click="handlePrice(r)"
            >{{ r.label }}</span>
          </div>
        </div>
        <div class="filter-row">
          <span class="filter-label">成色</span>
          <div class="filter-tags">
            <span
              class="filter-tag"
              :class="{ active: !queryParams.condition }"
              @click="handleCondition(null)"
            >不限</span>
            <span
              v-for="c in conditions"
              :key="c.value"
              class="filter-tag"
              :class="{ active: queryParams.condition === c.value }"
              @click="handleCondition(c.value)"
            >{{ c.label }}</span>
          </div>
        </div>
      </section>

      <!-- 排序和结果 -->
      <section class="result-section">
        <div class="result-header">
          <div class="sort-btns">
            <span
              class="sort-btn"
              :class="{ active: queryParams.sort_by === 'create_time' }"
              @click="handleSort('create_time')"
            >最新</span>
            <span
              class="sort-btn"
              :class="{ active: queryParams.sort_by === 'view_count' }"
              @click="handleSort('view_count')"
            >最热</span>
            <span
              class="sort-btn"
              :class="{ active: queryParams.sort_by === 'price' }"
              @click="handleSort('price')"
            >价格</span>
          </div>
          <span class="result-count">共 {{ total }} 件商品</span>
        </div>

        <div v-if="productList.length > 0" class="product-grid">
          <div
            v-for="p in productList"
            :key="p.id"
            class="product-card"
            @click="$router.push(`/product/${p.id}`)"
          >
            <div class="product-image">
              <img :src="p.cover_image || 'https://picsum.photos/300/300'" :alt="p.title" />
              <div v-if="p.is_top" class="badge badge-hot">置顶</div>
              <div v-if="p.is_recommend" class="badge badge-rec">推荐</div>
            </div>
            <div class="product-detail">
              <h4 class="title">{{ p.title }}</h4>
              <div class="price-row">
                <span class="price">¥{{ p.price }}</span>
                <span v-if="p.original_price" class="original">¥{{ p.original_price }}</span>
              </div>
              <div class="meta">
                <span class="seller">{{ p.seller_name }}</span>
                <span class="views"><el-icon><View /></el-icon>{{ p.view_count }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty">
          <el-empty description="暂无商品" />
        </div>

        <div v-if="total > 0" class="pagination">
          <el-pagination
            v-model:current-page="queryParams.page"
            v-model:page-size="queryParams.page_size"
            :total="total"
            :page-sizes="[20, 40, 60]"
            layout="total, sizes, prev, pager, next"
          />
        </div>
      </section>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { productApi } from '@/api'
import { View } from '@element-plus/icons-vue'
import MainLayout from '@/components/MainLayout.vue'

const route = useRoute()
const categories = ref([])
const productList = ref([])
const total = ref(0)
const priceRange = ref(null)

const queryParams = reactive({
  page: 1,
  page_size: 20,
  category_id: null,
  keyword: '',
  min_price: null,
  max_price: null,
  condition: null,
  sort_by: 'create_time',
  sort_order: 'desc'
})

const priceRanges = [
  { label: '50以下', min: 0, max: 50 },
  { label: '50-100', min: 50, max: 100 },
  { label: '100-300', min: 100, max: 300 },
  { label: '300-500', min: 300, max: 500 },
  { label: '500以上', min: 500, max: null }
]

const conditions = [
  { label: '全新', value: 1 },
  { label: '九成新', value: 2 },
  { label: '八成新', value: 3 },
  { label: '七成新', value: 4 },
  { label: '其他', value: 5 }
]

const handleCategory = (id) => {
  queryParams.category_id = id
  queryParams.page = 1
  load()
}

const handlePrice = (r) => {
  if (r) {
    priceRange.value = r.label
    queryParams.min_price = r.min
    queryParams.max_price = r.max
  } else {
    priceRange.value = null
    queryParams.min_price = null
    queryParams.max_price = null
  }
  queryParams.page = 1
  load()
}

const handleCondition = (v) => {
  queryParams.condition = v
  queryParams.page = 1
  load()
}

const handleSort = (by) => {
  queryParams.sort_by = by
  queryParams.sort_order = by === 'price' ? (queryParams.sort_order === 'asc' ? 'desc' : 'asc') : 'desc'
  load()
}

const load = async () => {
  try {
    const data = await productApi.getProductList(queryParams)
    productList.value = data?.list || []
    total.value = data?.total || 0
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  if (route.query.keyword) queryParams.keyword = route.query.keyword
  if (route.query.category_id) queryParams.category_id = parseInt(route.query.category_id)
  if (route.query.sort === 'hot') { queryParams.sort_by = 'view_count'; queryParams.sort_order = 'desc' }
  if (route.query.sort === 'new') { queryParams.sort_by = 'create_time'; queryParams.sort_order = 'desc' }
  try {
    categories.value = await productApi.getCategories() || []
  } catch (e) {}
  load()
})
</script>

<style lang="scss" scoped>
.product-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.filter-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  .filter-row {
    display: flex;
    padding: 12px 0;
    border-bottom: 1px solid #f5f5f5;

    &:last-child {
      border-bottom: none;
    }
  }

  .filter-label {
    width: 60px;
    flex-shrink: 0;
    font-size: 14px;
    color: #666;
    line-height: 32px;
  }

  .filter-tags {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .filter-tag {
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 14px;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    background: #f8f8fa;

    &:hover {
      color: #667eea;
      background: #f0f2ff;
    }

    &.active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
    }
  }
}

.result-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;

  .sort-btns {
    display: flex;
    gap: 24px;
  }

  .sort-btn {
    font-size: 14px;
    color: #666;
    cursor: pointer;
    padding: 4px 0;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;

    &:hover {
      color: #667eea;
    }

    &.active {
      color: #667eea;
      font-weight: 600;
      border-bottom-color: #667eea;
    }
  }

  .result-count {
    font-size: 14px;
    color: #999;
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.product-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #f0f0f0;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.18);

    img {
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

.empty {
  padding: 40px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 1024px) {
  .product-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
  .product-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
