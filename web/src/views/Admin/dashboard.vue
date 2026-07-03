<template>
  <div class="admin-dashboard">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-text">管理后台</span>
      </div>
      <nav class="nav-menu">
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'dashboard' }"
          @click="activeMenu = 'dashboard'; $router.push('/admin/dashboard')"
        >
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'users' }"
          @click="activeMenu = 'users'; $router.push('/admin/users')"
        >
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'products' }"
          @click="activeMenu = 'products'; $router.push('/admin/products')"
        >
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'orders' }"
          @click="activeMenu = 'orders'; $router.push('/admin/orders')"
        >
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </div>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="page-title">数据看板</div>
        <div class="user-info">
          <el-avatar :size="32">A</el-avatar>
          <span>管理员</span>
        </div>
      </header>

      <!-- 内容区 -->
      <div class="content">
        <!-- 统计卡片 -->
        <div class="stat-cards">
          <div class="stat-card card-blue">
            <div class="card-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.users?.total || 0 }}</div>
              <div class="card-label">用户总数</div>
              <div class="card-trend">
                <span class="trend-up">+{{ stats.users?.today_new || 0 }}</span>
                今日新增
              </div>
            </div>
          </div>

          <div class="stat-card card-green">
            <div class="card-icon">
              <el-icon><Goods /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.products?.total || 0 }}</div>
              <div class="card-label">商品总数</div>
              <div class="card-trend">
                <span class="trend-up">{{ stats.products?.on_shelf || 0 }}</span>
                在售商品
              </div>
            </div>
          </div>

          <div class="stat-card card-orange">
            <div class="card-icon">
              <el-icon><List /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.orders?.total || 0 }}</div>
              <div class="card-label">订单总数</div>
              <div class="card-trend">
                <span class="trend-up">+{{ stats.orders?.today_new || 0 }}</span>
                今日订单
              </div>
            </div>
          </div>

          <div class="stat-card card-purple">
            <div class="card-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">¥{{ formatAmount(stats.orders?.total_amount || 0) }}</div>
              <div class="card-label">交易总额</div>
              <div class="card-trend">
                <span class="trend-up">12.5%</span>
                较上周
              </div>
            </div>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-row">
          <!-- 销售趋势图 -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>销售趋势</h3>
              <el-radio-group v-model="salesDays" size="small" @change="loadSalesTrend">
                <el-radio-button :value="7">7天</el-radio-button>
                <el-radio-button :value="14">14天</el-radio-button>
                <el-radio-button :value="30">30天</el-radio-button>
              </el-radio-group>
            </div>
            <div ref="salesChartRef" class="chart-container"></div>
          </div>

          <!-- 分类统计 -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>商品分类分布</h3>
            </div>
            <div ref="categoryChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 待处理事项 -->
        <div class="pending-section">
          <div class="pending-card">
            <div class="pending-header">
              <h3>待处理事项</h3>
            </div>
            <div class="pending-list">
              <div class="pending-item">
                <div class="pending-icon icon-orange">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="pending-info">
                  <div class="pending-title">实名认证待审核</div>
                  <div class="pending-count">{{ stats.pending?.real_name || 0 }} 条</div>
                </div>
                <el-button type="primary" link @click="$router.push('/admin/real-name')">
                  去处理
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { adminApi } from '@/api'
import * as echarts from 'echarts'
import {
  DataAnalysis, User, Goods, List, Money, UserFilled
} from '@element-plus/icons-vue'

const activeMenu = ref('dashboard')
const stats = ref({})
const salesDays = ref(7)

const salesChartRef = ref(null)
const categoryChartRef = ref(null)

let salesChart = null
let categoryChart = null

const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

const loadStats = async () => {
  try {
    const data = await adminApi.getDashboardStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadSalesTrend = async () => {
  try {
    const data = await adminApi.getSalesTrend(salesDays.value)
    renderSalesChart(data)
  } catch (error) {
    console.error('加载销售趋势失败:', error)
  }
}

const loadCategoryStats = async () => {
  try {
    const data = await adminApi.getCategoryStats()
    renderCategoryChart(data)
  } catch (error) {
    console.error('加载分类统计失败:', error)
  }
}

const renderSalesChart = (data) => {
  if (!salesChartRef.value) return

  if (!salesChart) {
    salesChart = echarts.init(salesChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['订单数', '交易额']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates || []
    },
    yAxis: [
      {
        type: 'value',
        name: '订单数',
        position: 'left'
      },
      {
        type: 'value',
        name: '交易额',
        position: 'right',
        axisLabel: {
          formatter: '¥{value}'
        }
      }
    ],
    series: [
      {
        name: '订单数',
        type: 'line',
        smooth: true,
        data: data.order_counts || [],
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '交易额',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: data.amounts || [],
        itemStyle: {
          color: '#67c23a'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      }
    ]
  }

  salesChart.setOption(option)
}

const renderCategoryChart = (data) => {
  if (!categoryChartRef.value) return

  if (!categoryChart) {
    categoryChart = echarts.init(categoryChartRef.value)
  }

  const pieData = data.map(item => ({
    name: item.category_name,
    value: item.product_count
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }

  categoryChart.setOption(option)
}

// 响应式处理
const handleResize = () => {
  salesChart?.resize()
  categoryChart?.resize()
}

onMounted(async () => {
  await loadStats()
  await nextTick()
  await loadSalesTrend()
  await loadCategoryStats()

  window.addEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

// 侧边栏
.sidebar {
  width: 220px;
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid #1f2d3d;

    .logo-text {
      font-size: 18px;
      font-weight: bold;
      color: #fff;
    }
  }

  .nav-menu {
    flex: 1;
    padding: 16px 0;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    cursor: pointer;
    transition: all 0.3s;
    color: rgba(255, 255, 255, 0.65);

    &:hover {
      background: #1890ff;
      color: #fff;
    }

    &.active {
      background: #1890ff;
      color: #fff;
    }
  }
}

// 主内容区
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

// 顶部栏
.top-bar {
  height: 64px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .page-title {
    font-size: 18px;
    font-weight: 500;
    color: #333;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
  }
}

// 内容区
.content {
  flex: 1;
  padding: 24px;
}

// 统计卡片
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .card-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: #fff;

    &.card-blue {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  }

  &.card-blue .card-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  &.card-green .card-icon {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  }

  &.card-orange .card-icon {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  &.card-purple .card-icon {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  .card-info {
    flex: 1;
  }

  .card-value {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin-bottom: 4px;
  }

  .card-label {
    font-size: 14px;
    color: #999;
    margin-bottom: 8px;
  }

  .card-trend {
    font-size: 12px;
    color: #999;

    .trend-up {
      color: #67c23a;
      font-weight: 500;
      margin-right: 4px;
    }
  }
}

// 图表区域
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
  }

  .chart-container {
    height: 300px;
    width: 100%;
  }
}

// 待处理事项
.pending-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.pending-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .pending-header {
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
  }

  .pending-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .pending-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: #f9f9f9;
    border-radius: 8px;

    .pending-icon {
      width: 48px;
      height: 48px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: #fff;

      &.icon-orange {
        background: #e6a23c;
      }
    }

    .pending-info {
      flex: 1;
    }

    .pending-title {
      font-size: 14px;
      color: #333;
      margin-bottom: 4px;
    }

    .pending-count {
      font-size: 12px;
      color: #999;
    }
  }
}

// 响应式
@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .stat-cards {
    grid-template-columns: 1fr;
  }
}
</style>
