"""高德地图服务实现"""

import json
import re
from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo
from .map_service_provider import MapServiceProvider
from loguru import logger

# 全局MCP工具实例
_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    """获取高德地图MCP工具实例(单例模式)"""
    global _amap_mcp_tool
    
    if _amap_mcp_tool is None:
        settings = get_settings()
        
        if not settings.vite_amap_web_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置VITE_AMAP_WEB_KEY")
        
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务,支持POI搜索、路线规划、天气查询等功能",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.vite_amap_web_key},
            auto_expand=True
        )
        logger.info(f"✅ 高德地图MCP工具初始化成功")
    
    return _amap_mcp_tool


class AmapService(MapServiceProvider):
    """高德地图服务实现类"""
    
    def __init__(self):
        """初始化服务"""
        self.mcp_tool = get_amap_mcp_tool()
    
    def _parse_location(self, loc_str: str) -> Location:
        """解析 '经度,纬度' 格式的坐标字符串"""
        try:
            lon, lat = map(float, loc_str.split(","))
            return Location(longitude=lon, latitude=lat)
        except (ValueError, AttributeError):
            return Location(longitude=0.0, latitude=0.0)

    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """搜索POI"""
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_text_search",
                "arguments": {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": str(citylimit).lower()
                }
            })
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                return []
            data = json.loads(json_match.group())
            return [
                POIInfo(
                    id=poi.get("id", ""),
                    name=poi.get("name", ""),
                    type=poi.get("type", ""),
                    address=poi.get("address", ""),
                    location=self._parse_location(poi.get("location", "0,0")),
                    tel=poi.get("tel") or None,
                )
                for poi in data.get("pois", [])
            ]
        except Exception as e:
            logger.error(f"❌ POI搜索失败: {str(e)}")
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        """查询天气"""
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": city
                }
            })
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                return []
            data = json.loads(json_match.group())

            # 优先使用预报数据（forecasts），包含多天信息
            forecasts = data.get("forecasts", [])
            if forecasts:
                casts = forecasts[0].get("casts", [])
                return [
                    WeatherInfo(
                        date=cast.get("date", ""),
                        day_weather=cast.get("dayweather", ""),
                        night_weather=cast.get("nightweather", ""),
                        day_temp=cast.get("daytemp", 0),
                        night_temp=cast.get("nighttemp", 0),
                        wind_direction=cast.get("daywind", ""),
                        wind_power=cast.get("daypower", ""),
                    )
                    for cast in casts
                ]

            # 降级使用实时天气（lives）
            lives = data.get("lives", [])
            if lives:
                from datetime import date as date_cls
                live = lives[0]
                return [WeatherInfo(
                    date=date_cls.today().isoformat(),
                    day_weather=live.get("weather", ""),
                    night_weather=live.get("weather", ""),
                    day_temp=live.get("temperature", 0),
                    night_temp=live.get("temperature", 0),
                    wind_direction=live.get("winddirection", ""),
                    wind_power=live.get("windpower", ""),
                )]

            return []
        except Exception as e:
            logger.error(f"❌ 天气查询失败: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """规划路线"""
        try:
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }
            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")
            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address
            }
            if origin_city: arguments["origin_city"] = origin_city
            if destination_city: arguments["destination_city"] = destination_city
            
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments
            })
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw": result}
        except Exception as e:
            logger.error(f"❌ 路线规划失败: {str(e)}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """地理编码"""
        try:
            arguments = {"address": address}
            if city: arguments["city"] = city
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_geo",
                "arguments": arguments
            })
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                return None
            data = json.loads(json_match.group())
            geocodes = data.get("geocodes", [])
            if geocodes:
                loc_str = geocodes[0].get("location", "")
                if loc_str:
                    return self._parse_location(loc_str)
            return None
        except Exception as e:
            logger.error(f"❌ 地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """获取POI详情"""
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_search_detail",
                "arguments": {"id": poi_id}
            })
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw": result}
        except Exception as e:
            logger.error(f"❌ 获取POI详情失败: {str(e)}")
            return {}
