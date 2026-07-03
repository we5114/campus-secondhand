import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home/index.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/product',
    name: 'ProductList',
    component: () => import('@/views/Product/list.vue'),
    meta: { title: '商品列表' }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('@/views/Product/detail.vue'),
    meta: { title: '商品详情' }
  },
  {
    path: '/product/publish',
    name: 'ProductPublish',
    component: () => import('@/views/Product/publish.vue'),
    meta: { title: '发布商品', requiresAuth: true }
  },
  {
    path: '/user',
    name: 'User',
    component: () => import('@/views/User/index.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('@/views/User/profile.vue'),
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    path: '/user/favorites',
    name: 'UserFavorites',
    component: () => import('@/views/User/favorites.vue'),
    meta: { title: '我的收藏', requiresAuth: true }
  },
  {
    path: '/user/products',
    name: 'UserProducts',
    component: () => import('@/views/User/products.vue'),
    meta: { title: '我发布的', requiresAuth: true }
  },
  {
    path: '/order',
    name: 'OrderList',
    component: () => import('@/views/Order/index.vue'),
    meta: { title: '我的订单', requiresAuth: true }
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: () => import('@/views/Order/detail.vue'),
    meta: { title: '订单详情', requiresAuth: true }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/Order/cart.vue'),
    meta: { title: '购物车', requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat/index.vue'),
    meta: { title: '消息中心', requiresAuth: true }
  },
  {
    path: '/chat/:userId',
    name: 'ChatDetail',
    component: () => import('@/views/Chat/detail.vue'),
    meta: { title: '聊天', requiresAuth: true }
  },
  {
    path: '/ai/service',
    name: 'AIService',
    component: () => import('@/views/AI/service.vue'),
    meta: { title: '智能客服', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin/index.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/Admin/dashboard.vue'),
    meta: { title: '数据看板', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/Admin/users.vue'),
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: () => import('@/views/Admin/products.vue'),
    meta: { title: '商品管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'AdminOrders',
    component: () => import('@/views/Admin/orders.vue'),
    meta: { title: '订单管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/User/login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/User/register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 校园二手交易平台`
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      // 检查是否需要管理员权限
      if (to.meta.requiresAdmin) {
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        if (userInfo.user_level !== 99) {
          next({ path: '/' })
          return
        }
      }
      next()
    }
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
