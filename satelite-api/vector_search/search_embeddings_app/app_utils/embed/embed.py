import requests
from app_utils import ssm_param

OPENAI_API_EMBED_MODEL = ssm_param.get_param("OPENAI_API_EMBED_MODEL")
OPENAI_API_KEY = ssm_param.get_param("OPENAI_API_KEY")
OPENAI_API_ORGANIZATION_ID = ssm_param.get_param("OPENAI_API_ORGANIZATION_ID")

def exec(input_text):
    result = None
    try:
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            json={
                "model": OPENAI_API_EMBED_MODEL,
                "input": input_text
            },
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Organization": OPENAI_API_ORGANIZATION_ID
            }
        )
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        result = response.json()
        return {'embedding': result.get("data")[0].get("embedding")}
    except Exception as e:
        print("error")
        print(e)
        print(input_text)
        print(result)
        return None
