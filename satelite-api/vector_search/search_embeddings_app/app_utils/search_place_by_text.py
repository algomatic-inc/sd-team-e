import boto3
from boto3.dynamodb.conditions import Attr
from app_utils.embed import calc_similarity, embed
from app_utils.db import get_merged_locations

# DynamoDBリソースを初期化
dynamodb = boto3.resource('dynamodb')

# テーブル名を指定
table = dynamodb.Table('location')

def _place_to_calc_similarity_format(place):
    return [ float(elm) for elm in place.get("embedding")]


def _add_similarity_to_places(input_embedding, places):
    embeddings = [_place_to_calc_similarity_format(place) for place in places]
    similarities = calc_similarity.exec(input_embedding, embeddings)
    result_places = [ {"similarity": similarity, "place": places[idx] } for idx, similarity in enumerate(similarities)]
    return result_places


def exec(input_text:str, count=5):
    input_embedding = embed.exec(input_text).get("embedding")

    column_exists_filter = Attr('embedding').exists()
    # スキャン操
    response = table.scan(
        FilterExpression=column_exists_filter
    )
    places = response.get('Items', [])

    result_places = _add_similarity_to_places(input_embedding, places)

    # 再帰的にスキャンの継続 (データが多い場合)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression=column_exists_filter)
        places = response.get('Items', [])
        result_places.extend(_add_similarity_to_places(input_embedding, places))
    
    # 類似度が高いものから取得
    result_places.sort(key=lambda x: x.get("similarity"), reverse=True)
    print("sorted")
    filtered_result_places = result_places[:count] if len(result_places) > count else result_places
    filtered_places = [ x.get("place") for x in filtered_result_places]
    print(f"filtered: {len(filtered_places)}")
    
    return get_merged_locations.exec(filtered_places)
    
