import boto3

def get_param(name):
    # SSM クライアントを作成
    ssm = boto3.client('ssm', region_name='ap-northeast-1')

    # パラメータを取得
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=False  # パラメータが暗号化されている場合に True に設定
    )

    # パラメータの値を取得
    parameter_value = response['Parameter']['Value']

    return parameter_value