import boto3
import json
from utils.const import DYNAMODB_LOCATION_TABLE_NAME
from utils.llm import review_locations
from boto3.dynamodb.conditions import Attr
# DynamoDBリソースを初期化
dynamodb = boto3.resource('dynamodb')

# テーブル名を指定
table = dynamodb.Table(DYNAMODB_LOCATION_TABLE_NAME)

def _get_place_info(place):
    station = json.loads(place.get("station"))
    user_rating = json.loads(place.get("user_rating"))
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
            } for review in json.loads(place.get("reviews"))
        ],
        "rating_statistics": {
            "upper_limit": user_rating.get("upper_limit"),
            "lower_limit": user_rating.get("lower_limit"),
            "average_rating": user_rating.get("average_rating")
        }
    }

    return info

def _add_reviews_to_places(places):
    request_places = [ {"place": _get_place_info(place), "name": place.get("name")} for place in places]
    review_places = review_locations.exec(request_places)
    # return review_places
    result_places = [{**places[idx], **(review_place if review_place is not None else {})} for idx, review_place in enumerate(review_places)]
    return result_places


def _write_batch(batch_places):
    print(len(batch_places))
    with table.batch_writer() as batch:
        for place in batch_places:
            batch.put_item(Item=place)

def exec():
    # good_point_attribute_filter = Attr('good_point').not_exists()
    good_point_attribute_filter = Attr('name').exists()
    # スキャン操
    response = table.scan(
        FilterExpression=good_point_attribute_filter
    )
    places = response.get('Items', [])
    # TODO test
    # places = places[:30]

    batch_places = _add_reviews_to_places(places)

    # 再帰的にスキャンの継続 (データが多い場合)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression=good_point_attribute_filter)
        places = response.get('Items', [])
        batch_places.extend(_add_reviews_to_places(places))
    _write_batch(batch_places)
