#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from contextlib import asynccontextmanager

from src.config import Settings
from src.service import CrawlerService
from src.strategy import GitHubStrategy
from src.model.github import ModelType
from src.util import setup_logging, get_logger, DataSerializer


class GitHubUserRequest(BaseModel):
    username: str


class APIResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    message: str = ""
    count: int = 0


app_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global app_instance
    from main import ETraceApp
    app_instance = ETraceApp()
    yield


app = FastAPI(
    title="ETrace API",
    description="GitHub 数据抽取 API 服务",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "ETrace API 服务正在运行", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/github/profile", response_model=APIResponse)
async def get_github_profile(request: GitHubUserRequest):
    try:
        result = await app_instance.crawl_github_profile(request.username)
        
        if result:
            serialized_data = DataSerializer.serialize_for_json(result)
            return APIResponse(
                success=True,
                data=serialized_data,
                message=f"成功获取用户 {request.username} 的资料",
                count=len(serialized_data)
            )
        else:
            return APIResponse(
                success=False,
                message=f"未能获取用户 {request.username} 的资料"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/github/repositories", response_model=APIResponse)
async def get_github_repositories(request: GitHubUserRequest):
    try:
        result = await app_instance.crawl_github_repositories(request.username)
        
        if result:
            serialized_data = DataSerializer.serialize_for_json(result)
            return APIResponse(
                success=True,
                data=serialized_data,
                message=f"成功获取用户 {request.username} 的仓库",
                count=len(serialized_data)
            )
        else:
            return APIResponse(
                success=False,
                message=f"未能获取用户 {request.username} 的仓库"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github/events/{username}")
async def get_github_events(
    username: str,
    event_type: str = "public",
    per_page: int = 30
):
    try:
        result = await app_instance.get_github_events(
            username, 
            event_type=event_type, 
            per_page=per_page
        )
        
        if result:
            return APIResponse(
                success=True,
                data=result,
                message=f"成功获取用户 {username} 的事件",
                count=len(result)
            )
        else:
            return APIResponse(
                success=False,
                message=f"未能获取用户 {username} 的事件"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github/repo-events/{owner}/{repo}")
async def get_repository_events(
    owner: str,
    repo: str,
    per_page: int = 30
):
    try:
        result = await app_instance.get_repository_events(
            owner, 
            repo, 
            per_page=per_page
        )
        
        if result:
            return APIResponse(
                success=True,
                data=result,
                message=f"成功获取仓库 {owner}/{repo} 的事件",
                count=len(result)
            )
        else:
            return APIResponse(
                success=False,
                message=f"未能获取仓库 {owner}/{repo} 的事件"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)