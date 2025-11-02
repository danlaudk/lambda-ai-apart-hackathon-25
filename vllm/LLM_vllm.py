import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import json


# Initialize vLLM client (pointing to local server)
vllm_client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM doesn't require authentication
)

MODEL_NAME = "MasterControlAIML/DeepSeek-R1-Qwen2.5-1.5b-SFT-R1-JSON-Unstructured-To-Structured"


def load_data(csv_path, transcript_column="transcript_text"):
    df = pd.read_csv(csv_path)
    return df


def extract_claims(text):
    """
    Extract factual claims from text using vLLM server.
    Much faster than loading the model in Python!
    """
    prompt = f"""
You are a fact extraction assistant. 
From the following YouTube transcript, extract all **factual claims** in **JSON array format**.
Each claim should be concise, self-contained, and written in natural language. 
Do not include opinions or vague statements. Only include factual, verifiable claims.

Transcript:
{text}

Output JSON array of claims:
["""

    try:
        # Make request to vLLM server
        response = vllm_client.completions.create(
            model=MODEL_NAME,
            prompt=prompt,
            max_tokens=1024,
            temperature=0.0
        )
        
        result = response.choices[0].text
        
        # Parse JSON from result
        try:
            claims = json.loads("[" + result[:result.rfind("]")+1])
        except:
            # Fallback: extract quoted strings
            claims = re.findall(r'"(.*?)"', result)
        
        return claims
    
    except Exception as e:
        print(f"Error extracting claims: {e}")
        print("Make sure vLLM server is running:")
        print("  cd /lambda/nfs/newinstance/vllm")
        print("  ./start_vllm_server.sh")
        return []


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
    
    print(f"Processing {len(transcripts)} transcripts...")
    
    all_claims = []
    for i, transcript in enumerate(transcripts):
        print(f"Extracting claims from transcript {i+1}/{len(transcripts)}...")
        claims = extract_claims(transcript)
        all_claims.extend(claims)
        print(f"  Found {len(claims)} claims")
    
    print(f"\nTotal claims extracted: {len(all_claims)}")
    
    if not all_claims:
        print("No claims extracted. Exiting.")
        return {}, {}
    
    print("Embedding claims...")
    embeddings = embed_claims(all_claims)
    
    print("Clustering claims...")
    clustered_claims = cluster_claims(embeddings, all_claims)
    
    cluster_scores = map_scores_to_clusters(clustered_claims, performance_scores, transcripts)
    
    print("Generating word cloud...")
    generate_wordcloud(clustered_claims, performance_scores=cluster_scores)
    
    return clustered_claims, cluster_scores


if __name__ == "__main__":
    csv_path = "../ai_assessment_dora/youtube_videos_merged.csv"
    
    print("="*80)
    print("YouTube Transcript Claim Extraction (vLLM Version)")
    print("="*80)
    print("\nMake sure vLLM server is running before starting!")
    print("If not, run: cd /lambda/nfs/newinstance/vllm && ./start_vllm_server.sh")
    print("="*80 + "\n")
    
    clusters, cluster_scores = main(csv_path, transcript_column="transcript_text")
    
    print("\n" + "="*80)
    print("Results:")
    print("="*80)
    print(f"\nNumber of clusters: {len(clusters)}")
    for label, claims in list(clusters.items())[:3]:  # Show first 3 clusters
        print(f"\nCluster {label} ({len(claims)} claims):")
        for claim in claims[:5]:  # Show first 5 claims per cluster
            print(f"  - {claim}")
    
    print("\n" + "="*80)
