"""
PrismaMate 棱镜 - 数据库模型

MVP模式下，SQLAlchemy模型暂不可用。
使用内存存储替代。
"""

# MVP模式：延迟导入，避免 Base = None 导致的问题
# 如需使用数据库模型，请设置 MVP_MODE = False 并配置数据库

# 品牌档案使用内存存储
from app.models.brand_profile import BrandProfile, BrandProfileStore

__all__ = [
    "BrandProfile",
    "BrandProfileStore",
]
