"""Google Maps 服务实现"""

import googlemaps
import json
from typing import List, Dict, Any, Optional
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo
from .map_service_provider import MapServiceProvider
from ..utils.coords import wgs84_to_gcj02

class GoogleMapsService(MapServiceProvider):
    """Google Maps 服务实现类"""
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.api_key = settings.google_maps_api_key
        if not self.api_key:
            print("⚠️  警告: Google Maps API Key未配置,请在.env中设置GOOGLE_MAPS_API_KEY")
            self.client = None
        else:
            try:
                self.client = googlemaps.Client(key=self.api_key)
                print("✅ Google Maps 客户端初始化成功")
            except Exception as e:
                print(f"❌ Google Maps 客户端初始化失败: {e}")
                self.client = None
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """搜索POI并转换为POIInfo列表"""
        if not self.client:
            return []
            
        print(f"🌐 [Google Maps] 搜索POI: {keywords} in {city}")
        try:
            # 使用 Places API 搜索
            query = f"{keywords} in {city}"
            places_result = self.client.places(query=query)
            
            pois = []
            for place in places_result.get('results', []):
                loc = place.get('geometry', {}).get('location', {})
                lng = loc.get('lng', 0)
                lat = loc.get('lat', 0)
                
                # 如果是中国境内且需要兼容高德，可以转换
                # 但本项目前端已做适配，Google 模式下使用原生 WGS84
                
                poi = POIInfo(
                    id=place.get('place_id', ''),
                    name=place.get('name', ''),
                    type=place.get('types', [''])[0],
                    address=place.get('formatted_address', ''),
                    location=Location(
                        longitude=lng,
                        latitude=lat
                    ),
                    tel="", 
                    distance=0
                )
                pois.append(poi)
            return pois
        except Exception as e:
            print(f"❌ Google Maps POI搜索异常: {e}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """查询天气 (Google Maps 不支持, 降级使用高德)"""
        print(f"🌐 [Google Maps] 查询天气: {city} (尝试高德降级)")
        try:
            from .amap_service import AmapService
            amap = AmapService()
            return amap.get_weather(city)
        except Exception as e:
            print(f"❌ 天气服务降级失败: {e}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """使用 Directions API 规划路线"""
        if not self.client:
            return {}
            
        print(f"🌐 [Google Maps] 规划路线: {origin_address} -> {destination_address}")
        try:
            mode = "walking" if route_type == "walking" else "driving"
            directions_result = self.client.directions(
                origin_address,
                destination_address,
                mode=mode
            )
            return directions_result
        except Exception as e:
            print(f"❌ Google Maps 路线规划异常: {e}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """使用 Geocoding API 进行地理编码"""
        if not self.client:
            return None
            
        print(f"🌐 [Google Maps] 地理编码: {address}")
        try:
            geocode_result = self.client.geocode(address)
            if geocode_result:
                loc = geocode_result[0].get('geometry', {}).get('location', {})
                return Location(
                    longitude=loc.get('lng', 0),
                    latitude=loc.get('lat', 0)
                )
            return None
        except Exception as e:
            print(f"❌ Google Maps 地理编码异常: {e}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """获取 POI 详情"""
        if not self.client:
            return {}
            
        print(f"🌐 [Google Maps] 获取POI详情: {poi_id}")
        try:
            place_detail = self.client.place(place_id=poi_id)
            return place_detail.get('result', {})
        except Exception as e:
            print(f"❌ Google Maps 获取详情异常: {e}")
            return {}
