import asyncio
import aiohttp
from openai import OpenAI
from pydantic import BaseModel
from utils.const import OPENAI_ORGANIZATION_ID, OPENAI_API_KEY, OPENAI_PLACE_REVIEW_MODEL, OPENAI_API_MAX_THROTTLING, OPENAI_API_DELAY
from math import ceil
import json

client = OpenAI(organization=OPENAI_ORGANIZATION_ID, api_key=OPENAI_API_KEY)

class Review(BaseModel):
    good_point: str
    bad_point: str

def _get_response_json_format():
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "review_location",
                "schema": {
                    "type": "object",
                    "properties": {
                        "good_point": {
                            "type": "string"
                        },
                        "bad_point": {
                            "type": "string"
                        }
                    },
                    "required": ["good_point", "bad_point"],
                    "additionalProperties": False
                },
            "strict": True
            }
    }
    return response_format
     
async def _fetch_review(session, place):
    result = None
    system_prompt = """
    あなたは県内の選挙において、投票所を設置する決裁者である。場所を入力されたら、その場所に投票所を設置する場合の投票活動上の長所と短所をそれぞれ日本語100文字以内でjson形式にまとめて出力する。
    ただし、場所は以下のjson形式で与えられる。
    {
        "name": <投票所の名称>,
        "station": {
            "station": <最寄り駅名>,
            "company": <駅の運営会社名>,
            "rail": <駅の路線名>,
            "distanceM": <最寄り駅までのメートル距離>
        },
        "reviews": [
            {
                "text": <ユーザのコメント>,
                "rating": <ユーザレビューの評価点>
            },...
        ],
        "rating_statistics": {
            "upper_limit": <ユーザレビューの評価点の最高点>,
            "lower_limit": <ユーザレビューの評価点の最低点>,
            "average_rating": <ユーザレビューの評価点の平均点>
        }
    }
    """
    try:
        async with session.post(
            'https://api.openai.com/v1/chat/completions',
        json={
            "model": OPENAI_PLACE_REVIEW_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"投票所の情報: {place}"}
            ],
            "response_format": _get_response_json_format(),
        },
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Organization": OPENAI_ORGANIZATION_ID
        }
        ) as response:
            result = await response.json()
            choice = result.get("choices")[0]
            message = choice.get("message")
            content = message.get("content")
            if choice.get("finish_reason") != "stop" or message.get("refusal") is not None:
                print(place)
                print(result)
                return None
            return json.loads(content)
    except Exception as e:
        print("error")
        print(e)
        print(place)
        print(result)
        return None

async def _batch_fetch_review(request_items):
    results = []
    async with aiohttp.ClientSession() as session:

        total_batches = ceil(len(request_items) / OPENAI_API_MAX_THROTTLING)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * OPENAI_API_MAX_THROTTLING
            end_idx = start_idx + OPENAI_API_MAX_THROTTLING
            batch = request_items[start_idx:end_idx]

            print(f"Processing batch {batch_idx + 1}/{total_batches}...")

            tasks = [
                    _fetch_review(session, task_param.get("place"))
                for task_param in batch
            ]

            results.extend(await asyncio.gather(*tasks))
            # 最後のバッチでなければ delay 秒待機
            if batch_idx < total_batches - 1:
                print(f"Waiting for {OPENAI_API_DELAY} seconds before the next batch...")
                await asyncio.sleep(OPENAI_API_DELAY)
    return results
    
    
def exec(request_items):
    print("exec")
    print(len(request_items))
    return asyncio.run(_batch_fetch_review(request_items))

def _get_place_info(place):
    info = {
        "name": place.get("name"),
        "station": {
            "station": place.get("station").get("station"),
            "company": place.get("station").get("company"),
            "rail": place.get("station").get("rail"),
            "distanceM": place.get("station").get("distanceM")
        },
        "reviews": [
            {
                "text": review.get("text"),
                "rating": review.get("rating")
            } for review in place.get("reviews")
        ],
        "rating_statistics": {
            "upper_limit": place.get("user_rating").get("upper_limit"),
            "lower_limit": place.get("user_rating").get("lower_limit"),
            "average_rating": place.get("user_rating").get("average_rating")
        }
    }

    return info
    

def test():
    places = [{
        "lat": 35.61175,
        "lng": 139.6282344,
        "space": 12601.76,
        "station": {
            "station": "二子玉川",
            "company": "東急電鉄",
            "companyDisplayLabel": "東急",
            "rail": "大井町線",
            "distanceM": 175
        },
        "name": "places/ChIJVVWV3z_0GGARlmuWyKGhjH0",
        "display_name": "二子玉川ライズ",
        "display_address": "日本、〒158-0094 東京都世田谷区玉川２丁目２１−１",
        "reviews": [
            {
                "text": "駅から二子玉川公園に向かう際に通りました。\n\nとにかくオシャレ！憧れの蔦屋家電にも立ち寄れます！笑\n\nショッピングモールにいながら緑と自然を感じられる作りになっているので、天気の良い日はとても気持ちが良いです♪",
                "rating": 5
            },
            {
                "text": "イベントがあったため、サイクリングを兼ねて訪問。駐輪場も3時間無料で台数の余裕もある。\n\n建物は開放的で洗練されれおり、レストランや映画館などが充実しているので、地元の人は便利だと思われる。\n★3つにしたのは、このショッピングセンターの為に地元以外の人は来ないと思われるため。\n地元の人にとっては★5つと思われる。",
                "rating": 3
            }
        ],
        "city_name": "世田谷区",
        "city_code": "13112",
        "user_rating": {
            "upper_limit": 5.0,
            "lower_limit": 1.0,
            "average_rating": 3.9
        }
    }]
    request_places = [ {"place": _get_place_info(place), "name": place.get("name")} for place in places]
    print(exec(request_places))