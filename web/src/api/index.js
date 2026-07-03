import request from '@/utils/request'

// 用户相关API
export const userApi = {
  // 注册
  register(data) {
    return request.post('/user/register', data)
  },

  // 登录
  login(data) {
    return request.post('/user/login', data)
  },

  // 获取用户信息
  getUserInfo() {
    return request.get('/user/info')
  },

  // 更新用户信息
  updateUserInfo(data) {
    return request.put('/user/info', data)
  },

  // 修改密码
  updatePassword(data) {
    return request.put('/user/password', data)
  },

  // 获取用户详情
  getUserDetail(userId) {
    return request.get(`/user/${userId}`)
  },

  // 申请实名认证
  applyRealName(data) {
    return request.post('/user/real-name', data)
  }
}

// 商品相关API
export const productApi = {
  // 获取分类树
  getCategories() {
    return request.get('/product/categories')
  },

  // 获取商品列表
  getProductList(params) {
    return request.get('/product/list', { params })
  },

  // 获取商品详情
  getProductDetail(productId) {
    return request.get(`/product/${productId}`)
  },

  // 发布商品
  createProduct(data) {
    return request.post('/product', data)
  },

  // 更新商品
  updateProduct(productId, data) {
    return request.put(`/product/${productId}`, data)
  },

  // 删除商品
  deleteProduct(productId) {
    return request.delete(`/product/${productId}`)
  },

  // 收藏/取消收藏
  toggleFavorite(productId) {
    return request.post(`/product/${productId}/favorite`)
  },

  // 获取我的收藏
  getMyFavorites(params) {
    return request.get('/product/my/favorites', { params })
  },

  // 获取我发布的商品
  getMyProducts(params) {
    return request.get('/product/my/products', { params })
  },

  // 获取热门商品
  getHotProducts(limit = 10) {
    return request.get('/product/hot/list', { params: { limit } })
  },

  // 获取最新商品
  getNewProducts(limit = 10) {
    return request.get('/product/new/list', { params: { limit } })
  }
}

// 订单相关API
export const orderApi = {
  // 创建订单
  createOrder(data) {
    return request.post('/order', data)
  },

  // 获取订单列表
  getOrderList(params) {
    return request.get('/order/list', { params })
  },

  // 获取订单详情
  getOrderDetail(orderId) {
    return request.get(`/order/${orderId}`)
  },

  // 支付订单
  payOrder(orderId, data) {
    return request.post(`/order/${orderId}/pay`, data)
  },

  // 取消订单
  cancelOrder(orderId, data) {
    return request.post(`/order/${orderId}/cancel`, data)
  },

  // 发货
  shipOrder(orderId) {
    return request.post(`/order/${orderId}/ship`)
  },

  // 确认收货
  confirmReceipt(orderId) {
    return request.post(`/order/${orderId}/confirm`)
  },

  // 申请退款
  applyRefund(orderId, data) {
    return request.post(`/order/${orderId}/refund`, data)
  },

  // 购物车列表
  getCartList() {
    return request.get('/order/cart/list')
  },

  // 添加到购物车
  addToCart(data) {
    return request.post('/order/cart/add', data)
  },

  // 更新购物车
  updateCartItem(cartId, data) {
    return request.put(`/order/cart/${cartId}`, data)
  },

  // 从购物车移除
  removeFromCart(data) {
    return request.delete('/order/cart', { data })
  },

  // 创建评价
  createReview(orderId, data) {
    return request.post(`/order/${orderId}/review`, data)
  },

  // 获取商品评价
  getProductReviews(productId, params) {
    return request.get(`/order/product/${productId}/reviews`, { params })
  }
}

// 推荐相关API
export const recommendApi = {
  // 首页推荐
  getHomeRecommend(limit = 20) {
    return request.get('/recommend/home', { params: { limit } })
  },

  // 相似商品推荐
  getSimilarProducts(productId, limit = 10) {
    return request.get(`/recommend/similar/${productId}`, { params: { limit } })
  },

  // 个性化推荐
  getPersonalizedRecommend(limit = 20) {
    return request.get('/recommend/personalized', { params: { limit } })
  }
}

// 聊天相关API
export const chatApi = {
  // 获取会话列表
  getSessionList(params) {
    return request.get('/chat/sessions', { params })
  },

  // 获取消息列表
  getMessageList(otherUserId, params) {
    return request.get(`/chat/messages/${otherUserId}`, { params })
  },

  // 发送消息
  sendMessage(data) {
    return request.post('/chat/send', data)
  },

  // 标记已读
  markAsRead(otherUserId) {
    return request.post(`/chat/read/${otherUserId}`)
  },

  // 获取未读消息数
  getUnreadCount() {
    return request.get('/chat/unread')
  },

  // 获取系统消息
  getSystemMessages(params) {
    return request.get('/chat/system', { params })
  }
}

// 大模型相关API
export const llmApi = {
  // AI对话
  chatWithAI(data) {
    return request.post('/llm/chat', data)
  },

  // 生成商品描述
  generateDescription(data) {
    return request.post('/llm/generate-description', data)
  },

  // 内容审核
  contentModeration(data) {
    return request.post('/llm/moderation', data)
  },

  // 智能定价
  smartPricing(data) {
    return request.post('/llm/smart-pricing', data)
  },

  // 情感分析
  sentimentAnalysis(data) {
    return request.post('/llm/sentiment', data)
  }
}

// 管理后台相关API
export const adminApi = {
  // 仪表盘统计
  getDashboardStats() {
    return request.get('/admin/dashboard/stats')
  },

  // 销售趋势
  getSalesTrend(days = 7) {
    return request.get('/admin/dashboard/sales-trend', { params: { days } })
  },

  // 分类统计
  getCategoryStats() {
    return request.get('/admin/dashboard/category-stats')
  },

  // 用户列表
  getUserList(params) {
    return request.get('/admin/users', { params })
  },

  // 更新用户状态
  updateUserStatus(userId, data) {
    return request.put(`/admin/users/${userId}/status`, data)
  },

  // 实名认证列表
  getRealNameList(params) {
    return request.get('/admin/real-name', { params })
  },

  // 审核实名认证
  auditRealName(id, data) {
    return request.post(`/admin/real-name/${id}/audit`, data)
  },

  // 商品列表
  getProductList(params) {
    return request.get('/admin/products', { params })
  },

  // 更新商品状态
  updateProductStatus(productId, data) {
    return request.put(`/admin/products/${productId}/status`, data)
  },

  // 设置商品推荐
  setProductRecommend(productId, data) {
    return request.put(`/admin/products/${productId}/recommend`, data)
  },

  // 订单列表
  getOrderList(params) {
    return request.get('/admin/orders', { params })
  }
}
