"""POI相关API路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services import get_map_service
from ...services.unsplash_service import get_unsplash_service
from ...config import get_settings

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详细信息,包括图片"
)
async def get_poi_detail(poi_id: str):
    """
    获取POI详情
    
    Args:
        poi_id: POI ID
        
    Returns:
        POI详情响应
    """
    try:
        service = get_map_service()
        
        # 调用地图POI详情API
        result = service.get_poi_detail(poi_id)
        
        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data=result
        )
        
    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}"
        )


@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI"
)
async def search_poi(keywords: str, city: str = "北京"):
    """
    搜索POI

    Args:
        keywords: 搜索关键词
        city: 城市名称

    Returns:
        搜索结果
    """
    try:
        service = get_map_service()
        result = service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "搜索成功",
            "data": result
        }

    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}"
        )


@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从Unsplash获取图片"
)
async def get_attraction_photo(name: str, city: Optional[str] = None):
    """
    获取景点图片

    Args:
        name: 景点名称
        city: 所在城市(用于提升搜索准确率)

    Returns:
        图片URL
    """
    try:
        unsplash_service = get_unsplash_service()
        settings = get_settings()
        
        # 判断目的地是否在国内 (简单判断)
        is_international = settings.map_provider == "google"
        
        photo_url = None
        
        if is_international:
            # Google 模式下直接用英文名称搜索效果更好 (假設 name 已經由 Agent 翻譯或本身是英文)
            # 嘗試 1: 原名 + 城市
            query = f"{name} {city}" if city else name
            photo_url = unsplash_service.get_photo_url(query)
        else:
            # 高德模式下保持拼音邏輯
            import pypinyin
            pinyin_list = pypinyin.pinyin(name, style=pypinyin.Style.NORMAL)
            pinyin_name = "".join([p[0] for p in pinyin_list])
            query_attraction = f"{pinyin_name} China"
            photo_url = unsplash_service.get_photo_url(query_attraction)

        if not photo_url:
            # 备用方案
            fallback_query = f"{city} travel" if city else "travel landmark"
            photo_url = unsplash_service.get_photo_url(fallback_query, randomize=True)
            
        if not photo_url:
            # 最终兜底
            photo_url = unsplash_service.get_photo_url("beautiful landscape", randomize=True)

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url
            }
        }

    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}"
        )

