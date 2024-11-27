# output/merged-locations/google-org/yyyymmdd-hhmmss.jsonを読み込んで、city_codeが13のもののみを抽出してoutput/filtered-merged-locations/google-org/yyyymmdd-hhmmss.jsonに出力する
import json
import os
from utils.file import create_dir
from utils.const import FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME, FILTERED_INVALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME

def _is_invalid_city_code(place):
    return place['city_code'] is None or place['space'] is None or place['station'] is None

def exec(input_file_path: str, output_dir: str):
    # 条件に合わないplaceを抽出して、bug_placesに格納する
    bug_places = []
    # 条件に合うplaceを抽出して、filtered_placesに格納する
    filtered_places = []
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for place in data:
            if not _is_invalid_city_code(place):
                filtered_places.append(place)
            else:
                bug_places.append(place)
    create_dir.exec(output_dir)
    with open(f"{output_dir}/{FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME}", 'w', encoding='utf-8') as f:
        json.dump(filtered_places, f, ensure_ascii=False, indent=4)
    with open(f"{output_dir}/{FILTERED_INVALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME}", 'w', encoding='utf-8') as f:
        json.dump(bug_places, f, ensure_ascii=False, indent=4)