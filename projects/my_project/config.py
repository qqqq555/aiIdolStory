# config.py
import os

# S3配置
S3_BUCKET = os.environ.get('S3_BUCKET', 'your-bucket-name')
S3_REGION = os.environ.get('S3_REGION', 'your-region')  # 例如 us-east-1
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'your-access-key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'your-secret-key')

# 應用配置
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')

# 顯示配置（不顯示敏感信息）
def get_config_summary():
    return {
        'S3_BUCKET': S3_BUCKET,
        'S3_REGION': S3_REGION,
        'DEBUG': DEBUG,
        'PORT': PORT,
        'HOST': HOST
    }