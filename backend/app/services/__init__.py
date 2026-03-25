"""地图服务统一导出"""

from .map_service_provider import MapServiceProvider
from .amap_service import AmapService
from .google_maps_service import GoogleMapsService
from ..config import get_settings

_map_service = None

def get_map_service() -> MapServiceProvider:
    """获取当前配置的地图服务实例(单例)"""
    global _map_service
    
    if _map_service is None:
        settings = get_settings()
        if settings.map_provider == "google":
            _map_service = GoogleMapsService()
            print("🗺️  使用 Google Maps 服務")
        else:
            _map_service = AmapService()
            print("🗺️  使用 高德地圖 服務")
            
    return _map_service
