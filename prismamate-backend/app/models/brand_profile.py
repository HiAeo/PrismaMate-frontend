"""
PrismaMate 棱镜 - 品牌档案数据模型

用户的企业信息管理中心，是所有检测报告的数据底座。
MVP阶段使用 JSON 文件持久化存储。
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field, asdict


# JSON 持久化文件路径
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
_BRAND_PROFILES_FILE = os.path.join(_DATA_DIR, "brand_profiles.json")


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _load_profiles_from_file() -> dict:
    """从 JSON 文件加载品牌档案"""
    if not os.path.exists(_BRAND_PROFILES_FILE):
        return {}
    try:
        with open(_BRAND_PROFILES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = {}
        for pid, pdict in data.items():
            profiles[int(pid)] = BrandProfile.from_dict(pdict)
        return profiles
    except Exception:
        return {}


def _save_profiles_to_file(profiles: dict):
    """保存品牌档案到 JSON 文件"""
    _ensure_data_dir()
    data = {str(pid): p.to_dict() for pid, p in profiles.items()}
    with open(_BRAND_PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_counter_from_file() -> int:
    """从 JSON 文件加载计数器"""
    if not os.path.exists(_BRAND_PROFILES_FILE):
        return 0
    try:
        with open(_BRAND_PROFILES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return 0
        return max(int(k) for k in data.keys())
    except Exception:
        return 0


@dataclass
class BrandProfile:
    """品牌档案数据类"""
    id: int
    user_id: str  # 用户ID（字符串，与认证系统一致）
    
    # 必填字段
    company_name: str
    brand_names: List[str]
    website: str
    products: str
    
    # 选填字段
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "brand_names": self.brand_names or [],
            "website": self.website,
            "products": self.products,
            "description": self.description,
            "keywords": self.keywords or [],
            "competitors": self.competitors or [],
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BrandProfile":
        """从字典创建"""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()
            
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.utcnow()
            
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            company_name=data["company_name"],
            brand_names=data.get("brand_names", []),
            website=data["website"],
            products=data["products"],
            description=data.get("description"),
            keywords=data.get("keywords", []),
            competitors=data.get("competitors", []),
            created_at=created_at,
            updated_at=updated_at,
        )


# JSON 文件持久化存储 - MVP阶段使用
_brand_profiles: dict[int, BrandProfile] = _load_profiles_from_file()
_brand_profile_counter: int = _load_counter_from_file()


def get_next_profile_id() -> int:
    """获取下一个档案ID"""
    global _brand_profile_counter
    _brand_profile_counter += 1
    return _brand_profile_counter


class BrandProfileStore:
    """品牌档案 JSON 文件持久化存储"""
    
    @classmethod
    def create(cls, user_id: str, data: dict) -> BrandProfile:
        """创建品牌档案"""
        global _brand_profiles
        
        profile_id = get_next_profile_id()
        profile = BrandProfile(
            id=profile_id,
            user_id=user_id,
            company_name=data["company_name"],
            brand_names=data.get("brand_names", []),
            website=data["website"],
            products=data["products"],
            description=data.get("description"),
            keywords=data.get("keywords", []),
            competitors=data.get("competitors", []),
        )
        _brand_profiles[profile_id] = profile
        _save_profiles_to_file(_brand_profiles)
        return profile
    
    @classmethod
    def get_by_id(cls, profile_id: int) -> Optional[BrandProfile]:
        """根据ID获取档案"""
        # 先从内存读取，如果文件有更新则重新加载
        global _brand_profiles
        _brand_profiles = _load_profiles_from_file()
        return _brand_profiles.get(profile_id)
    
    @classmethod
    def get_by_user(cls, user_id: str) -> List[BrandProfile]:
        """获取用户的所有档案"""
        global _brand_profiles
        _brand_profiles = _load_profiles_from_file()
        return [p for p in _brand_profiles.values() if p.user_id == user_id]
    
    @classmethod
    def update(cls, profile_id: int, data: dict) -> Optional[BrandProfile]:
        """更新档案"""
        global _brand_profiles
        _brand_profiles = _load_profiles_from_file()
        
        profile = _brand_profiles.get(profile_id)
        if not profile:
            return None
        
        # 更新字段
        if "company_name" in data:
            profile.company_name = data["company_name"]
        if "brand_names" in data:
            profile.brand_names = data["brand_names"]
        if "website" in data:
            profile.website = data["website"]
        if "products" in data:
            profile.products = data["products"]
        if "description" in data:
            profile.description = data["description"]
        if "keywords" in data:
            profile.keywords = data["keywords"]
        if "competitors" in data:
            profile.competitors = data["competitors"]
        
        profile.updated_at = datetime.utcnow()
        _brand_profiles[profile_id] = profile
        _save_profiles_to_file(_brand_profiles)
        return profile
    
    @classmethod
    def delete(cls, profile_id: int) -> bool:
        """删除档案"""
        global _brand_profiles
        _brand_profiles = _load_profiles_from_file()
        
        if profile_id in _brand_profiles:
            del _brand_profiles[profile_id]
            _save_profiles_to_file(_brand_profiles)
            return True
        return False


# 导出
__all__ = ["BrandProfile", "BrandProfileStore"]
