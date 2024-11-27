import asyncio
import aiohttp
from math import ceil
import pandas as pd
import json
import glob
import os
from utils.const import ORG_API_URL, ORG_API_MAX_THROTTLING_SIZE, ORG_API_DELAY_BETWEEN_BATCHES, ORG_API_KEY, ORG_API_OUTPUT_DIR, GOOGLE_API_LAT_LNG_OUTPUT_DIR
from utils.file import create_dir
async def fetch_data(session, api_url, task_param):
    api_param = task_param.get("api_param", {})
    lat = api_param.get("lat", 0)
    lng = api_param.get("lng", 0)
    """
    非同期でAPIを呼び出し、応答を返す。
    """
    try:
        payload = {
            "api_key": ORG_API_KEY,
            "latitude": lat,
            "longitude": lng
        }
                
        async with session.post(api_url, json=payload) as response:
            response.raise_for_status()
            return {"response": await response.json(), "request": payload, "name": task_param.get("name")}
    except Exception as e:
        return {"error": str(e)}

async def process_in_batches(task_params, api_url, max_api_throttling, delay, output_dir: str):
    """
    配列を分割し、スロットリング制限に従ってAPIを呼び出す。
    """
    create_dir.exec(output_dir)
    async with aiohttp.ClientSession() as session:
        total_batches = ceil(len(task_params) / max_api_throttling)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * max_api_throttling
            end_idx = start_idx + max_api_throttling
            batch = task_params[start_idx:end_idx]

            print(f"Processing batch {batch_idx + 1}/{total_batches}...")

            tasks = [
                fetch_data(session, api_url, task_param)
                for task_param in batch
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

async def _run(input_dir: str, output_dir: str):
    # JSONファイルのパスを取得
    csv_files = glob.glob(f'{input_dir}/batch-*.csv')

    task_params = []

    for csv_file in csv_files:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_file)
        task_params.extend([{'api_param': {'lat': float(row['lat']), 'lng': float(row['lng'])}, 'name': row['name']} for index, row in df.iterrows()])

    await process_in_batches(task_params, ORG_API_URL, ORG_API_MAX_THROTTLING_SIZE, ORG_API_DELAY_BETWEEN_BATCHES, output_dir)

# 実行
def exec(input_dir: str, output_dir: str):
    asyncio.run(_run(input_dir, output_dir))
