import motor.motor_asyncio
from typing import Optional

class DatabaseManager:
    #_前缀表示为内部属性，但是是约定的内部属性
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    _database = None
    
    #用来实现设计模式的方法，在创建过程中调用，先于init
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    #用来设置相关参数的初始化
    def __init__(self):
        if self._client is None:
            self.MONGO_DETAILS = "mongodb://localhost:27017"
            self._client = motor.motor_asyncio.AsyncIOMotorClient(self.MONGO_DETAILS)
            self._database = self._client.pachong
    
    #修改参数类型为只读不改
    @property
    def database(self):
        return self._database
    
    @property
    def client(self):
        return self._client
    
    async def close_connection(self):
        if self._client:
            self._client.close()

# 全局数据库管理器实例
db_manager = DatabaseManager()