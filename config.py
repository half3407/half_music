from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT相关配置
    JWT_TOKEN_EXPIRE_TIME: int = 7200  # token有效时间，单位为秒，当前为默认2小时
    JWT_SECRET: str = "7m#L9v@Qx2pKf$Rn8sW4eY6!zA1hC5tG"  # 加解密密钥
    JWT_ALGORITHM: str = "HS256"  # 加解密算法

    # 日志相关配置
    MUSIC_LOG_FILE_PATH: str = "logs/half_music.log"  # 日志文件路径
    MUSIC_LOG_FILE_LEVEL: str = "INFO"  # 默认日志文件输出的日志等级
    MUSIC_LOG_CONSOLE_LEVEL: str = "INFO"  # 默认控制台输出的日志等级
    MUSIC_LOG_ROTATION_SIZE: str = "5 MB"  # 轮转大小
    MUSIC_LOG_RETENTION_DAYS: str = "5"  # 保留天数

    # 分页相关配置
    page_default: int = 1 # 默认页码
    page_size_default: int = 12 # 默认每页数量
    page_size_max: int = 100 # 每页最大数量
    page_size_min: int = 1 # 每页最小数量

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False # 环境变量不区分大小写
        extra = "allow" # 允许额外的环境变量，不会因为未定义的环境变量而报错


settings = Settings()