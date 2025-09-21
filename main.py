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
from src.util import setup_logging, get_logger


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
            await self._save_result(result, f"github_repos_{username}")
        else:
            self.logger.warning("未获取到仓库信息")
            
        return result
    
    async def crawl_github_profile(self, username: str) -> Optional[list]:
        """爬取GitHub用户资料"""
        self.logger.info(f"开始爬取用户 {username} 的资料信息")
        
        strategy = GitHubStrategy(self.crawler_service, model_type=ModelType.USER_PROFILE)
        result = await strategy.crawl_user_profile(username)
        
        if result:
            self.logger.info("成功获取用户资料信息")
            await self._save_result(result, f"github_profile_{username}")
        else:
            self.logger.warning("未获取到用户资料信息")
            
        return result
    
    async def crawl_custom_url(self, url: str, model_type: ModelType = ModelType.ACTIVITY) -> Optional[list]:
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
            await self._save_result(result, f"custom_{model_type}")
        else:
            self.logger.warning("未获取到数据")
            
        return result
    
    async def _save_result(self, result: list, filename: str) -> None:
        """保存结果到文件"""
        output_dir = Path(self.settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{filename}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f)
            self.logger.info(f"结果已保存到: {output_file}")
        except Exception as e:
            self.logger.error(f"保存结果失败: {str(e)}")


async def main():
    """主函数 - 复现原始demo的功能"""
    # 创建应用实例
    app = ETraceApp()
    
    result = await app.crawl_github_profile("Kritoooo")
    
    if result:
        print("提取的内容:")
        print(result)
    else:
        print("爬取失败")


if __name__ == "__main__":
    asyncio.run(main())