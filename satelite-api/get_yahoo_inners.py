import asyncio
import aiohttp
from math import ceil
import pandas as pd
import json
import glob
import os

async def fetch_data(session, api_url, api_param):
    API_KEY = ""
    lat = api_param["coord"]["lat"]
    lng = api_param["coord"]["lng"]
    """
    非同期でAPIを呼び出し、応答を返す。
    """
    try:
        payload = {
            "appid": API_KEY,
            "lat": lat,
            "lon": lng,
            "results": 1,
            "output": "json"
        }
                
        async with session.get(api_url, params=payload) as response:
            response.raise_for_status()
            return {"response": await response.json(), "request": payload}
    except Exception as e:
        return {"error": str(e)}

async def process_in_batches(api_params, api_url, max_api_throttling, delay):
    """
    配列を分割し、スロットリング制限に従ってAPIを呼び出す。
    """
    async with aiohttp.ClientSession() as session:
        total_batches = ceil(len(api_params) / max_api_throttling)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * max_api_throttling
            end_idx = start_idx + max_api_throttling
            batch = api_params[start_idx:end_idx]

            print(f"Processing batch {batch_idx + 1}/{total_batches}...")

            tasks = [
                fetch_data(session, api_url, api_param)
                for api_param in batch
            ]

            results = await asyncio.gather(*tasks)

            for i, result in enumerate(results):
                print(f"Result for {batch[i]}: {result}")
                output_dir = "output/yahoo-inners"
                # 結果をファイルに書き込む
                with open(f"{output_dir}/batch-{batch_idx}-task-{i}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False)

            # 最後のバッチでなければ delay 秒待機
            if batch_idx < total_batches - 1:
                print(f"Waiting for {delay} seconds before the next batch...")
                await asyncio.sleep(delay)

async def exec():
    api_url = "https://map.yahooapis.jp/inner/V1/building"  # 適切なAPI URLを指定

    # JSONファイルのパスを取得
    csv_files = glob.glob('output/google-locations/google-lat-lng/batch-*.csv')

    coordinates = []

    for csv_file in csv_files:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_file)
        coordinates.extend([{'lat': float(row['lat']), 'lng': float(row['lng'])} for index, row in df.iterrows()])

    api_params = []
    for coord in coordinates:
        api_params.append({"coord": coord})

    # スロットリング制限と待機時間
    MAX_API_THROTTLING = 2 # 一度に実行できる最大のAPIリクエスト数
    DELAY_BETWEEN_BATCHES = 5  # 各バッチ間の待機時間（秒）

    await process_in_batches(api_params, api_url, MAX_API_THROTTLING, DELAY_BETWEEN_BATCHES)

# 実行
if __name__ == "__main__":
    asyncio.run(exec())
