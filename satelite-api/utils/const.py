from dotenv import load_dotenv
import os

load_dotenv()

# GOOGLE API 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_URL = "https://places.googleapis.com/v1/places:searchNearby"  # 適切なAPI URLを指定
GOOGLE_API_RADIUS = 10000
GOOGLE_API_REQUEST_COUNT = 10
GOOGLE_API_INCLUDED_TYPES = {
    "station": ["subway_station", "train_station"],
    "shopping": ["department_store", "shopping_mall"]
}

GOOGLE_API_MAX_THROTTLING_SIZE = 10
GOOGLE_API_DELAY_BETWEEN_BATCHES = 5
GOOGLE_API_FIELD_MASK = "places.name,places.formattedAddress,places.location,places.displayName,places.plusCode,places.primaryTypeDisplayName,places.addressComponents,places.rating,places.plusCode,places.reviews,places.photos,places.accessibilityOptions,places.restroom,places.parkingOptions"

# ORG API
ORG_API_URL = "https://ty665ls8s5.execute-api.ap-northeast-1.amazonaws.com/prod/get-estate-info"
ORG_API_MAX_THROTTLING_SIZE = 5
ORG_API_DELAY_BETWEEN_BATCHES = 5
ORG_API_KEY = os.getenv("ORG_API_KEY")

# OPENAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORGANIZATION_ID = os.getenv("OPENAI_ORGANIZATION_ID")
OPENAI_PLACE_REVIEW_MODEL = "gpt-4o-mini"
OPENAI_API_MAX_THROTTLING = 10
OPENAI_API_DELAY = 5
OPENAI_API_EMBED_MODEL = "text-embedding-3-small"
OPENAI_APIEMBED_MAX_THROTTLING = 10
OPENAI_API_EMBED_DELAY = 2

# DYNAMODB
DYNAMODB_LOCATION_TABLE_NAME = "location"

# FILE
# 各モジュールでディレクトリ操作が競合しないようにファイル名はモジュール外で管理
OUTPUT_DIR = "output/"
MESH_3_FILE = "resources/tokyo-mesh/13.csv"
MESH_3_TO_2_OUTPUT_FILE = "resources/tokyo-mesh/13-2.csv"
MESH_2_TO_LAT_LNG_OUTPUT_FILE = "resources/tokyo-mesh/13-2-lat-lng.csv"
GOOGLE_API_OUTPUT_DIR= f"{OUTPUT_DIR}google-locations/apis/"
GOOGLE_API_LAT_LNG_OUTPUT_DIR = f"{OUTPUT_DIR}google-locations/lat-lng/"
ORG_API_OUTPUT_DIR = f"{OUTPUT_DIR}org-locations/apis/"
MERGED_GOOGLE_ORG_OUTPUT_DIR = f"{OUTPUT_DIR}merged-locations/google-org/"
MERGED_GOOGLE_ORG_OUTPUT_BASENAME = "merged.json"
ORG_ONLY_OUTPUT_BASENAME = "org-only.json"
GOOGLE_ONLY_OUTPUT_BASENAME = "google-only.json"
FILTERED_MERGED_GOOGLE_ORG_OUTPUT_DIR = f"{OUTPUT_DIR}filtered-merged-locations/google-org/"
FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME = "valid.json"
FILTERED_INVALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME = "invalid.json"
FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_FILE = f"{FILTERED_MERGED_GOOGLE_ORG_OUTPUT_DIR}/{FILTERED_VALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME}"
FILTERED_INVALID_MERGED_GOOGLE_ORG_OUTPUT_FILE = f"{FILTERED_MERGED_GOOGLE_ORG_OUTPUT_DIR}/{FILTERED_INVALID_MERGED_GOOGLE_ORG_OUTPUT_BASENAME}"