import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IdolStoryState')

def lambda_handler(event, context):
    user_id = "test"
    
    try:
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id),
            ScanIndexForward=False,  
            Limit=1
        )
        
        if response['Items']:
            item = response['Items'][0]
            affinity = str(item.get('affinity', 30))
            chat_history = item.get('chat_history', '')
        
            if not chat_history:
                chat_history = "故事剛剛開始"
            
            result = {
                "affinity": affinity,
                "chat_history": chat_history
            }
        else:
            result = {
                "affinity": "30",
                "chat_history": "故事剛剛開始"
            }
            
            table.put_item(
                Item={
                    'userId': user_id,
                    'recordId': '1', 
                    'affinity': int(result['affinity']),
                    'chat_history': result['chat_history'],
                }
            )
    
        return {
            "affinity": str(result['affinity']),
            "chat_history": result['chat_history'],
        }
    
    except Exception as e:
        print(f"讀取數據時出錯: {str(e)}")
        return {
            "affinity": "30",
            "chat_history": "故事剛剛開始",
        }