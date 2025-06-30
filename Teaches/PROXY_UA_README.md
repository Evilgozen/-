# 代理IP池和User-Agent轮换功能

这个项目为Scrapy爬虫添加了简单的代理IP池和User-Agent轮换功能，包含基础版本和基于KDL API的高级版本，适合学习使用。

## 功能特性

- **基础代理IP池**: 静态代理列表的随机轮换
- **KDL动态代理池**: 基于KDL API的动态代理获取和刷新
- **User-Agent轮换**: 随机轮换使用不同的浏览器User-Agent
- **代理认证支持**: 支持用户名密码认证和白名单认证
- **自动刷新**: 定期自动刷新代理IP池
- **简单配置**: 朴素的实现，易于理解和修改
- **日志记录**: 记录使用的代理和User-Agent信息

## 文件说明

### middlewares.py
包含三个主要的中间件类：

1. **ProxyMiddleware**: 基础代理IP池中间件
   - 使用静态代理列表
   - 随机选择代理IP
   - 处理代理失败情况
   - 记录代理使用日志

2. **KDLProxyMiddleware**: KDL高级代理中间件（推荐）
   - 基于KDL API动态获取代理
   - 支持用户名密码认证和白名单认证
   - 自动处理代理格式
   - 更稳定的代理服务

3. **UserAgentMiddleware**: User-Agent轮换中间件
   - 随机选择User-Agent
   - 包含多种浏览器的User-Agent
   - 记录使用的User-Agent

### proxy_extension.py
代理扩展模块：

1. **ProxyPool**: 代理池管理类
   - 动态获取代理列表
   - 代理列表刷新功能
   - 异常处理和备用代理

2. **ProxyExtension**: 代理扩展类
   - 定期刷新代理池
   - 与Scrapy引擎同步启动和关闭
   - 多线程代理刷新

### settings.py
配置文件中启用了中间件和扩展：
```python
# 中间件配置
DOWNLOADER_MIDDLEWARES = {
    # 基础代理中间件（简单版本）
    # "Teaches.middlewares.ProxyMiddleware": 350,
    
    # KDL高级代理中间件（推荐使用）
    "Teaches.middlewares.KDLProxyMiddleware": 350,
    
    "Teaches.middlewares.UserAgentMiddleware": 400,
    "Teaches.middlewares.TeachesDownloaderMiddleware": 543,
}

# 扩展配置
EXTENSIONS = {
    "Teaches.proxy_extension.ProxyExtension": 300,
}

# 代理池配置
PROXY_REFRESH_INTERVAL = 60  # 代理刷新间隔（秒）
```

## 使用方法

### 方式一：使用KDL动态代理（推荐）

#### 1. 配置KDL API

在 `proxy_extension.py` 中修改API配置：

```python
# 替换为你的KDL API信息
API_URL = 'https://dps.kdlapi.com/api/getdps/?secret_id=your_secret_id&signature=your_signature&num=10&format=json&sep=1'
```

#### 2. 配置代理认证

在 `middlewares.py` 的 `KDLProxyMiddleware` 类中配置：

```python
# 代理认证信息
self.username = "your_username"  # 你的KDL用户名
self.password = "your_password"  # 你的KDL密码

# 认证方式选择
self.use_auth = True   # 用户名密码认证（私密代理/独享代理）
# self.use_auth = False  # 白名单认证（私密代理/独享代理）
```

### 方式二：使用基础静态代理

#### 1. 配置静态代理IP池

在 `middlewares.py` 的 `ProxyMiddleware` 类中修改 `proxy_list`：

```python
self.proxy_list = [
    'http://your-proxy1.com:8080',
    'http://your-proxy2.com:8080',
    'http://127.0.0.1:7890',  # 本地代理
    # 添加更多有效的代理IP
]
```

#### 2. 切换到基础代理中间件

在 `settings.py` 中注释KDL中间件，启用基础中间件：

```python
DOWNLOADER_MIDDLEWARES = {
    "Teaches.middlewares.ProxyMiddleware": 350,  # 启用基础代理
    # "Teaches.middlewares.KDLProxyMiddleware": 350,  # 注释KDL代理
    "Teaches.middlewares.UserAgentMiddleware": 400,
}
```

### 通用配置

#### 1. 自定义User-Agent

在 `middlewares.py` 的 `UserAgentMiddleware` 类中修改 `user_agent_list`：

```python
self.user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    # 添加更多User-Agent
]
```

#### 2. 调整代理刷新间隔

在 `settings.py` 中修改：

```python
PROXY_REFRESH_INTERVAL = 60  # 代理刷新间隔（秒），可根据需要调整
```

### 运行和测试

#### 1. 运行爬虫

正常运行你的Scrapy爬虫，中间件会自动工作：

```bash
# 运行现有的爬虫
scrapy crawl encu

# 或者运行测试爬虫
python proxy_ua_example.py
```

#### 2. 测试基础功能

使用提供的测试脚本验证功能：

```bash
python proxy_ua_example.py
```

#### 3. 测试KDL功能

运行KDL测试脚本：

```bash
python kdl_test.py
```

这个脚本会访问 httpbin.org 来显示当前使用的IP和User-Agent。

## 注意事项

### KDL代理使用注意事项

1. **API配置**: 确保KDL API的secret_id和signature正确
2. **认证信息**: 根据你的KDL套餐类型选择正确的认证方式
3. **代理数量**: 根据需要调整API请求的代理数量（num参数）
4. **刷新频率**: 合理设置代理刷新间隔，避免频繁请求API
5. **网络连接**: 确保能正常访问KDL API接口

### 通用注意事项

1. **代理IP有效性**: 示例中的代理IP仅为演示，请替换为有效的代理地址
2. **代理认证**: 如果代理需要用户名密码，格式为：`http://username:password@proxy.com:8080`
3. **HTTPS代理**: 对于HTTPS网站，使用 `https://` 前缀的代理
4. **代理失效处理**: 当前实现较简单，可以根据需要添加更复杂的失效处理逻辑
5. **成本控制**: 使用付费代理服务时注意成本控制

## 扩展功能

### 已实现的高级功能

- ✅ KDL动态代理池
- ✅ 自动代理刷新
- ✅ 多种认证方式支持
- ✅ 代理失败处理
- ✅ 详细日志记录

### 可进一步扩展的功能

- 代理IP健康检查和评分
- 多个代理服务商支持
- 更复杂的User-Agent轮换策略
- 代理使用统计和分析
- 地理位置相关的代理选择
- 代理池负载均衡

## 日志查看

运行爬虫时，你会看到类似的日志输出：

```
2024-01-01 10:00:00 [Teaches.middlewares] INFO: 使用代理: http://127.0.0.1:7890
2024-01-01 10:00:00 [Teaches.middlewares] INFO: 使用User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit...
```

这样你就可以监控代理和User-Agent的使用情况。

## 学习建议

1. 先理解中间件的工作原理
2. 尝试修改代理池和User-Agent列表
3. 观察日志输出，了解轮换效果
4. 根据实际需求调整和优化代码

这个实现保持了简单性，非常适合学习Scrapy中间件的工作机制和代理使用方法。