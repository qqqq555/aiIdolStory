# app.py
from flask import Flask, render_template, url_for, redirect, jsonify, request
import boto3
import os
import time
from datetime import datetime
from botocore.client import Config
import logging
import json

# 配置S3連接
S3_BUCKET = os.environ.get('S3_BUCKET', 'your-bucket-name')
S3_REGION = os.environ.get('S3_REGION', 'your-region')  # 例如 us-east-1
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'your-access-key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'your-secret-key')

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# 創建S3客戶端
try:
    s3_client = boto3.client(
        's3',
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    logger.info("S3客戶端創建成功")
except Exception as e:
    logger.error(f"創建S3客戶端時出錯: {e}")
    s3_client = None

# 假的對白文字，根據視頻順序
DIALOGUE_TEXTS = [
    "謝謝大家今天來參加我們的見面會！看到這麼多洋咩咩們來支持我，真的很開心!",
    " 大家真的太棒了！啊...等等...(小聲自言自語)",
    "真的嗎？你願意幫我找？",
    "抱歉...我太激動了。那條項鍊真的對我意義非凡。",
    "是一條銀色的，上面有個小小的籃球吊墜。是我媽媽送我的幸運物...",
    "今天還有後續的見面會，我真的需要找到它。",
    "謝謝你這麼認真地幫我找！舞台對我來說是很特別的地方。",
    "每次站在這裡表演前，我都會摸摸那條項鍊，感覺媽媽就在身邊...",
    "等等！那是什麼？那邊好像有東西在發亮！",
]

@app.route('/')
def index():
    """主頁面 - 顯示第一個視頻和對白"""
    if not s3_client:
        return render_template('error.html', message="無法連接到S3服務")
    
    try:
        # 獲取S3存儲桶中的所有對象
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        
        videos = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # 只處理outputVids目錄中的MP4文件
                if obj['Key'].lower().endswith('.mp4') and 'outputVids' in obj['Key']:
                    # 生成預簽名URL，有效期為1小時
                    presigned_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': S3_BUCKET, 'Key': obj['Key']},
                        ExpiresIn=3600
                    )
                    videos.append({
                        'name': obj['Key'],
                        'url': presigned_url,
                        'dialogue': DIALOGUE_TEXTS[min(len(videos), len(DIALOGUE_TEXTS)-1)]  # 確保對白索引不超出範圍
                    })
            
            logger.info(f"成功獲取{len(videos)}個MP4文件")
            
            # 排序視頻（如果需要）
            # videos.sort(key=lambda x: x['name'])
            
            # 將視頻列表存儲在會話中
            app.config['VIDEOS'] = videos
            
            if videos:
                # 返回第一個視頻
                return render_template(
                    'video_player.html', 
                    current_video=videos[0], 
                    video_index=0, 
                    total_videos=len(videos)
                )
            else:
                return render_template('error.html', message="在outputVids目錄中沒有找到MP4文件")
        else:
            return render_template('error.html', message="S3存儲桶中沒有內容")
            
    except Exception as e:
        logger.error(f"獲取視頻列表時出錯: {e}")
        return render_template('error.html', message=f"獲取視頻時發生錯誤: {str(e)}")

@app.route('/video/<int:index>')
def show_video(index):
    """顯示指定索引的視頻"""
    videos = app.config.get('VIDEOS', [])
    
    if not videos:
        return redirect(url_for('index'))
    
    # 確保索引在有效範圍內
    if index < 0:
        index = 0
    if index >= len(videos):
        index = len(videos) - 1
    
    return render_template(
        'video_player.html', 
        current_video=videos[index], 
        video_index=index, 
        total_videos=len(videos)
    )

@app.route('/health')
def health_check():
    """健康檢查端點"""
    status = "healthy" if s3_client else "unhealthy"
    return jsonify({
        "status": status,
        "bucket": S3_BUCKET
    })

@app.errorhandler(404)
def page_not_found(e):
    """404頁面"""
    return render_template('error.html', message="找不到請求的頁面"), 404

@app.errorhandler(500)
def server_error(e):
    """500頁面"""
    logger.error(f"服務器錯誤: {e}")
    return render_template('error.html', message="服務器內部錯誤"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)