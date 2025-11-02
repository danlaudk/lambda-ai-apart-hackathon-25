import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import json


def load_data(csv_path, transcript_column="transcript_text"):
    df = pd.read_csv(csv_path)
    return df


def extract_claims(text):
    model_name = "MasterControlAIML/DeepSeek-R1-Qwen2.5-1.5b-SFT-R1-JSON-Unstructured-To-Structured"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
    nlp_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    prompt = f"""
You are a fact extraction assistant. 
From the following YouTube transcript, extract all **factual claims** in **JSON array format**.
Each claim should be concise, self-contained, and written in natural language. 
Do not include opinions or vague statements. Only include factual, verifiable claims.

Transcript:
{text}

Output JSON array of claims:
["""

    result = nlp_pipeline(prompt, max_new_tokens=1024, do_sample=False)[0]['generated_text']

    try:
        claims = json.loads(result[result.find("["):result.rfind("]")+1])
    except:
        claims = re.findall(r'"(.*?)"', result)
    return claims


def embed_claims(claims):
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embed_model.encode(claims)
    return embeddings


def cluster_claims(embeddings, claims, n_clusters=None):
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric='cosine',
        linkage='average'
    )
    labels = clustering.fit_predict(embeddings)
    
    clustered_claims = {}
    for label, claim in zip(labels, claims):
        clustered_claims.setdefault(label, []).append(claim)
    return clustered_claims


def calculate_performance_scores(df):
    # Weighted performance score
    df['performance_score'] = df['view_count'] * 0.6 + df['like_count'] * 0.3 + df['comment_count'] * 0.1
    return df['performance_score'].tolist()


def map_scores_to_clusters(clustered_claims, scores, transcripts):
    cluster_scores = {}
    score_idx = 0
    for label, claims in clustered_claims.items():
        cluster_scores[label] = scores[score_idx]
        score_idx += 1
    return cluster_scores


def generate_wordcloud(clustered_claims, performance_scores):
    weighted_claims = []
    for label, claims in clustered_claims.items():
        weight = int(performance_scores.get(label, 1))
        weighted_claims.extend(claims * weight)
    
    text_for_wc = " ".join(weighted_claims)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_for_wc)
    
    plt.figure(figsize=(15, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


def main(csv_path, transcript_column="transcript_text"):
    df = load_data(csv_path, transcript_column)
    transcripts = df[transcript_column].dropna().tolist()
    performance_scores = calculate_performance_scores(df)
    
    all_claims = []
    for transcript in transcripts:
        claims = extract_claims(transcript)
        all_claims.extend(claims)
    
    embeddings = embed_claims(all_claims)
    clustered_claims = cluster_claims(embeddings, all_claims)
    
    cluster_scores = map_scores_to_clusters(clustered_claims, performance_scores, transcripts)
    
    generate_wordcloud(clustered_claims, performance_scores=cluster_scores)
    return clustered_claims, cluster_scores


if __name__ == "__main__":
    csv_path = "youtube_videos_merged.csv"
    clusters, cluster_scores = main(csv_path, transcript_column="transcript_text")
    print(clusters)
    print(cluster_scores)
