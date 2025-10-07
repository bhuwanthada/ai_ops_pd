from chromadb.utils import embedding_functions
from google.cloud import aiplatform
import vertexai.preview
import chromadb
import os
from google import genai
from google.genai.types import EmbedContentConfig


GOOGLE_CLOUD_PROJECT="wayfair-test-378605"
GOOGLE_CLOUD_LOCATION="global"
GOOGLE_GENAI_USE_VERTEXAI=True



client = genai.Client(vertexai=GOOGLE_GENAI_USE_VERTEXAI,project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=[
        "How do I get a driver's license/learner's permit?",
        "How long is my driver's license valid for?",
        "Driver's knowledge test study guide",
    ],
    config=EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",  # Optional
        output_dimensionality=3072,  # Optional
        title="Driver's License",  # Optional
    ),
)
print(response.embeddings)
# Example response:
# embeddings=[ContentEmbedding(values=[-0.06302902102470398, 0.00928034819662571, 0.014716853387653828, -0.028747491538524628, ... ],
# statistics=ContentEmbeddingStatistics(truncated=False, token_count=13.0))]
# metadata=EmbedContentMetadata(billable_character_count=112)