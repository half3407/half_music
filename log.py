import os
from loguru import logger

retention_days = os.getenv("MUSIC_LOG_RETENTION_DAYS", "5")
retention = f"{retention_days} days"
LOG_LEVEL = os.getenv("MUSIC_LOG_LEVEL", "INFO").upper()


def init_logger(log_file: str = "app.log", level: str = LOG_LEVEL):
    logger.remove()
    logger.add(
        log_file,
        level=os.environ.get("MUSIC_LOG_FILE_LEVEL", "DEBUG"),
        rotation=os.environ.get("MUSIC_LOG_ROTATION_SIZE", "5 MB"),
        retention=retention,
        compression="zip",
    )

    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=os.environ.get("MUSIC_LOG_CONSOLE_LEVEL", "INFO"),
    )

    logger.info(f"日志器初始化... 日志文件 {log_file} 当前日志等级 {level}")
    logger.info(
        f"日志器配置：轮转大小 {os.environ.get("MUSIC_LOG_ROTATION_SIZE", "5 MB")}，保留天数 {5} 天，旧日志压缩为 zip 格式"
    )
