import json
import boto3
import glob
from utils.const import DYNAMODB_LOCATION_TABLE_NAME

# DynamoDBクライアントを作成
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_LOCATION_TABLE_NAME)

def _batch_write_to_dynamodb(items):
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def exec(input_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)       
        # DynamoDBに書き込むためのデータを準備
        items_to_write = []
        for place in data:
            # TODO なんかnullになることがあるのでバグ調査
            if place.get('city_code') is None:
                print(place)
                continue
            item = {
                'city_code': place.get('city_code'),
                'name': place.get('name'),
                'city_name': place.get('city_name'),
                'display_name': place.get('display_name'),
                'display_address': place.get('display_address'),
                'lat': str(place.get('lat')),
                'lng': str(place.get('lng')),
                'space': str(place.get('space', 0)),
                'station': json.dumps(place.get('station')),
                'reviews': json.dumps(place.get('reviews')),
                'user_rating': json.dumps(place.get('user_rating')),
            }
            print(item)
            items_to_write.append(item)
        # DynamoDBにバッチ書き込み
        _batch_write_to_dynamodb(items_to_write)

# exec()