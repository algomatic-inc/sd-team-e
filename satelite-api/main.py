from merge_google_org_locations import exec as merge_google_org_locations
from write_locations_to_db import exec as write_locations_to_db
from mesh_3_to_2 import exec as mesh_3_to_2
from get_google_locations import exec as get_google_locations
from get_org_locations import exec as get_org_locations
from google_to_lat_lng import exec as google_to_lat_lng
from mesh_to_lat_lng import exec as mesh_to_lat_lng
from filter_google_org_locations import exec as filter_google_org_locations
from utils.const import MESH_3_FILE, MESH_2_TO_LAT_LNG_OUTPUT_FILE, GOOGLE_API_OUTPUT_DIR, GOOGLE_API_LAT_LNG_OUTPUT_DIR, MERGED_GOOGLE_ORG_OUTPUT_BASENAME, FILTERED_MERGED_GOOGLE_ORG_OUTPUT_DIR, ORG_API_OUTPUT_DIR, MESH_3_TO_2_OUTPUT_FILE, MERGED_GOOGLE_ORG_OUTPUT_DIR, FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_FILE
from clear_location_db import exec as clear_location_db
from utils.llm.review_locations import test as review_locations
from write_reviews_to_db import exec as write_reviews_to_db
from utils.llm.embed_locations import test as embed_locations
from write_embeddings_to_db import exec as write_embeddings_to_db

def exec():
    # 3階層のメッシュを2階層に変換 
    # mesh_3_to_2(MESH_3_FILE, MESH_3_TO_2_OUTPUT_FILE)

    # # メッシュをlat, lngに変換
    # mesh_to_lat_lng(MESH_3_TO_2_OUTPUT_FILE, MESH_2_TO_LAT_LNG_OUTPUT_FILE)
    
    # # Google APIの呼び出し
    # get_google_locations(MESH_2_TO_LAT_LNG_OUTPUT_FILE, GOOGLE_API_OUTPUT_DIR)

    # # # Google APIの呼び出し結果をlat, lngに変換
    google_to_lat_lng(GOOGLE_API_OUTPUT_DIR, GOOGLE_API_LAT_LNG_OUTPUT_DIR)

    # # # 不動産APIの呼び出し   
    # get_org_locations(GOOGLE_API_LAT_LNG_OUTPUT_DIR, ORG_API_OUTPUT_DIR)

    # # apiの呼び出し結果をマージ
    # merge_google_org_locations(GOOGLE_API_OUTPUT_DIR, ORG_API_OUTPUT_DIR, MERGED_GOOGLE_ORG_OUTPUT_DIR)
    
    # # # # マージ結果をフィルタリング
    # filter_google_org_locations(f"{MERGED_GOOGLE_ORG_OUTPUT_DIR}{MERGED_GOOGLE_ORG_OUTPUT_BASENAME}", FILTERED_MERGED_GOOGLE_ORG_OUTPUT_DIR)

    # # db書き込み
    write_locations_to_db(f"{FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_FILE}")

def update_db():
    # dynamoのデータに計算処理を行う
    # write_reviews_to_db()
    write_embeddings_to_db()

def option_exec():
    # TODO google apiのresponseにplaceがないものを抜き出してretryできるようにrequestを作成
    # TODO orgも同様
    # オプション
    # # dbの全アイテムを削除
    clear_location_db()

update_db()


# exec()
# review_locations()
# embed_locations()