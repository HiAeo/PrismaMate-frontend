"""
PrismaMate 棱镜 - 品牌智库 API

提供品牌档案的 CRUD 功能。
MVP阶段使用内存存储。
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.api.v1.auth import get_current_user
from app.models.brand_profile import BrandProfile, BrandProfileStore

router = APIRouter(tags=["品牌智库"])


def _get_user_id(current_user) -> str:
    """安全获取用户ID，兼容对象和字典"""
    if hasattr(current_user, "user_id"):
        return current_user.user_id
    return current_user.get("user_id", "")


# ==================== 请求/响应模型 ====================

class BrandProfileCreate(BaseModel):
    """创建品牌档案请求"""
    company_name: str = Field(..., min_length=1, max_length=255, description="公司名称")
    brand_names: List[str] = Field(..., min_length=1, description="品牌名称列表")
    website: str = Field(..., min_length=1, max_length=512, description="官方网址")
    products: str = Field(..., min_length=1, description="主营产品或服务")
    description: Optional[str] = Field(None, max_length=1000, description="企业简介")
    keywords: List[str] = Field(..., min_length=1, description="核心语义词")
    competitors: Optional[List[str]] = Field(default_factory=list, description="主要竞品")


class BrandProfileUpdate(BaseModel):
    """更新品牌档案请求"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_names: Optional[List[str]] = None
    website: Optional[str] = Field(None, min_length=1, max_length=512)
    products: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    keywords: Optional[List[str]] = None
    competitors: Optional[List[str]] = None


class BrandProfileResponse(BaseModel):
    """品牌档案响应"""
    id: int
    user_id: str
    company_name: str
    brand_names: List[str]
    website: str
    products: str
    description: Optional[str]
    keywords: List[str]
    competitors: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]


# ==================== API 端点 ====================

@router.post("", response_model=BrandProfileResponse, summary="创建品牌档案")
async def create_brand_profile(
    profile: BrandProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建新的品牌档案"""
    profile_data = profile.model_dump()
    new_profile = BrandProfileStore.create(
        user_id=_get_user_id(current_user),
        data=profile_data
    )
    return new_profile.to_dict()


@router.get("", response_model=List[BrandProfileResponse], summary="获取品牌档案列表")
async def list_brand_profiles(
    current_user: dict = Depends(get_current_user)
):
    """获取当前用户的所有品牌档案"""
    profiles = BrandProfileStore.get_by_user(_get_user_id(current_user))
    # 按更新时间倒序
    profiles.sort(key=lambda p: p.updated_at, reverse=True)
    return [p.to_dict() for p in profiles]


@router.get("/{profile_id}", response_model=BrandProfileResponse, summary="获取品牌档案详情")
async def get_brand_profile(
    profile_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取单个品牌档案详情"""
    profile = BrandProfileStore.get_by_id(profile_id)
    
    if not profile or profile.user_id != _get_user_id(current_user):
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    
    return profile.to_dict()


@router.put("/{profile_id}", response_model=BrandProfileResponse, summary="更新品牌档案")
async def update_brand_profile(
    profile_id: int,
    profile: BrandProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新品牌档案"""
    # 验证所有权
    existing = BrandProfileStore.get_by_id(profile_id)
    if not existing or existing.user_id != _get_user_id(current_user):
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    
    update_data = profile.model_dump(exclude_unset=True)
    updated = BrandProfileStore.update(profile_id, update_data)
    
    return updated.to_dict()


@router.delete("/{profile_id}", summary="删除品牌档案")
async def delete_brand_profile(
    profile_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除品牌档案"""
    # 验证所有权
    existing = BrandProfileStore.get_by_id(profile_id)
    if not existing or existing.user_id != _get_user_id(current_user):
        raise HTTPException(status_code=404, detail="品牌档案不存在")
    
    BrandProfileStore.delete(profile_id)
    return {"message": "品牌档案已删除"}
