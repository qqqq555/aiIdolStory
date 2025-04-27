import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print(f"收到的事件: {json.dumps(event)}")
    
    try:
        body = {}
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
                
        user_input = body.get('user_input', '')
        print(f"用戶輸入: {user_input}")
        
        client_runtime = boto3.client('bedrock-agent-runtime')
        
        FLOW_ID = os.environ.get('FLOW_ID', '你的Flow ID')
        FLOW_ALIAS_ID = os.environ.get('FLOW_ALIAS_ID', '你的Flow Alias ID')

        inputs = [
            {
                "content": {
                    "document": user_input 
                },
                "nodeName": "FlowInputNode",
                "nodeOutputName": "document"
            }
        ]
        
        print(f"發送到 Bedrock Flow 的輸入: {json.dumps(inputs)}")

        response = client_runtime.invoke_flow(
            flowIdentifier=FLOW_ID,
            flowAliasIdentifier=FLOW_ALIAS_ID,
            inputs=inputs
        )
        
        response = client_runtime.invoke_flow(
            flowIdentifier=FLOW_ID,
            flowAliasIdentifier=FLOW_ALIAS_ID,
            inputs=inputs
        )

        doc_obj = capture_document_object(response)

        return build_success_response({
            "document": doc_obj
        })

            
    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return build_error_response(500, f"處理請求時發生錯誤: {str(e)}")
def capture_document_object(response):
    if not isinstance(response, dict) or 'responseStream' not in response:
        return {}

    for event in response['responseStream']:
        flow_evt = event.get('flowOutputEvent')
        if not flow_evt:
            continue

        content = flow_evt.get('content', {})

        doc_obj = content.get('document')
        if isinstance(doc_obj, dict):
            return doc_obj

    return {}


def build_success_response(data):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data, default=str)
    }

def build_error_response(status_code, message):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'error': True,
            'message': message
        })
    }