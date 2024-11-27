import asyncio
import aiohttp
from openai import OpenAI
from pydantic import BaseModel
from utils.const import OPENAI_ORGANIZATION_ID, OPENAI_API_KEY, OPENAI_API_EMBED_MODEL, OPENAI_API_MAX_THROTTLING, OPENAI_API_DELAY
from math import ceil
     
async def _fetch_api(session, place):
    reviews_string = "、".join([ f'「{x.get("text")}」' for x in place.get("reviews") ])
    result = None
    input_text = f"""
    場所名：{place.get("name")},\n
    最寄駅：{place.get("station").get("station")},\n
    駅の運営会社：{place.get("station").get("company")},\n
    駅の路線：{place.get("station").get("rail")},\n
    レビュー一覧：{reviews_string}
    """
    try:
        async with session.post(
            'https://api.openai.com/v1/embeddings',
        json={
            "model": OPENAI_API_EMBED_MODEL,
            "input": input_text
        },
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Organization": OPENAI_ORGANIZATION_ID
        }
        ) as response:
            result = await response.json()
            return {'embedding': result.get("data")[0].get("embedding")}
    except Exception as e:
        print("error")
        print(e)
        print(place)
        print(result)
        return None

async def _batch_fetch_api(request_items):
    results = []
    async with aiohttp.ClientSession() as session:

        total_batches = ceil(len(request_items) / OPENAI_API_MAX_THROTTLING)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * OPENAI_API_MAX_THROTTLING
            end_idx = start_idx + OPENAI_API_MAX_THROTTLING
            batch = request_items[start_idx:end_idx]

            print(f"Processing batch {batch_idx + 1}/{total_batches}...")

            tasks = [
                    _fetch_api(session, task_param.get("place"))
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
    return asyncio.run(_batch_fetch_api(request_items))

def _get_place_info(place):
    info = {
        "name": place.get("display_name"),
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