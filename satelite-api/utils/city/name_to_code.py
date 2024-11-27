# 13.csvを読み込んで、city_nameとcity_codeのmapを作成する
import pandas as pd
from utils.const import MESH_3_FILE

# すべて文字列で読み込む
df = pd.read_csv(MESH_3_FILE, encoding='utf-8', dtype=str)
def exec(city_name):
    # city_nameが合致しない場合は、Noneを返す
    result = df[df['市区町村名'] == city_name]['都道府県市区町村コード'].values[0] if city_name in df['市区町村名'].values else None
    return result