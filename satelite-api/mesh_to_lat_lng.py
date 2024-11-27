import pandas as pd

def exec(input_file: str, output_file: str):
    # CSVファイルの読み込み
    df = pd.read_csv(input_file, header=None, names=['2次メッシュコード'], dtype=str)

    # 各2次メッシュコードに対して中心の緯度・経度を計算
    df[['lat', 'lng']] = df['2次メッシュコード'].apply(_meshcode_to_latlon).apply(pd.Series)

    # 結果をCSVファイルとして保存
    df.to_csv(output_file, columns=['lat', 'lng'], index=False, encoding='utf-8')


# 2次メッシュコードから中心の緯度・経度を計算する関数
def _meshcode_to_latlon(mesh_code):
    """
    Converts a second-level regional mesh code to the central latitude and longitude.
    
    Parameters:
    mesh_code (str): A 6-digit string representing the second-level mesh code.
    
    Returns:
    dict: A dictionary containing the central latitude and longitude.
    """
    if len(mesh_code) != 6:
        raise ValueError("Mesh code must be 6 digits for second-level mesh.")
    
    # Extract components from the mesh code
    m = int(mesh_code[0:2])  # Latitude index
    n = int(mesh_code[2:4])  # Longitude index
    p = int(mesh_code[4])    # Row within the mesh
    q = int(mesh_code[5])    # Column within the mesh

    # Define units for calculations
    lat_unit_1st = 2 / 3     # Degrees (40 minutes)
    lon_unit_1st = 1         # Degrees
    lat_unit_2nd = lat_unit_1st / 8  # Degrees
    lon_unit_2nd = lon_unit_1st / 8  # Degrees

    # Calculate base coordinates
    base_lat = m * lat_unit_1st
    base_lon = 100 + n * lon_unit_1st

    # Calculate delta for second-level mesh
    delta_lat = (p + 0.5) * lat_unit_2nd
    delta_lon = (q + 0.5) * lon_unit_2nd

    # Calculate central coordinates
    center_lat = base_lat + delta_lat
    center_lon = base_lon + delta_lon

    return {
        'center_lat': center_lat,
        'center_lon': center_lon
    }

# exec()