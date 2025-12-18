from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from engine.utils.preprocessing import preprocess
import pandas as pd
import torch

def detect_duplicates(df):
    """
    Detects duplicate and near-duplicate posts.

    Returns:
        duplicate_post_ids : set[int]
        similarity_matrix  : np.ndarray
        clusters_df        : pd.DataFrame (post_id, cluster_id)
    """

    df = df.copy()

    # Preprocess
    df["clean_text"] = df["text"].apply(preprocess)

    # Embeddings
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    embeddings = model.encode(df["clean_text"].tolist())

    similarity_matrix = cosine_similarity(embeddings)

    # Threshold
    threshold = 0.85

    duplicate_post_ids = set()
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i][j] >= threshold:
                duplicate_post_ids.add(df.iloc[i]["post_id"])
                duplicate_post_ids.add(df.iloc[j]["post_id"])

    # Clustering
    distance_matrix = 1 - similarity_matrix
    clustering = AgglomerativeClustering(
        n_clusters=None,
        metric="precomputed",
        linkage="complete",
        distance_threshold=1 - threshold,
    )

    df["cluster_id"] = clustering.fit_predict(distance_matrix)

    clusters_df = df[["post_id", "cluster_id"]]

    return duplicate_post_ids, similarity_matrix, clusters_df
