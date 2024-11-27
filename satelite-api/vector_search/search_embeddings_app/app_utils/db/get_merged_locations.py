import boto3

# DynamoDBリソースを初期化
dynamodb = boto3.resource('dynamodb')

# テーブル名を指定
table = dynamodb.Table('merged_location')

def exec(places):
    # スキャン操
    response = table.scan()
    merged_places = response.get('Items', [])
    merged_place_dict = {}

    for merged_place in merged_places:
        merged_place_dict[merged_place.get("name")] = merged_place


    # 再帰的にスキャンの継続 (データが多い場合)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        merged_places = response.get('Items', [])
        for merged_place in merged_places:
            merged_place_dict[merged_place.get("name")] = merged_place
        
    return [ merged_place_dict.get(x.get("name")) for x in places]
    
