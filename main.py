#!/usr/bin/env python3
"""
ETrace 主应用入口
"""

import asyncio
from pathlib import Path
from typing import Optional

from src.config import Settings
from src.service import CrawlerService
from src.strategy import GitHubStrategy
from src.model.github import ModelType
from src.util import setup_logging, get_logger, DataSerializer


class ETraceApp:
    """ETrace应用主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path and Path(config_path).exists():
            self.settings = Settings.from_file(config_path)
        else:
            self.settings = Settings.from_env()
        
        setup_logging(
            level=self.settings.log_level,
            log_file=f"{self.settings.output_dir}/etrace.log"
        )
        self.logger = get_logger(__name__)
        
        self.crawler_service = CrawlerService(self.settings)
    
    async def crawl_github_profile(self, username: str) -> Optional[list]:
        """爬取GitHub用户资料"""
        self.logger.info(f"开始爬取用户 {username} 的资料信息")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.USER_PROFILE, use_simple_schema=False)
        result = await strategy.crawl_user_profile(username)
        
        if result:
            self.logger.info("成功获取用户资料信息")
            # 转换为可序列化的格式
            serialized_result = DataSerializer.serialize_for_json(result)
            await self._save_result(serialized_result, f"github_profile_{username}")
        else:
            self.logger.warning("未获取到用户资料信息")
            
        return result
    
    async def get_github_events(self, username: str, event_type: str = "public", per_page: int = 30) -> Optional[list]:
        """通过 API 获取 GitHub 用户事件"""
        self.logger.info(f"开始获取用户 {username} 的 {event_type} 事件")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.EVENT)
        result = await strategy.get_user_events_via_api(username, event_type=event_type, per_page=per_page)
        
        if result:
            self.logger.info(f"成功获取 {len(result)} 个事件")
            # 使用序列化工具转换为可保存的格式
            events_data = DataSerializer.convert_pydantic_list_to_dict_list(result)
            await self._save_result(events_data, f"github_events_{username}_{event_type}")
            return events_data
        else:
            self.logger.warning("未获取到事件数据")
            return None
    
    async def get_github_repositories(self, username: str, per_page: int = 30, page: int = 1) -> Optional[list]:
        """通过 API 获取 GitHub 用户仓库列表"""
        self.logger.info(f"开始获取用户 {username} 的仓库列表")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.REPOSITORY)
        result = await strategy.get_user_repositories_via_api(username, per_page=per_page, page=page)
        
        if result:
            self.logger.info(f"成功获取 {len(result)} 个仓库")
            # 使用序列化工具转换为可保存的格式
            repos_data = DataSerializer.convert_pydantic_list_to_dict_list(result)
            await self._save_result(repos_data, f"github_repositories_{username}")
            return repos_data
        else:
            self.logger.warning("未获取到仓库数据")
            return None
    
    async def get_github_repository_details(self, owner: str, repo: str) -> Optional[dict]:
        """通过 API 获取 GitHub 仓库详细信息"""
        self.logger.info(f"开始获取仓库 {owner}/{repo} 的详细信息")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.REPOSITORY)
        result = await strategy.get_repository_details_via_api(owner, repo)
        
        if result:
            self.logger.info(f"成功获取仓库详细信息: {owner}/{repo}")
            # 使用序列化工具转换为可保存的格式
            repo_data = DataSerializer.convert_pydantic_to_dict(result)
            await self._save_result([repo_data], f"github_repository_{owner}_{repo}")
            return repo_data
        else:
            self.logger.warning("未获取到仓库详细信息")
            return None
    
    async def _save_result(self, result: list, filename: str) -> None:
        """保存结果到文件"""
        output_dir = Path(self.settings.output_dir)
        output_file = output_dir / f"{filename}.json"
        
        if DataSerializer.save_to_json(result, output_file):
            self.logger.info(f"结果已保存到: {output_file}")
        else:
            self.logger.error(f"保存结果失败: {output_file}")


async def main():
    """主函数 - 演示 GitHub API 事件获取功能"""
    # 创建应用实例
    app = ETraceApp()
    
    result = await app.get_github_repository_details("Kritoooo", "dify")
    
    if result:
        print("提取的内容:")
        print(result)
    else:
        print("爬取失败")


    # # 演示获取用户事件
    # print("=== 获取 GitHub 用户事件 ===")
    # events = await app.get_github_events("Kritoooo", event_type="public", per_page=10)
    
    # if events:
    #     print(f"成功获取到 {len(events)} 个事件:")
    #     for i, event in enumerate(events[:3], 1):  # 只显示前3个事件
    #         print(f"{i}. {event.get('type', 'Unknown')} - {event.get('repo', {}).get('name', 'Unknown')} - {event.get('created_at', 'Unknown')}")
    # else:
    #     print("未获取到用户事件")
    
    # # 演示获取仓库事件（可选）
    # print("\n=== 获取仓库事件 ===")
    # repo_events = await app.get_repository_events("torvalds", "linux", per_page=5)
    
    # if repo_events:
    #     print(f"成功获取到 {len(repo_events)} 个仓库事件:")
    #     for i, event in enumerate(repo_events[:2], 1):  # 只显示前2个事件
    #         print(f"{i}. {event.get('type', 'Unknown')} - {event.get('actor', {}).get('login', 'Unknown')} - {event.get('created_at', 'Unknown')}")
    # else:
    #     print("未获取到仓库事件")


if __name__ == "__main__":
    asyncio.run(main())