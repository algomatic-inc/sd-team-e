# output/google-locations/batch-*.jsonを読み込んで、lat, lngを抽出してoutput/google-locations/google-lat-lng/batch-*.csvに出力する
import json
import glob
import csv
import os
from utils.file import create_dir

# TODO googleの結果のfiltering余地がある
def exec(input_dir: str, output_dir: str):
    # JSONファイルのパスを取得
    json_files = glob.glob(f'{input_dir}/batch-*.json')
    create_dir.exec(output_dir)

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # lat, lngを抽出
        lat_lng_data = []
        for place in data.get('response', {}).get('places', []):
            location = place.get('location', {})
            lat = location.get('latitude')
            lng = location.get('longitude')
            if lat is not None and lng is not None:
                lat_lng_data.append({'name': place.get('name'), 'lat': lat, 'lng': lng})
        
        # CSVファイルに出力
        csv_file = os.path.join(output_dir, os.path.basename(json_file).replace('.json', '.csv'))
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'lat', 'lng']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in lat_lng_data:
                writer.writerow(row)