import boto3
import json
from utils.const import DYNAMODB_LOCATION_TABLE_NAME
from utils.llm import embed_locations
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
# DynamoDBリソースを初期化
dynamodb = boto3.resource('dynamodb')

# テーブル名を指定
table = dynamodb.Table(DYNAMODB_LOCATION_TABLE_NAME)

def _get_place_info(place):
    station = json.loads(place.get("station"))
    reviews = json.loads(place.get("reviews"))
    info = {
        "name": place.get("display_name"),
        "station": {
            "station": station.get("station"),
            "company": station.get("company"),
            "rail": station.get("rail"),
            "distanceM": station.get("distanceM")
        },
        "reviews": [
            {
                "text": review.get("text"),
                "rating": review.get("rating")
            } for review in reviews
        ], 
    }

    return info

def _embedding_place_to_dynamo_format(embedding_place):
    dynamo_format_vector = [
        str(elm) for elm in embedding_place.get("embedding")
    ]
    return {"embedding": dynamo_format_vector}

def _add_embeddings_to_places(places):
    request_places = [ {"place": _get_place_info(place), "name": place.get("name")} for place in places]
    embedding_places = embed_locations.exec(request_places)
    # return embedding_places
    result_places = [{ **places[idx],**(_embedding_place_to_dynamo_format(embedding_place) if embedding_place is not None else {})} for idx, embedding_place in enumerate(embedding_places)]
    return result_places


def _write_batch(batch_places):
    print(len(batch_places))
    # print(batch_places)
    with table.batch_writer() as batch:
        for place in batch_places:
            batch.put_item(Item=place)

def exec():
    # good_point_attribute_filter = Attr('good_point').not_exists()
    column_not_exists_filter = Attr('name').exists()
    # スキャン操
    response = table.scan(
        FilterExpression=column_not_exists_filter
    )
    places = response.get('Items', [])
    # TODO test
    # places = places[:11]

    batch_places = _add_embeddings_to_places(places)

    # 再帰的にスキャンの継続 (データが多い場合)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression=column_not_exists_filter)
        places = response.get('Items', [])
        batch_places.extend(_add_embeddings_to_places(places))
    _write_batch(batch_places)
