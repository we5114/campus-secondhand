"""
校园二手交易智能分析与推荐平台 - 主入口文件
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config.settings import settings
from app.config.constants import ErrorCode, ERROR_MESSAGES
from app.utils.redis import init_redis, close_redis

# 导入路由
from app.api.v1.user import router as user_router
from app.api.v1.product import router as product_router
from app.api.v1.order import router as order_router
from app.api.v1.recommend import router as recommend_router
from app.api.v1.chat import router as chat_router
from app.api.v1.llm import router as llm_router
from app.api.v1.admin import router as admin_router


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="校园二手交易智能分析与推荐平台API文档",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(user_router, prefix="/api/v1/user", tags=["用户模块"])
    app.include_router(product_router, prefix="/api/v1/product", tags=["商品模块"])
    app.include_router(order_router, prefix="/api/v1/order", tags=["订单模块"])
    app.include_router(recommend_router, prefix="/api/v1/recommend", tags=["推荐模块"])
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["消息聊天模块"])
    app.include_router(llm_router, prefix="/api/v1/llm", tags=["大模型模块"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["管理后台"])

    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时执行"""
        # 初始化Redis
        await init_redis()
        print(f"✅ {settings.APP_NAME} 启动成功")
        print(f"📚 API文档: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")

    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时执行"""
        await close_redis()
        print(f"👋 {settings.APP_NAME} 已关闭")

    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        # 让 FastAPI 自带的 HTTPException 正常返回（401、403 等）
        from fastapi import HTTPException
        if isinstance(exc, HTTPException):
            raise exc

        print(f"❌ 系统异常: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.SYSTEM_ERROR,
                "message": ERROR_MESSAGES.get(ErrorCode.SYSTEM_ERROR, "系统错误"),
                "data": None,
                "timestamp": int(time.time())
            }
        )

    # 健康检查接口
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查"""
        return {
            "code": 0,
            "message": "success",
            "data": {
                "status": "ok",
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION
            },
            "timestamp": int(time.time())
        }

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
