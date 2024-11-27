# vector_search

## 内容
テキストで投票所候補を検索するREST APIを提供するAWS SAMアプリケーション

## 前提
- docker
- vscode devcontainer拡張
- aws sam cli
- AWS
    - SSMパラメータストア   
    - DynamoDB
- OpenAI API KEY

## ファイル構成
- .devcontainer devcontainerの設定ファイル
- template.yaml aws samのテンプレートファイル
- docker-compose.yaml docker composeの設定ファイル  
- search-embeddings-app アプリケーションのpythonコード
    - app.py アプリケーションのエントリーポイント
    - requirements.txt アプリケーションの依存ライブラリ
    - Dockerfile アプリケーションのDockerfile
    - app_utils/ アプリケーションのユーティリティ関数群

## デプロイ

```bash
sam build
sam deploy --guided
```

