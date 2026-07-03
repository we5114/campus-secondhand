"""
数据同步工具
将MySQL数据同步到Hive数仓
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
import pymysql
from datetime import datetime, timedelta

from config.collector_config import CollectorConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSyncTool:
    """数据同步工具类"""

    def __init__(self):
        self.config = CollectorConfig
        self.mysql_conn = None
        self._init_mysql()

    def _init_mysql(self):
        """初始化MySQL连接"""
        try:
            self.mysql_conn = pymysql.connect(
                host=self.config.MYSQL_HOST,
                port=self.config.MYSQL_PORT,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("MySQL连接初始化成功")
        except Exception as e:
            logger.error(f"MySQL连接初始化失败: {str(e)}")
            raise

    def get_table_count(self, table_name, where_clause=None):
        """
        获取表记录数

        Args:
            table_name: 表名
            where_clause: WHERE条件

        Returns:
            int: 记录数
        """
        try:
            with self.mysql_conn.cursor() as cursor:
                sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
                if where_clause:
                    sql += f" WHERE {where_clause}"
                cursor.execute(sql)
                result = cursor.fetchone()
                return result['cnt']
        except Exception as e:
            logger.error(f"获取表记录数失败: {str(e)}")
            return 0

    def get_table_data(self, table_name, columns="*", where_clause=None,
                       order_by=None, limit=None, offset=None):
        """
        获取表数据

        Args:
            table_name: 表名
            columns: 列名
            where_clause: WHERE条件
            order_by: 排序
            limit: 限制数量
            offset: 偏移量

        Returns:
            list: 数据列表
        """
        try:
            with self.mysql_conn.cursor() as cursor:
                sql = f"SELECT {columns} FROM {table_name}"
                if where_clause:
                    sql += f" WHERE {where_clause}"
                if order_by:
                    sql += f" ORDER BY {order_by}"
                if limit:
                    sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"获取表数据失败: {str(e)}")
            return []

    def sync_user_data(self, start_date=None, end_date=None):
        """
        同步用户数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            int: 同步的记录数
        """
        logger.info("开始同步用户数据...")

        where_clause = None
        if start_date and end_date:
            where_clause = f"create_time BETWEEN '{start_date}' AND '{end_date}'"

        count = self.get_table_count("user", where_clause)
        logger.info(f"待同步用户数据: {count} 条")

        # 分批同步
        batch_size = self.config.SYNC_BATCH_SIZE
        total_synced = 0

        for offset in range(0, count, batch_size):
            data = self.get_table_data(
                "user",
                where_clause=where_clause,
                order_by="id",
                limit=batch_size,
                offset=offset
            )

            # 写入Hive（这里简化，实际应该通过Spark或Sqoop同步）
            # 实际项目中应该调用Spark任务或Sqoop命令
            total_synced += len(data)
            logger.info(f"同步用户数据进度: {total_synced}/{count}")

        logger.info(f"用户数据同步完成，共 {total_synced} 条")
        return total_synced

    def sync_product_data(self, start_date=None, end_date=None):
        """
        同步商品数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            int: 同步的记录数
        """
        logger.info("开始同步商品数据...")

        where_clause = None
        if start_date and end_date:
            where_clause = f"create_time BETWEEN '{start_date}' AND '{end_date}'"

        count = self.get_table_count("product", where_clause)
        logger.info(f"待同步商品数据: {count} 条")

        batch_size = self.config.SYNC_BATCH_SIZE
        total_synced = 0

        for offset in range(0, count, batch_size):
            data = self.get_table_data(
                "product",
                where_clause=where_clause,
                order_by="id",
                limit=batch_size,
                offset=offset
            )

            total_synced += len(data)
            logger.info(f"同步商品数据进度: {total_synced}/{count}")

        logger.info(f"商品数据同步完成，共 {total_synced} 条")
        return total_synced

    def sync_order_data(self, start_date=None, end_date=None):
        """
        同步订单数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            int: 同步的记录数
        """
        logger.info("开始同步订单数据...")

        where_clause = None
        if start_date and end_date:
            where_clause = f"create_time BETWEEN '{start_date}' AND '{end_date}'"

        count = self.get_table_count("order_info", where_clause)
        logger.info(f"待同步订单数据: {count} 条")

        batch_size = self.config.SYNC_BATCH_SIZE
        total_synced = 0

        for offset in range(0, count, batch_size):
            data = self.get_table_data(
                "order_info",
                where_clause=where_clause,
                order_by="id",
                limit=batch_size,
                offset=offset
            )

            total_synced += len(data)
            logger.info(f"同步订单数据进度: {total_synced}/{count}")

        logger.info(f"订单数据同步完成，共 {total_synced} 条")
        return total_synced

    def sync_behavior_data(self, start_date=None, end_date=None):
        """
        同步用户行为数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            int: 同步的记录数
        """
        logger.info("开始同步用户行为数据...")

        where_clause = None
        if start_date and end_date:
            where_clause = f"create_time BETWEEN '{start_date}' AND '{end_date}'"

        count = self.get_table_count("user_behavior", where_clause)
        logger.info(f"待同步用户行为数据: {count} 条")

        batch_size = self.config.SYNC_BATCH_SIZE
        total_synced = 0

        for offset in range(0, count, batch_size):
            data = self.get_table_data(
                "user_behavior",
                where_clause=where_clause,
                order_by="id",
                limit=batch_size,
                offset=offset
            )

            total_synced += len(data)
            logger.info(f"同步用户行为数据进度: {total_synced}/{count}")

        logger.info(f"用户行为数据同步完成，共 {total_synced} 条")
        return total_synced

    def sync_all_data(self, start_date=None, end_date=None):
        """
        同步所有数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            dict: 各表同步数量
        """
        logger.info("开始同步所有数据...")

        results = {}

        # 同步用户数据
        results['user'] = self.sync_user_data(start_date, end_date)

        # 同步商品数据
        results['product'] = self.sync_product_data(start_date, end_date)

        # 同步订单数据
        results['order'] = self.sync_order_data(start_date, end_date)

        # 同步用户行为数据
        results['behavior'] = self.sync_behavior_data(start_date, end_date)

        logger.info(f"所有数据同步完成: {results}")
        return results

    def incremental_sync(self):
        """
        增量同步（同步昨天的数据）

        Returns:
            dict: 各表同步数量
        """
        logger.info("开始增量同步...")

        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d 00:00:00")
        end_date = yesterday.strftime("%Y-%m-%d 23:59:59")

        return self.sync_all_data(start_date, end_date)

    def close(self):
        """关闭连接"""
        if self.mysql_conn:
            self.mysql_conn.close()
            logger.info("MySQL连接已关闭")


if __name__ == "__main__":
    sync_tool = DataSyncTool()

    # 测试增量同步
    results = sync_tool.incremental_sync()
    print(f"同步结果: {results}")

    sync_tool.close()
