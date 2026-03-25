"""地图服务提供商抽象基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.schemas import Location, POIInfo, WeatherInfo

class MapServiceProvider(ABC):
    """地图服务提供商抽象基类,定义统一的地图服务接口"""

    @abstractmethod
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """搜索POI"""
        pass

    @abstractmethod
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """查询天气"""
        pass

    @abstractmethod
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """规划路线"""
        pass

    @abstractmethod
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """地理编码(地址转坐标)"""
        pass

    @abstractmethod
    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """获取POI详情"""
        pass
