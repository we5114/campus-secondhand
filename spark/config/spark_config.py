"""
Spark配置文件
"""
import os


class SparkConfig:
    """Spark配置类"""

    # Spark应用名称
    APP_NAME = "CampusSecondhand"

    # Spark Master
    MASTER = os.environ.get("SPARK_MASTER", "local[*]")

    # Hive配置
    HIVE_METASTORE_URIS = os.environ.get("HIVE_METASTORE_URIS", "thrift://localhost:9083")
    HIVE_WAREHOUSE_DIR = os.environ.get("HIVE_WAREHOUSE_DIR", "/user/hive/warehouse")

    # 数据库配置
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "campus_secondhand")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")

    # Redis配置
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))

    # 数据路径
    DATA_PATH = os.environ.get("DATA_PATH", "/data/campus-secondhand")

    # 推荐系统配置
    RECOMMEND_CONFIG = {
        "user_cf_neighbors": 50,  # UserCF邻居数
        "item_cf_neighbors": 50,  # ItemCF邻居数
        "recommend_count": 100,  # 推荐数量
        "hot_recommend_count": 50,  # 热门推荐数量
        "new_recommend_count": 30,  # 新品推荐数量
    }

    # 任务调度配置
    SCHEDULE_CONFIG = {
        "etl_cron": "0 1 * * *",  # ETL任务每天凌晨1点执行
        "recommend_cron": "0 2 * * *",  # 推荐任务每天凌晨2点执行
        "profile_cron": "0 3 * * *",  # 画像任务每天凌晨3点执行
        "report_cron": "0 4 * * *",  # 报表任务每天凌晨4点执行
    }

    @classmethod
    def get_mysql_url(cls):
        """获取MySQL连接URL"""
        return f"jdbc:mysql://{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}?useUnicode=true&characterEncoding=utf8&useSSL=false"

    @classmethod
    def get_mysql_properties(cls):
        """获取MySQL连接属性"""
        return {
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "driver": "com.mysql.cj.jdbc.Driver"
        }
