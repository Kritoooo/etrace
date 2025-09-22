#!/usr/bin/env python3
"""
ETrace 主应用入口
"""

import asyncio
import json
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
        # 加载配置
        if config_path and Path(config_path).exists():
            self.settings = Settings.from_file(config_path)
        else:
            self.settings = Settings.from_env()
        
        # 设置日志
        setup_logging(
            level=self.settings.log_level,
            log_file=f"{self.settings.output_dir}/etrace.log"
        )
        self.logger = get_logger(__name__)
        
        # 初始化服务
        self.crawler_service = CrawlerService(self.settings)
        
    async def crawl_github_repositories(self, username: str) -> Optional[list]:
        """爬取GitHub用户的仓库信息"""
        self.logger.info(f"开始爬取用户 {username} 的仓库信息")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.REPOSITORY)
        result = await strategy.crawl_user_repositories(username)
        
        if result:
            self.logger.info(f"成功获取 {len(result)} 条仓库信息")
            # 转换为可序列化的格式
            serialized_result = DataSerializer.serialize_for_json(result)
            await self._save_result(serialized_result, f"github_repos_{username}")
        else:
            self.logger.warning("未获取到仓库信息")
            
        return result
    
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
    
    async def crawl_custom_url(self, url: str, model_type: ModelType = ModelType.EVENT) -> Optional[list]:
        """爬取自定义URL"""
        self.logger.info(f"开始爬取URL: {url}")
        
        if "github.com" in url:
            strategy = GitHubStrategy(self.crawler_service, model_type=model_type)
            result = await strategy.execute(url)
        else:
            self.logger.error("目前只支持GitHub URL")
            return None
        
        if result:
            self.logger.info(f"成功获取 {len(result)} 条数据")
            # 转换为可序列化的格式
            serialized_result = DataSerializer.serialize_for_json(result)
            await self._save_result(serialized_result, f"custom_{model_type}")
        else:
            self.logger.warning("未获取到数据")
            
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
    
    async def get_repository_events(self, owner: str, repo: str, per_page: int = 30) -> Optional[list]:
        """通过 API 获取 GitHub 仓库事件"""
        self.logger.info(f"开始获取仓库 {owner}/{repo} 的事件")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.EVENT)
        result = await strategy.get_repository_events_via_api(owner, repo, per_page=per_page)
        
        if result:
            self.logger.info(f"成功获取 {len(result)} 个事件")
            # 使用序列化工具转换为可保存的格式
            events_data = DataSerializer.convert_pydantic_list_to_dict_list(result)
            await self._save_result(events_data, f"repo_events_{owner}_{repo}")
            return events_data
        else:
            self.logger.warning("未获取到事件数据")
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
    
    result = await app.crawl_github_profile("Kritoooo")
    
    if result:
        print("提取的内容:")
        print(result)
    else:
        print("爬取失败")


    # 演示获取用户事件
    print("=== 获取 GitHub 用户事件 ===")
    events = await app.get_github_events("Kritoooo", event_type="public", per_page=10)
    
    if events:
        print(f"成功获取到 {len(events)} 个事件:")
        for i, event in enumerate(events[:3], 1):  # 只显示前3个事件
            print(f"{i}. {event.get('type', 'Unknown')} - {event.get('repo', {}).get('name', 'Unknown')} - {event.get('created_at', 'Unknown')}")
    else:
        print("未获取到用户事件")
    
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