from sklearn.metrics.pairwise import cosine_similarity
import math

def exec(input_embedding, embeddings):
    """
    各アイテムと入力embeddingの逆相関を計算し、結果を返す。
    """
    results = []

    for embedding in embeddings:

        # コサイン類似度を計算
        similarity = cosine_similarity([input_embedding], [embedding])[0][0]

        # 必要な情報を格納
        results.append(similarity)

    return results

