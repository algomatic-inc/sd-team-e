import json
import boto3
import glob
from utils.const import DYNAMODB_LOCATION_TABLE_NAME

# DynamoDBクライアントを作成
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_LOCATION_TABLE_NAME)

def exec():
    # テーブルから全てのアイテムをスキャン
    response = table.scan()
    items = response.get('Items', [])

    # 各アイテムを削除
    with table.batch_writer() as batch:
        # key_schemaからAttributeNameのリストを取得
        keys= [ key_item['AttributeName'] for key_item in table.key_schema ]
        for item in items:
            # アイテムの主キーを取得
            key = {k: item[k] for k in keys}
            batch.delete_item(Key=key)
    
    print(f"{len(items)} items deleted from {table}")

    # 再帰的に処理 (もしアイテムが多く、scanで全て取得できない場合)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items = response.get('Items', [])
        with table.batch_writer() as batch:
            for item in items:
                key = {k: item[k] for k in table.key_schema[0].keys()}
                batch.delete_item(Key=key)
        print(f"{len(items)} additional items deleted from {table}")