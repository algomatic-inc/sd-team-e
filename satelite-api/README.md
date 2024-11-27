# satelite-api

## 内容
東京全域の3次メッシュをもとに、投票所の候補となる場所を扱うアプリケーション

## ディレクトリ構造
```
/vector_search
├── 投票所をテキスト検索するREST APIのAWS-SAMプロジェクト
/resources
├── メッシュデータ等の入力データ
/rest
├── REST APIの動確用ファイル
/utils
├── Pythonのユーティリティファイル
xxx.py
├── 業務を構成するタスク単位のPythonファイル
main.py
├── 業務を扱うPythonエントリポイント
.env.template
├── 環境変数のテンプレート
├── こいつをベースに.envを作成して環境変数を設定してから利用する
```

## 前提
- Python 3.11
- poetry
- AWS
    - DynamoDB
- OpenAI API KEY
- Google Places API KEY
- ハッカソン運営提供の不動産 API KEY

## setup
```bash
poetry install
```


