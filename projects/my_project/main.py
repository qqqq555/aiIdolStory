# main.py
from load_env import load_env_file
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    應用程序主入口
    """
    # 加載環境變量
    load_env_file()
    
    # 導入配置
    from config import HOST, PORT, DEBUG
    from app import app
    
    logger.info(f"啟動S3 MP4視頻播放器應用於 {HOST}:{PORT}, DEBUG模式: {DEBUG}")
    app.run(host=HOST, port=PORT, debug=DEBUG)

if __name__ == "__main__":
    main()