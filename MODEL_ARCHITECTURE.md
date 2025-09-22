# ETrace 解耦架构说明

## 设计原则：职责分离

### 📋 Schema层 - 数据抽取专用
**职责**：定义从网页抽取什么数据，如何抽取
- 继承 `BaseExtractionSchema`
- 包含抽取指令（`get_extraction_instruction`）
- 字段定义针对网页抽取优化（如字符串类型）
- **不包含业务逻辑**

**示例**：
```python
class UserProfileExtractionSchema(BaseExtractionSchema):
    username: str = Field(..., description="用户名")
    followers: str = Field("0", description="关注者数量")  # 字符串便于抽取
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从GitHub用户页面抽取用户信息..."
```

### 🏢 Model层 - 业务逻辑专用
**职责**：业务数据模型，专注业务逻辑和验证
- 直接继承 `pydantic.BaseModel`
- 包含业务方法（计算、验证、格式化等）
- 字段类型针对业务需求（如整数、日期对象）
- **不包含抽取功能**

**示例**：
```python
class UserProfile(BaseModel):
    username: str
    stats: UserStats  # 嵌套业务对象
    
    def get_activity_level(self) -> str:  # 业务逻辑
        score = self.stats.influence_score()
        return "High" if score > 1000 else "Low"
```

### 🔄 转换层 - 数据映射
**职责**：将Schema抽取的数据转换为业务模型
- 位于 `GitHubStrategy._convert_to_models()`
- 处理字段映射和类型转换
- 创建嵌套业务对象

## 架构层次

```
┌─────────────────────┐
│   网页内容/API响应    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Schema层（抽取）    │  ← 专注抽取任务
│ - ExtractionSchema  │
│ - 抽取指令          │
│ - 字符串字段        │
└─────────┬───────────┘
          │
          ▼ 数据转换
┌─────────────────────┐
│  Model层（业务）     │  ← 专注业务逻辑  
│ - BusinessModel     │
│ - 业务方法          │
│ - 类型化字段        │
└─────────────────────┘
```

## 模型分类

### Schema模型（src/model/github/extraction.py）
- `UserProfileExtractionSchema` - 用户资料抽取
- `RepositoryExtractionSchema` - 仓库抽取
- 继承 `BaseExtractionSchema`，具有抽取指令

### 业务模型（src/model/github/）
- `UserProfile` - 用户业务模型
- `Repository` - 仓库业务模型
- `Event` - 事件模型（API直接映射）
- 直接继承 `pydantic.BaseModel`，专注业务逻辑

### 子模型
- `UserSocialLinks`, `UserStats` - 业务子对象
- `EventActor`, `EventRepo` - API子对象

## 数据流

```
网页 → Schema抽取 → 原始字典 → 转换器 → 业务模型实例
API → Event.from_api_response() → Event实例
```

## 优势

1. **职责清晰**：Schema只管抽取，Model只管业务
2. **独立演化**：抽取需求变化不影响业务模型
3. **类型安全**：业务模型使用合适的数据类型
4. **易于测试**：各层可独立测试
5. **易于维护**：降低耦合度