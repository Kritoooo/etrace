import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path


class LLMConfig(BaseModel):
    provider: str = Field(..., description="LLM提供商")
    api_token: str = Field(..., description="API密钥")
    base_url: str = Field(..., description="API基础URL")
    model_name: Optional[str] = Field(None, description="模型名称")


class CrawlerConfig(BaseModel):
    chunk_token_threshold: int = Field(default=8000, description="分块令牌阈值")
    apply_chunking: bool = Field(default=True, description="是否应用分块")
    input_format: str = Field(default="html", description="输入格式")
    verbose: bool = Field(default=True, description="是否详细输出")
    timeout: int = Field(default=30, description="超时时间(秒)")


class Settings(BaseModel):
    llm: LLMConfig
    crawler: CrawlerConfig
    output_dir: str = Field(default="output", description="输出目录")
    log_level: str = Field(default="INFO", description="日志级别")

    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量加载配置"""
        llm_config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai/deepseek-ai/DeepSeek-V3.1"),
            api_token=os.getenv("LLM_API_TOKEN", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
        )
        
        crawler_config = CrawlerConfig(
            chunk_token_threshold=int(os.getenv("CHUNK_TOKEN_THRESHOLD", "8000")),
            apply_chunking=os.getenv("APPLY_CHUNKING", "true").lower() == "true",
            verbose=os.getenv("VERBOSE", "true").lower() == "true"
        )
        
        return cls(
            llm=llm_config,
            crawler=crawler_config,
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )

    @classmethod
    def from_file(cls, config_path: str) -> "Settings":
        """从配置文件加载配置"""
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(**config_data)

    def to_file(self, config_path: str) -> None:
        """保存配置到文件"""
        import json
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)