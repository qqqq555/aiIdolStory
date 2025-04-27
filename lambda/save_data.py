import json
import boto3
import re
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IdolStoryState')

def lambda_handler(event, context):

    print(f"收到的完整事件: {json.dumps(event, default=str)}")

    user_id = "test"
    
    try:

        ai_response = None
  
        if (isinstance(event, dict) and 'node' in event and 
            isinstance(event['node'], dict) and 'inputs' in event['node'] and 
            isinstance(event['node']['inputs'], list) and len(event['node']['inputs']) > 0 and
            isinstance(event['node']['inputs'][0], dict) and 'value' in event['node']['inputs'][0]):
            
            ai_response = event['node']['inputs'][0]['value']
            print(f"從 node.inputs[0].value 獲取 AI 回應: {ai_response[:100]}...")

        if not ai_response:
            error_msg = "無法獲取 AI 回應"
            print(error_msg)

            return {
                "document": f"錯誤: {error_msg}。請檢查 Lambda 函數的日誌。",
                "scene": "未知場景"
            }

        affinity_match = re.search(r'\[好感度:?\s*(\d+)\]', ai_response)
        new_affinity = 30  
        
        if affinity_match:
            try:
                new_affinity = int(affinity_match.group(1))
                new_affinity = max(0, min(100, new_affinity))
                print(f"提取到的好感度: {new_affinity}")
            except (ValueError, IndexError) as e:
                print(f"解析好感度失敗，使用預設值 30: {str(e)}")
        else:
            print("未找到好感度標記，使用預設值 30")
        
        scene_match = re.search(r'\[場景:\s*([^\]]+)\]', ai_response)
        current_scene = "未知場景"
        
        if scene_match:
            current_scene = scene_match.group(1).strip()
            print(f"提取到的場景: {current_scene}")
        else:
            print("未找到場景標記，使用預設值")
        
        display_response = re.sub(r'\[好感度:?\s*\d+\]', '', ai_response).strip()
        
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        
        record_count = len(response.get('Items', []))
        new_record_id = str(record_count + 1)
        print(f"新記錄 ID: {new_record_id}")
        
        dialog_parts = re.findall(r'\[夏浦洋\](.*?)(?=\[|\Z)', display_response, re.DOTALL)
        dialog_summary = ""
        
        if dialog_parts:
            joined_dialog = " ".join([part.strip() for part in dialog_parts])
            dialog_summary = joined_dialog[:100] + ("..." if len(joined_dialog) > 100 else "")
            print(f"提取的對話摘要: {dialog_summary}")
        else:
            print("未找到對話片段，使用前100個字符作為摘要")
            dialog_summary = display_response[:100] + ("..." if len(display_response) > 100 else "")
        timestamp = datetime.now().isoformat()
        
        try:
            table.put_item(
                Item={
                    'userId': user_id,
                    'recordId': new_record_id,
                    'affinity': new_affinity,
                    'scene': current_scene, 
                    'chat_history': dialog_summary,
                    'full_content': display_response,
                    'timestamp': timestamp
                }
            )
            print("成功儲存到 DynamoDB")
        except Exception as db_error:
            print(f"儲存到 DynamoDB 時出錯: {str(db_error)}")
        return {
            "document": display_response,  
            "scene": current_scene,  
            "affinity": new_affinity
        }
    
    except Exception as e:
        print(f"處理資料時出錯: {str(e)}")
        return {
            "document": f"發生錯誤: {str(e)}",
            "scene": "錯誤場景"
        }