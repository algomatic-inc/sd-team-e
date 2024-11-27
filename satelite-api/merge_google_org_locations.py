import json
import glob
import os
from utils.city import name_to_code
from utils.file import create_dir
from utils.const import MERGED_GOOGLE_ORG_OUTPUT_BASENAME, ORG_ONLY_OUTPUT_BASENAME, GOOGLE_ONLY_OUTPUT_BASENAME

def exec(google_input_dir: str, org_input_dir: str, output_dir: str):
    # JSONファイルのパスを取得
    org_files = glob.glob(f'{org_input_dir}batch-*.json')
    google_files = glob.glob(f'{google_input_dir}batch-*.json')

    # 各ディレクトリのデータを連結
    org_data_combined = []
    for org_file in org_files:
        with open(org_file, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
            request_param = org_data.get('request', {})
            place = org_data.get('response', {})
            stations = place.get('station', {}).get('stations', [])
            station = stations[0] if len(stations) > 0 else {}
            # 必要な列だけを抽出
            filtered_item = {
                "name": org_data.get('name'),
                "place": {
                    'lat': request_param.get('latitude'),
                    'lng': request_param.get('longitude'),
                    'space': place.get('chibanArea'),
                    'station': station
                }
            }
            org_data_combined.append(filtered_item)

    google_data_combined = []
    for google_file in google_files:
        with open(google_file, 'r', encoding='utf-8') as f:
            google_data = json.load(f)
            for place in google_data.get('response', {}).get('places', []):
                reviews = place.get('reviews', [])
                text_reviews = [review for review in reviews if review.get('text', {}).get('text')]
                # sort by rating
                text_reviews.sort(key=lambda x: x.get('rating'), reverse=True)

                filtered_reviews = []
                if len(text_reviews) > 0:
                    filtered_reviews.append({'text': text_reviews[0].get('text').get('text'), 'rating': text_reviews[0].get('rating')})  # First review
                    if len(text_reviews) > 1:
                        try:
                            filtered_reviews.append({'text': text_reviews[-1].get('text').get('text'), 'rating': text_reviews[-1].get('rating')})  # Last review
                        except:
                            print(f"error: {text_reviews[-1]}")

                address_components = place.get('addressComponents', [])
                # typsに'locali
                city_name = [component.get('longText') for component in address_components if 'locality' in component.get('types', [])][0]
                # 隣接する県に入ってしまうケースがある
                city_code = name_to_code.exec(city_name)
                # 必要な列だけを抽出
                filtered_item = {
                    "name": place.get('name'),
                    "place": {
                        "name": place.get('name'),
                        "display_name": place.get('displayName').get('text'),
                        "display_address": place.get('formattedAddress'),
                        'lat': place.get('location', {}).get('latitude'),
                        'lng': place.get('location', {}).get('longitude'),
                        "reviews": filtered_reviews,
                        "city_name": city_name,
                        "city_code": city_code,
                        "user_rating": {"upper_limit": 5.0, "lower_limit": 1.0, "average_rating": place.get('rating')}, 
                    },
                }
                google_data_combined.append(filtered_item)

    # lat, lngでマージ
    org_places = {f"{item['name']}": item.get('place') for item in org_data_combined}
    google_places = {f"{item['name']}": item.get('place') for item in google_data_combined}

    merged_data = []
    # 両方に存在するkeyのみマージ (Merge only keys present in both)
    for key in set(org_places.keys()).intersection(google_places.keys()):
        merged_place = org_places.get(key, {})
        merged_place.update(google_places.get(key, {}))
        merged_data.append(merged_place)

    # 出力ディレクトリを作成
    create_dir.exec(output_dir)
    # マージされたデータをJSONファイルに出力
    with open(f'{output_dir}{MERGED_GOOGLE_ORG_OUTPUT_BASENAME}', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    # 差分を出力
    org_only_data_keys = list(set(org_places.keys()) - set(google_places.keys()))
    with open(f'{output_dir}{ORG_ONLY_OUTPUT_BASENAME}', 'w', encoding='utf-8') as f:
        # org_only_dataのkeyからorg_placesのvalueを取得
        org_only_data = [{'name': key, 'place': org_places.get(key)} for key in org_only_data_keys]
        json.dump(org_only_data, f, ensure_ascii=False, indent=4)

    # 差分を出力
    google_only_data_keys = list(set(google_places.keys()) - set(org_places.keys()))
    with open(f'{output_dir}{GOOGLE_ONLY_OUTPUT_BASENAME}', 'w', encoding='utf-8') as f:
        # google_only_dataのkeyからgoogle_placesのvalueを取得
        google_only_data = [{'name': key, 'place': google_places.get(key)} for key in google_only_data_keys]
        json.dump(google_only_data, f, ensure_ascii=False, indent=4)

# exec()
