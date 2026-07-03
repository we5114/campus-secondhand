-- =====================================================
-- 校园二手交易智能分析与推荐平台 - 数据库初始化脚本
-- 数据库版本：MySQL 8.0+
-- 字符集：utf8mb4
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS campus_trade DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE campus_trade;

-- =====================================================
-- 一、用户系统表
-- =====================================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    `gender` TINYINT DEFAULT 0 COMMENT '性别：0-未知 1-男 2-女',
    `grade` VARCHAR(20) DEFAULT NULL COMMENT '年级',
    `major` VARCHAR(100) DEFAULT NULL COMMENT '专业',
    `campus` VARCHAR(50) DEFAULT NULL COMMENT '校区',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-禁用 2-注销',
    `user_level` TINYINT DEFAULT 1 COMMENT '用户等级：1-普通用户 2-VIP用户',
    `is_real_name` TINYINT DEFAULT 0 COMMENT '是否实名认证：0-否 1-是',
    `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_phone` (`phone`),
    UNIQUE KEY `uk_email` (`email`),
    KEY `idx_status` (`status`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 用户实名认证表
CREATE TABLE IF NOT EXISTS `user_real_name` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
    `student_id` VARCHAR(50) NOT NULL COMMENT '学号',
    `id_card` VARCHAR(50) DEFAULT NULL COMMENT '身份证号（脱敏）',
    `student_card_front` VARCHAR(255) DEFAULT NULL COMMENT '学生证正面照',
    `student_card_back` VARCHAR(255) DEFAULT NULL COMMENT '学生证反面照',
    `status` TINYINT DEFAULT 0 COMMENT '审核状态：0-待审核 1-通过 2-拒绝',
    `audit_user_id` BIGINT DEFAULT NULL COMMENT '审核人ID',
    `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
    `audit_remark` VARCHAR(255) DEFAULT NULL COMMENT '审核备注',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_id` (`user_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户实名认证表';

-- 3. 用户地址表
CREATE TABLE IF NOT EXISTS `user_address` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '地址ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `receiver` VARCHAR(50) NOT NULL COMMENT '收货人',
    `phone` VARCHAR(20) NOT NULL COMMENT '联系电话',
    `province` VARCHAR(50) DEFAULT NULL COMMENT '省份',
    `city` VARCHAR(50) DEFAULT NULL COMMENT '城市',
    `district` VARCHAR(50) DEFAULT NULL COMMENT '区县',
    `detail` VARCHAR(255) NOT NULL COMMENT '详细地址',
    `is_default` TINYINT DEFAULT 0 COMMENT '是否默认：0-否 1-是',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户地址表';

-- =====================================================
-- 二、商品系统表
-- =====================================================

-- 1. 商品分类表
CREATE TABLE IF NOT EXISTS `product_category` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
    `parent_id` INT DEFAULT 0 COMMENT '父分类ID，0表示一级分类',
    `level` TINYINT DEFAULT 1 COMMENT '分类层级：1-一级 2-二级 3-三级',
    `icon` VARCHAR(255) DEFAULT NULL COMMENT '分类图标',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-禁用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- 2. 商品表
CREATE TABLE IF NOT EXISTS `product` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    `seller_id` BIGINT NOT NULL COMMENT '卖家ID',
    `category_id` INT NOT NULL COMMENT '分类ID',
    `title` VARCHAR(100) NOT NULL COMMENT '商品标题',
    `description` TEXT COMMENT '商品描述',
    `price` DECIMAL(10,2) NOT NULL COMMENT '售价',
    `original_price` DECIMAL(10,2) DEFAULT NULL COMMENT '原价',
    `condition` TINYINT NOT NULL COMMENT '成色：1-全新 2-九成新 3-八成新 4-七成新 5-其他',
    `quality` VARCHAR(255) DEFAULT NULL COMMENT '质量描述',
    `trade_type` TINYINT DEFAULT 1 COMMENT '交易方式：1-面交 2-邮寄 3-均可',
    `location` VARCHAR(100) DEFAULT NULL COMMENT '交易地点',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-上架 1-已售 2-下架 3-审核中 4-违规',
    `view_count` INT DEFAULT 0 COMMENT '浏览量',
    `favorite_count` INT DEFAULT 0 COMMENT '收藏数',
    `chat_count` INT DEFAULT 0 COMMENT '咨询数',
    `is_top` TINYINT DEFAULT 0 COMMENT '是否置顶：0-否 1-是',
    `is_recommend` TINYINT DEFAULT 0 COMMENT '是否推荐：0-否 1-是',
    `audit_status` TINYINT DEFAULT 0 COMMENT '审核状态：0-待审核 1-通过 2-拒绝',
    `audit_user_id` BIGINT DEFAULT NULL COMMENT '审核人ID',
    `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
    `audit_remark` VARCHAR(255) DEFAULT NULL COMMENT '审核备注',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_seller_id` (`seller_id`),
    KEY `idx_category_id` (`category_id`),
    KEY `idx_status` (`status`),
    KEY `idx_price` (`price`),
    KEY `idx_create_time` (`create_time`),
    KEY `idx_view_count` (`view_count`),
    FULLTEXT KEY `ft_title_description` (`title`, `description`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- 3. 商品图片表
CREATE TABLE IF NOT EXISTS `product_image` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '图片ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `image_url` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `is_cover` TINYINT DEFAULT 0 COMMENT '是否封面：0-否 1-是',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品图片表';

-- 4. 商品收藏表
CREATE TABLE IF NOT EXISTS `product_collection` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品收藏表';

-- 5. 商品标签表
CREATE TABLE IF NOT EXISTS `product_tag` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '标签ID',
    `name` VARCHAR(50) NOT NULL COMMENT '标签名称',
    `type` TINYINT DEFAULT 1 COMMENT '标签类型：1-系统标签 2-自定义标签',
    `use_count` INT DEFAULT 0 COMMENT '使用次数',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品标签表';

-- 6. 商品标签关联表
CREATE TABLE IF NOT EXISTS `product_tag_relation` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `tag_id` INT NOT NULL COMMENT '标签ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_product_tag` (`product_id`, `tag_id`),
    KEY `idx_tag_id` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品标签关联表';

-- =====================================================
-- 三、订单系统表
-- =====================================================

-- 1. 购物车表
CREATE TABLE IF NOT EXISTS `cart` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '购物车ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `quantity` INT DEFAULT 1 COMMENT '数量',
    `selected` TINYINT DEFAULT 1 COMMENT '是否选中：0-否 1-是',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车表';

-- 2. 订单表
CREATE TABLE IF NOT EXISTS `order_info` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `order_no` VARCHAR(64) NOT NULL COMMENT '订单编号',
    `buyer_id` BIGINT NOT NULL COMMENT '买家ID',
    `seller_id` BIGINT NOT NULL COMMENT '卖家ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `product_title` VARCHAR(100) DEFAULT NULL COMMENT '商品标题快照',
    `product_image` VARCHAR(255) DEFAULT NULL COMMENT '商品图片快照',
    `product_price` DECIMAL(10,2) DEFAULT NULL COMMENT '商品单价快照',
    `quantity` INT DEFAULT 1 COMMENT '购买数量',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    `pay_amount` DECIMAL(10,2) DEFAULT NULL COMMENT '实付金额',
    `freight_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '运费',
    `discount_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '优惠金额',
    `pay_type` TINYINT DEFAULT 0 COMMENT '支付方式：0-未支付 1-微信 2-支付宝 3-线下支付',
    `trade_type` TINYINT DEFAULT 1 COMMENT '交易方式：1-面交 2-邮寄',
    `status` TINYINT DEFAULT 0 COMMENT '订单状态：0-待付款 1-待发货 2-待收货 3-已完成 4-已取消 5-退款中 6-已退款',
    `receiver_name` VARCHAR(50) DEFAULT NULL COMMENT '收货人姓名',
    `receiver_phone` VARCHAR(20) DEFAULT NULL COMMENT '收货人电话',
    `receiver_address` VARCHAR(255) DEFAULT NULL COMMENT '收货地址',
    `pay_time` DATETIME DEFAULT NULL COMMENT '支付时间',
    `ship_time` DATETIME DEFAULT NULL COMMENT '发货时间',
    `finish_time` DATETIME DEFAULT NULL COMMENT '完成时间',
    `cancel_time` DATETIME DEFAULT NULL COMMENT '取消时间',
    `cancel_reason` VARCHAR(255) DEFAULT NULL COMMENT '取消原因',
    `remark` VARCHAR(255) DEFAULT NULL COMMENT '订单备注',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_buyer_id` (`buyer_id`),
    KEY `idx_seller_id` (`seller_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_status` (`status`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 3. 订单日志表
CREATE TABLE IF NOT EXISTS `order_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `order_id` BIGINT NOT NULL COMMENT '订单ID',
    `operator_id` BIGINT DEFAULT NULL COMMENT '操作人ID',
    `operator_type` TINYINT DEFAULT 0 COMMENT '操作人类型：0-系统 1-买家 2-卖家 3-管理员',
    `action` VARCHAR(50) NOT NULL COMMENT '操作动作',
    `content` VARCHAR(500) DEFAULT NULL COMMENT '操作内容',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单日志表';

-- 4. 退款表
CREATE TABLE IF NOT EXISTS `refund` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '退款ID',
    `refund_no` VARCHAR(64) NOT NULL COMMENT '退款编号',
    `order_id` BIGINT NOT NULL COMMENT '订单ID',
    `user_id` BIGINT NOT NULL COMMENT '申请人ID',
    `refund_amount` DECIMAL(10,2) NOT NULL COMMENT '退款金额',
    `refund_reason` VARCHAR(255) DEFAULT NULL COMMENT '退款原因',
    `refund_desc` TEXT COMMENT '退款说明',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-待处理 1-同意 2-拒绝 3-退款中 4-已完成',
    `audit_user_id` BIGINT DEFAULT NULL COMMENT '审核人ID',
    `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
    `audit_remark` VARCHAR(255) DEFAULT NULL COMMENT '审核备注',
    `refund_time` DATETIME DEFAULT NULL COMMENT '退款完成时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_refund_no` (`refund_no`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='退款表';

-- 5. 评价表
CREATE TABLE IF NOT EXISTS `review` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '评价ID',
    `order_id` BIGINT NOT NULL COMMENT '订单ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `user_id` BIGINT NOT NULL COMMENT '评价人ID',
    `to_user_id` BIGINT NOT NULL COMMENT '被评价人ID',
    `rating` TINYINT NOT NULL COMMENT '评分：1-5星',
    `content` TEXT COMMENT '评价内容',
    `images` JSON DEFAULT NULL COMMENT '评价图片',
    `type` TINYINT DEFAULT 1 COMMENT '评价类型：1-买家评价卖家 2-卖家评价买家',
    `is_anonymous` TINYINT DEFAULT 0 COMMENT '是否匿名：0-否 1-是',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-删除',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_user` (`order_id`, `user_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_to_user_id` (`to_user_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评价表';

-- =====================================================
-- 四、消息系统表
-- =====================================================

-- 1. 站内消息表
CREATE TABLE IF NOT EXISTS `message` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `user_id` BIGINT NOT NULL COMMENT '接收用户ID',
    `type` TINYINT NOT NULL COMMENT '消息类型：1-系统通知 2-订单消息 3-互动消息 4-活动消息',
    `title` VARCHAR(100) NOT NULL COMMENT '消息标题',
    `content` TEXT COMMENT '消息内容',
    `biz_type` VARCHAR(50) DEFAULT NULL COMMENT '业务类型',
    `biz_id` BIGINT DEFAULT NULL COMMENT '业务ID',
    `is_read` TINYINT DEFAULT 0 COMMENT '是否已读：0-否 1-是',
    `read_time` DATETIME DEFAULT NULL COMMENT '阅读时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_type` (`type`),
    KEY `idx_is_read` (`is_read`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站内消息表';

-- 2. 聊天会话表
CREATE TABLE IF NOT EXISTS `chat_session` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    `user_id1` BIGINT NOT NULL COMMENT '用户1ID',
    `user_id2` BIGINT NOT NULL COMMENT '用户2ID',
    `product_id` BIGINT DEFAULT NULL COMMENT '关联商品ID',
    `last_message` VARCHAR(500) DEFAULT NULL COMMENT '最后一条消息',
    `last_message_time` DATETIME DEFAULT NULL COMMENT '最后消息时间',
    `user1_unread` INT DEFAULT 0 COMMENT '用户1未读数',
    `user2_unread` INT DEFAULT 0 COMMENT '用户2未读数',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_product` (`user_id1`, `user_id2`, `product_id`),
    KEY `idx_user_id1` (`user_id1`),
    KEY `idx_user_id2` (`user_id2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天会话表';

-- 3. 聊天消息表
CREATE TABLE IF NOT EXISTS `chat_message` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `session_id` BIGINT NOT NULL COMMENT '会话ID',
    `from_user_id` BIGINT NOT NULL COMMENT '发送者ID',
    `to_user_id` BIGINT NOT NULL COMMENT '接收者ID',
    `msg_type` TINYINT DEFAULT 1 COMMENT '消息类型：1-文本 2-图片 3-语音 4-系统消息',
    `content` TEXT COMMENT '消息内容',
    `media_url` VARCHAR(255) DEFAULT NULL COMMENT '媒体文件URL',
    `duration` INT DEFAULT NULL COMMENT '语音时长（秒）',
    `is_read` TINYINT DEFAULT 0 COMMENT '是否已读：0-否 1-是',
    `read_time` DATETIME DEFAULT NULL COMMENT '阅读时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_session_id` (`session_id`),
    KEY `idx_from_user_id` (`from_user_id`),
    KEY `idx_to_user_id` (`to_user_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天消息表';

-- =====================================================
-- 五、管理系统表
-- =====================================================

-- 1. 管理员表
CREATE TABLE IF NOT EXISTS `admin` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '管理员ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码',
    `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像',
    `role_id` INT DEFAULT NULL COMMENT '角色ID',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-禁用',
    `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- 2. 角色表
CREATE TABLE IF NOT EXISTS `role` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `code` VARCHAR(50) NOT NULL COMMENT '角色编码',
    `description` VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-禁用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 3. 权限表
CREATE TABLE IF NOT EXISTS `permission` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '权限ID',
    `name` VARCHAR(50) NOT NULL COMMENT '权限名称',
    `code` VARCHAR(100) NOT NULL COMMENT '权限编码',
    `type` TINYINT DEFAULT 1 COMMENT '权限类型：1-菜单 2-按钮 3-接口',
    `parent_id` INT DEFAULT 0 COMMENT '父权限ID',
    `path` VARCHAR(255) DEFAULT NULL COMMENT '路由路径',
    `icon` VARCHAR(50) DEFAULT NULL COMMENT '图标',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 4. 角色权限关联表
CREATE TABLE IF NOT EXISTS `role_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `role_id` INT NOT NULL COMMENT '角色ID',
    `permission_id` INT NOT NULL COMMENT '权限ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_permission` (`role_id`, `permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- 5. 操作日志表
CREATE TABLE IF NOT EXISTS `operation_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '操作人ID',
    `username` VARCHAR(50) DEFAULT NULL COMMENT '操作人用户名',
    `module` VARCHAR(50) DEFAULT NULL COMMENT '操作模块',
    `operation` VARCHAR(100) DEFAULT NULL COMMENT '操作描述',
    `method` VARCHAR(10) DEFAULT NULL COMMENT '请求方法',
    `url` VARCHAR(255) DEFAULT NULL COMMENT '请求URL',
    `params` TEXT COMMENT '请求参数',
    `ip` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    `duration` INT DEFAULT NULL COMMENT '耗时（毫秒）',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-成功 1-失败',
    `error_msg` TEXT COMMENT '错误信息',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_module` (`module`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- =====================================================
-- 六、用户行为日志表（用于推荐系统）
-- =====================================================

CREATE TABLE IF NOT EXISTS `user_behavior` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` BIGINT DEFAULT 0 COMMENT '用户ID（未登录为0）',
    `session_id` VARCHAR(64) DEFAULT NULL COMMENT '会话ID',
    `behavior_type` VARCHAR(20) NOT NULL COMMENT '行为类型：view-浏览 click-点击 favorite-收藏 cart-加购 buy-购买',
    `product_id` BIGINT DEFAULT NULL COMMENT '商品ID',
    `category_id` INT DEFAULT NULL COMMENT '分类ID',
    `page_id` VARCHAR(50) DEFAULT NULL COMMENT '页面ID',
    `refer_page` VARCHAR(100) DEFAULT NULL COMMENT '来源页面',
    `device` VARCHAR(50) DEFAULT NULL COMMENT '设备类型',
    `ip` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    `stay_time` INT DEFAULT 0 COMMENT '停留时长（秒）',
    `event_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '事件时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_behavior_type` (`behavior_type`),
    KEY `idx_event_time` (`event_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为日志表';

-- =====================================================
-- 七、初始化数据
-- =====================================================

-- 初始化管理员账号（密码：admin123，已加密）
INSERT INTO `admin` (`username`, `password`, `nickname`, `role_id`, `status`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJn5fXQ5qUq', '超级管理员', 1, 0)
ON DUPLICATE KEY UPDATE `username` = VALUES(`username`);

-- 初始化角色
INSERT INTO `role` (`name`, `code`, `description`, `status`) VALUES
('超级管理员', 'super_admin', '拥有所有权限', 0),
('普通管理员', 'admin', '普通管理员权限', 0),
('运营人员', 'operator', '运营人员权限', 0)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- 初始化商品分类
INSERT INTO `product_category` (`name`, `parent_id`, `level`, `sort`, `status`) VALUES
('教材书籍', 0, 1, 1, 0),
('数码产品', 0, 1, 2, 0),
('生活用品', 0, 1, 3, 0),
('服饰鞋包', 0, 1, 4, 0),
('运动户外', 0, 1, 5, 0),
('美妆护肤', 0, 1, 6, 0),
('食品饮料', 0, 1, 7, 0),
('其他', 0, 1, 8, 0);

-- 二级分类
INSERT INTO `product_category` (`name`, `parent_id`, `level`, `sort`, `status`) VALUES
('专业教材', 1, 2, 1, 0),
('考研考公', 1, 2, 2, 0),
('课外读物', 1, 2, 3, 0),
('笔记本电脑', 2, 2, 1, 0),
('手机平板', 2, 2, 2, 0),
('耳机音响', 2, 2, 3, 0),
('数码配件', 2, 2, 4, 0),
('宿舍用品', 3, 2, 1, 0),
('洗漱用品', 3, 2, 2, 0),
('收纳整理', 3, 2, 3, 0);

-- =====================================================
-- 数据库初始化完成
-- =====================================================
