"""
数据转换器 - 将抽取Schema数据转换为业务模型
职责：处理Schema抽取数据到业务模型的映射转换
"""
from typing import Dict, Any, List
from datetime import datetime
from .enums import ModelType


class DataConverter:
    """数据转换器基类"""
    
    @staticmethod
    def convert_extraction_to_domain(data: Dict[str, Any], model_type: ModelType) -> Dict[str, Any]:
        """将抽取数据转换为领域模型数据格式"""
        if model_type == ModelType.USER_PROFILE:
            return UserProfileConverter.convert(data)
        elif model_type == ModelType.EVENT:
            return EventConverter.convert(data)
        else:
            return data


class UserProfileConverter:
    """用户资料数据转换器"""
    
    @staticmethod
    def convert(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换用户资料数据"""
        # 确保必要字段存在
        username = data.get('username', '')
        if not username:
            username = data.get('login', data.get('name', 'unknown'))
        
        return {
            'id': username,
            'username': username,
            'name': data.get('display_name', ''),
            'bio': data.get('bio', ''),
            'avatar_url': data.get('avatar_url') or None,
            'gravatar_id': '',
            'location': data.get('location', ''),
            'company': data.get('company', ''),
            'hireable': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'type': data.get('account_type', 'User'),
            'site_admin': False,
            # 嵌套对象 - 使用字典，Pydantic会自动转换
            'social_links': {
                'website': data.get('website'),
                'twitter': data.get('twitter'),
                'email': data.get('email')
            },
            'stats': {
                'followers': int(data.get('followers', '0') or '0'),
                'following': int(data.get('following', '0') or '0'),
                'public_repos': int(data.get('public_repos', '0') or '0'),
                'public_gists': int(data.get('public_gists', '0') or '0'),
                'collaborators': 0
            },
            'html_url': f"https://github.com/{username}",
            'organizations': []  # 空列表，后续可以填充
        }




class EventConverter:
    """事件数据转换器"""
    
    @staticmethod
    def convert(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换事件数据 - 创建兼容GitHub API格式的数据结构"""
        return {
            'id': str(hash(f"{data.get('type', 'unknown')}_{data.get('timestamp', '')}")),
            'type': f"{data.get('type', 'Unknown')}Event",
            'actor': {
                'id': hash(data.get('actor_username', 'unknown')),
                'login': data.get('actor_username', ''),
                'avatar_url': data.get('actor_avatar', ''),
                'url': f"https://github.com/{data.get('actor_username', '')}"
            },
            'repo': {
                'id': hash(data.get('repository_name', 'unknown')),
                'name': data.get('repository_name', ''),
                'url': data.get('repository_url', '')
            },
            'payload': {
                'action': data.get('action_description', ''),
                'size': int(data.get('commit_count', '0') or '0'),
                'ref': data.get('branch_name', '')
            },
            'public': True,
            'created_at': data.get('timestamp', datetime.now().isoformat())
        }


class SchemaToModelConverter:
    """Schema到Model的批量转换器"""
    
    def __init__(self, model_type: ModelType):
        self.model_type = model_type
    
    def convert_batch(self, extracted_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量转换数据"""
        converted_data = []
        
        for data in extracted_data:
            try:
                converted = DataConverter.convert_extraction_to_domain(data, self.model_type)
                converted_data.append(converted)
            except Exception as e:
                print(f"转换数据失败: {e}, 数据: {data}")
                continue
                
        return converted_data