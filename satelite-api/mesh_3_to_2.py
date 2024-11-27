import pandas as pd

def exec(input_file: str, output_file: str):
    # CSVファイルの読み込み
    df = pd.read_csv(input_file, encoding='utf-8')

    # 3次メッシュコードから2次メッシュコードを抽出
    # 3次メッシュコードは8桁で、上位6桁が2次メッシュコード
    df['2次メッシュコード'] = df['基準メッシュ・コード'].astype(str).str[:6]

    # 重複を排除して2次メッシュコードのリストを作成
    unique_2nd_mesh_codes = df['2次メッシュコード'].drop_duplicates().reset_index(drop=True)

    # 結果をCSVファイルとして保存
    unique_2nd_mesh_codes.to_csv(output_file, index=False, header=False, encoding='utf-8')

# exec(MESH_3_FILE, MESH_3_TO_2_OUTPUT_FILE)