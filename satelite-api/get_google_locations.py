import asyncio
import aiohttp
from math import ceil
import pandas as pd
import json
from utils.const import GOOGLE_API_KEY, GOOGLE_API_RADIUS, GOOGLE_API_REQUEST_COUNT, GOOGLE_API_INCLUDED_TYPES, GOOGLE_API_MAX_THROTTLING_SIZE, GOOGLE_API_DELAY_BETWEEN_BATCHES, GOOGLE_API_URL, GOOGLE_API_FIELD_MASK, GOOGLE_API_OUTPUT_DIR
from utils.file import create_dir

async def fetch_data(session, api_url, api_param):
    lat = api_param["coord"]["lat"]
    lng = api_param["coord"]["lng"]
    included_types = api_param["included_types"]
    """
    非同期でAPIを呼び出し、応答を返す。
    """
    try:

        headers = {
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": GOOGLE_API_FIELD_MASK,
            "content-type": "application/json"
        }
        payload = { 
            "includedTypes": included_types,
            "maxResultCount": GOOGLE_API_REQUEST_COUNT,
            "languageCode": "ja",
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": GOOGLE_API_RADIUS
                }
            }
        }
                
        async with session.post(api_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return {"response": await response.json(), "request": payload}
    except Exception as e:
        return {"error": str(e)}

async def process_in_batches(api_params, api_url, max_api_throttling, delay, output_dir: str):
    create_dir.exec(output_dir)
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
                # 結果をファイルに書き込む
                with open(f"{output_dir}/batch-{batch_idx}-task-{i}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False)

            # 最後のバッチでなければ delay 秒待機
            if batch_idx < total_batches - 1:
                print(f"Waiting for {delay} seconds before the next batch...")
                await asyncio.sleep(delay)

async def _run(input_file: str, output_dir: str):
    # CSVファイルを読み込む
    df = pd.read_csv(input_file)

    # 各行を辞書形式に変換してリスト化する
    # TODO 数値誤差があるため、Decimalに変更する
    coordinates = [{'lat': float(row['lat']), 'lng': float(row['lng'])} for index, row in df.iterrows()]

    api_params = []
    for key, value in GOOGLE_API_INCLUDED_TYPES.items():
        for coord in coordinates:
            api_params.append({"coord": coord, "included_types": value})

    await process_in_batches(api_params, GOOGLE_API_URL, GOOGLE_API_MAX_THROTTLING_SIZE, GOOGLE_API_DELAY_BETWEEN_BATCHES, output_dir)

def exec(input_file: str, output_dir: str):
    asyncio.run(_run(input_file, output_dir))

