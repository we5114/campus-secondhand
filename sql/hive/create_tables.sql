-- =====================================================
-- 校园二手交易智能分析与推荐平台 - Hive数仓建表脚本
-- 数仓分层：ODS -> DWD -> DWS -> ADS
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS campus_trade_dw COMMENT '校园二手交易数据仓库';

USE campus_trade_dw;

-- =====================================================
-- 一、ODS层（操作数据层）
-- =====================================================

-- 1. ODS用户信息表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_user_info (
    user_id BIGINT COMMENT '用户ID',
    username STRING COMMENT '用户名',
    phone STRING COMMENT '手机号（脱敏）',
    email STRING COMMENT '邮箱',
    gender INT COMMENT '性别：0未知 1男 2女',
    grade STRING COMMENT '年级',
    major STRING COMMENT '专业',
    campus STRING COMMENT '校区',
    status INT COMMENT '状态：0正常 1禁用',
    user_level INT COMMENT '用户等级',
    is_real_name INT COMMENT '是否实名认证',
    create_time STRING COMMENT '创建时间',
    update_time STRING COMMENT '更新时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_user_info'
TBLPROPERTIES ('comment'='ODS层用户信息表');

-- 2. ODS商品信息表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_product_info (
    product_id BIGINT COMMENT '商品ID',
    seller_id BIGINT COMMENT '卖家ID',
    category_id INT COMMENT '分类ID',
    title STRING COMMENT '商品标题',
    description STRING COMMENT '商品描述',
    price DECIMAL(10,2) COMMENT '售价',
    original_price DECIMAL(10,2) COMMENT '原价',
    `condition` INT COMMENT '成色：1全新 2九成新 3八成新 4七成新 5其他',
    status INT COMMENT '状态：0上架 1已售 2下架 3审核中',
    view_count INT COMMENT '浏览量',
    favorite_count INT COMMENT '收藏数',
    chat_count INT COMMENT '咨询数',
    create_time STRING COMMENT '创建时间',
    update_time STRING COMMENT '更新时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_product_info'
TBLPROPERTIES ('comment'='ODS层商品信息表');

-- 3. ODS订单信息表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_order_info (
    order_id BIGINT COMMENT '订单ID',
    order_no STRING COMMENT '订单编号',
    buyer_id BIGINT COMMENT '买家ID',
    seller_id BIGINT COMMENT '卖家ID',
    product_id BIGINT COMMENT '商品ID',
    product_title STRING COMMENT '商品标题快照',
    total_amount DECIMAL(10,2) COMMENT '订单总金额',
    pay_amount DECIMAL(10,2) COMMENT '实付金额',
    pay_type INT COMMENT '支付方式',
    status INT COMMENT '订单状态',
    quantity INT COMMENT '购买数量',
    create_time STRING COMMENT '创建时间',
    pay_time STRING COMMENT '支付时间',
    finish_time STRING COMMENT '完成时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_order_info'
TBLPROPERTIES ('comment'='ODS层订单信息表');

-- 4. ODS用户行为日志表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_user_behavior_log (
    log_id STRING COMMENT '日志ID',
    user_id BIGINT COMMENT '用户ID（未登录为0）',
    session_id STRING COMMENT '会话ID',
    behavior_type STRING COMMENT '行为类型：view/click/favorite/cart/buy',
    product_id BIGINT COMMENT '商品ID',
    category_id INT COMMENT '分类ID',
    page_id STRING COMMENT '页面ID',
    refer_page STRING COMMENT '来源页面',
    device STRING COMMENT '设备类型',
    ip STRING COMMENT 'IP地址',
    stay_time INT COMMENT '停留时长（秒）',
    event_time STRING COMMENT '事件时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_user_behavior_log'
TBLPROPERTIES ('comment'='ODS层用户行为日志表');

-- 5. ODS商品分类表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_product_category (
    category_id INT COMMENT '分类ID',
    name STRING COMMENT '分类名称',
    parent_id INT COMMENT '父分类ID',
    level INT COMMENT '分类层级',
    sort INT COMMENT '排序',
    status INT COMMENT '状态',
    create_time STRING COMMENT '创建时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_product_category'
TBLPROPERTIES ('comment'='ODS层商品分类表');

-- 6. ODS评价表
CREATE EXTERNAL TABLE IF NOT EXISTS ods_review (
    review_id BIGINT COMMENT '评价ID',
    order_id BIGINT COMMENT '订单ID',
    product_id BIGINT COMMENT '商品ID',
    user_id BIGINT COMMENT '评价人ID',
    to_user_id BIGINT COMMENT '被评价人ID',
    rating INT COMMENT '评分：1-5星',
    content STRING COMMENT '评价内容',
    type INT COMMENT '评价类型',
    create_time STRING COMMENT '创建时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/campus_trade_dw.db/ods_review'
TBLPROPERTIES ('comment'='ODS层评价表');

-- =====================================================
-- 二、DWD层（明细数据层）
-- =====================================================

-- 1. DWD用户明细宽表
CREATE TABLE IF NOT EXISTS dwd_user_detail (
    user_id BIGINT COMMENT '用户ID',
    user_name STRING COMMENT '用户名',
    gender INT COMMENT '性别',
    grade STRING COMMENT '年级',
    major STRING COMMENT '专业',
    campus STRING COMMENT '校区',
    register_date STRING COMMENT '注册日期',
    register_days INT COMMENT '注册天数',
    is_real_name INT COMMENT '是否实名认证',
    user_level INT COMMENT '用户等级',
    status INT COMMENT '状态'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWD层用户明细宽表');

-- 2. DWD商品明细宽表
CREATE TABLE IF NOT EXISTS dwd_product_detail (
    product_id BIGINT COMMENT '商品ID',
    seller_id BIGINT COMMENT '卖家ID',
    category_id INT COMMENT '一级分类ID',
    category_name STRING COMMENT '一级分类名称',
    sub_category_id INT COMMENT '二级分类ID',
    sub_category_name STRING COMMENT '二级分类名称',
    title STRING COMMENT '标题',
    price DECIMAL(10,2) COMMENT '售价',
    original_price DECIMAL(10,2) COMMENT '原价',
    discount_rate DECIMAL(5,2) COMMENT '折扣率',
    price_range STRING COMMENT '价格区间',
    `condition` INT COMMENT '成色',
    condition_name STRING COMMENT '成色名称',
    view_count INT COMMENT '浏览量',
    favorite_count INT COMMENT '收藏数',
    status INT COMMENT '状态',
    publish_date STRING COMMENT '发布日期'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWD层商品明细宽表');

-- 3. DWD订单明细宽表
CREATE TABLE IF NOT EXISTS dwd_order_detail (
    order_id BIGINT COMMENT '订单ID',
    order_no STRING COMMENT '订单编号',
    buyer_id BIGINT COMMENT '买家ID',
    seller_id BIGINT COMMENT '卖家ID',
    product_id BIGINT COMMENT '商品ID',
    category_id INT COMMENT '分类ID',
    total_amount DECIMAL(10,2) COMMENT '订单金额',
    pay_amount DECIMAL(10,2) COMMENT '实付金额',
    pay_type INT COMMENT '支付方式',
    status INT COMMENT '订单状态',
    create_date STRING COMMENT '下单日期',
    create_hour INT COMMENT '下单小时',
    pay_date STRING COMMENT '支付日期',
    pay_interval_min INT COMMENT '支付间隔（分钟）',
    finish_date STRING COMMENT '完成日期'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWD层订单明细宽表');

-- 4. DWD用户行为明细
CREATE TABLE IF NOT EXISTS dwd_user_behavior_detail (
    log_id STRING COMMENT '日志ID',
    user_id BIGINT COMMENT '用户ID',
    session_id STRING COMMENT '会话ID',
    behavior_type STRING COMMENT '行为类型',
    behavior_weight INT COMMENT '行为权重',
    product_id BIGINT COMMENT '商品ID',
    category_id INT COMMENT '分类ID',
    page_id STRING COMMENT '页面',
    device STRING COMMENT '设备',
    event_date STRING COMMENT '事件日期',
    event_hour INT COMMENT '事件小时',
    event_time STRING COMMENT '事件时间',
    is_login INT COMMENT '是否登录用户'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWD层用户行为明细');

-- =====================================================
-- 三、DWS层（数据服务层）
-- =====================================================

-- 1. DWS用户日统计宽表
CREATE TABLE IF NOT EXISTS dws_user_stat_daily (
    user_id BIGINT COMMENT '用户ID',
    stat_date STRING COMMENT '统计日期',
    login_count INT COMMENT '登录次数',
    view_count INT COMMENT '浏览商品数',
    click_count INT COMMENT '点击次数',
    favorite_count INT COMMENT '收藏数',
    cart_count INT COMMENT '加购数',
    buy_count INT COMMENT '购买数',
    publish_count INT COMMENT '发布商品数',
    sold_count INT COMMENT '卖出商品数',
    total_pay_amount DECIMAL(10,2) COMMENT '消费总金额',
    total_income_amount DECIMAL(10,2) COMMENT '收入总金额',
    avg_stay_time DECIMAL(10,2) COMMENT '平均停留时长',
    active_session_count INT COMMENT '活跃会话数'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWS层用户日统计宽表');

-- 2. DWS商品日统计宽表
CREATE TABLE IF NOT EXISTS dws_product_stat_daily (
    product_id BIGINT COMMENT '商品ID',
    stat_date STRING COMMENT '统计日期',
    view_count INT COMMENT '浏览量',
    view_user_count INT COMMENT '浏览用户数',
    click_count INT COMMENT '点击量',
    favorite_count INT COMMENT '收藏数',
    favorite_user_count INT COMMENT '收藏用户数',
    cart_count INT COMMENT '加购数',
    order_count INT COMMENT '下单数',
    order_user_count INT COMMENT '下单用户数',
    conversion_rate DECIMAL(5,4) COMMENT '转化率',
    avg_stay_time DECIMAL(10,2) COMMENT '平均停留时长'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWS层商品日统计宽表');

-- 3. DWS品类日统计宽表
CREATE TABLE IF NOT EXISTS dws_category_stat_daily (
    category_id INT COMMENT '分类ID',
    category_name STRING COMMENT '分类名称',
    stat_date STRING COMMENT '统计日期',
    product_count INT COMMENT '商品数量',
    new_product_count INT COMMENT '新增商品数',
    view_count BIGINT COMMENT '浏览量',
    order_count INT COMMENT '订单数',
    gmv DECIMAL(12,2) COMMENT '成交总额',
    avg_price DECIMAL(10,2) COMMENT '平均成交价',
    seller_count INT COMMENT '卖家数',
    buyer_count INT COMMENT '买家数'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWS层品类日统计宽表');

-- 4. DWS交易日统计宽表
CREATE TABLE IF NOT EXISTS dws_trade_stat_daily (
    stat_date STRING COMMENT '统计日期',
    order_count INT COMMENT '订单总数',
    order_user_count INT COMMENT '下单用户数',
    gmv DECIMAL(12,2) COMMENT '成交总额',
    pay_order_count INT COMMENT '支付订单数',
    pay_amount DECIMAL(12,2) COMMENT '支付总额',
    pay_rate DECIMAL(5,4) COMMENT '支付转化率',
    avg_order_amount DECIMAL(10,2) COMMENT '客单价',
    finish_order_count INT COMMENT '完成订单数',
    refund_order_count INT COMMENT '退款订单数',
    refund_rate DECIMAL(5,4) COMMENT '退款率'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='DWS层交易日统计宽表');

-- =====================================================
-- 四、ADS层（应用数据层）
-- =====================================================

-- 1. ADS用户商品评分矩阵（用于推荐）
CREATE TABLE IF NOT EXISTS ads_user_product_score (
    user_id BIGINT COMMENT '用户ID',
    product_id BIGINT COMMENT '商品ID',
    score DECIMAL(5,2) COMMENT '综合评分',
    view_score DECIMAL(5,2) COMMENT '浏览得分',
    click_score DECIMAL(5,2) COMMENT '点击得分',
    favorite_score DECIMAL(5,2) COMMENT '收藏得分',
    cart_score DECIMAL(5,2) COMMENT '加购得分',
    buy_score DECIMAL(5,2) COMMENT '购买得分'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='ADS层用户商品评分矩阵');

-- 2. ADS用户画像宽表
CREATE TABLE IF NOT EXISTS ads_user_profile (
    user_id BIGINT COMMENT '用户ID',
    basic_tags MAP<STRING, STRING> COMMENT '基础标签',
    behavior_tags MAP<STRING, STRING> COMMENT '行为标签',
    preference_tags MAP<STRING, STRING> COMMENT '偏好标签',
    value_tags MAP<STRING, STRING> COMMENT '价值标签',
    rfm_score STRUCT<r_score:INT, f_score:INT, m_score:INT, total_score:INT> COMMENT 'RFM评分',
    lifecycle_stage STRING COMMENT '生命周期阶段',
    update_time STRING COMMENT '更新时间'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='ADS层用户画像宽表');

-- 3. ADS销售报表宽表
CREATE TABLE IF NOT EXISTS ads_sales_report (
    stat_date STRING COMMENT '统计日期',
    stat_type STRING COMMENT '统计粒度：day/week/month',
    category_id INT COMMENT '分类ID（-1表示全部）',
    campus STRING COMMENT '校区（all表示全部）',
    order_count INT COMMENT '订单数',
    user_count INT COMMENT '用户数',
    gmv DECIMAL(12,2) COMMENT 'GMV',
    avg_order_amount DECIMAL(10,2) COMMENT '客单价'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='ADS层销售报表宽表');

-- 4. ADS热门商品榜
CREATE TABLE IF NOT EXISTS ads_hot_product_rank (
    rank_type STRING COMMENT '榜单类型：view/favorite/sale/gmv',
    product_id BIGINT COMMENT '商品ID',
    product_title STRING COMMENT '商品标题',
    category_id INT COMMENT '分类ID',
    category_name STRING COMMENT '分类名称',
    seller_id BIGINT COMMENT '卖家ID',
    score DECIMAL(10,2) COMMENT '榜单分数',
    rank INT COMMENT '排名',
    stat_date STRING COMMENT '统计日期'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='ADS层热门商品榜');

-- 5. ADS用户留存分析表
CREATE TABLE IF NOT EXISTS ads_user_retention (
    stat_date STRING COMMENT '统计日期',
    register_date STRING COMMENT '注册日期',
    new_user_count INT COMMENT '新增用户数',
    day1_retention DECIMAL(5,4) COMMENT '次日留存率',
    day7_retention DECIMAL(5,4) COMMENT '7日留存率',
    day30_retention DECIMAL(5,4) COMMENT '30日留存率'
)
PARTITIONED BY (dt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY', 'comment'='ADS层用户留存分析表');

-- =====================================================
-- 数仓建表完成
-- =====================================================
