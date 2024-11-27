import json
import boto3
from app_utils import lambda_app_logger
from app_utils import search_place_by_text

logger = lambda_app_logger.get_logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    query_params = event.get("queryStringParameters", {})
    input_text = query_params.get("input_text", "投票率が低いところ")
    count = int(query_params.get("count", 5))
    places = search_place_by_text.exec(input_text, count)

    response = {
        "statusCode": 200,
        "body": json.dumps({"Items": places}, ensure_ascii=False),
    }
    logger.info(
        "Response to client",
        extra={"response": response},
    )
    return response

# event = {
#     "queryStringParameters": {
#         "input_text": "大田区で駅に近いところ",
#         "count": 5
#     }
# }

# lambda_handler(event, {})
