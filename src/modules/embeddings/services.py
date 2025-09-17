import os
from uuid import UUID
from typing import List
import torch
from fastapi import BackgroundTasks
from pymilvus import Collection

from src.modules.embeddings.dto import GeneratePostEmbeddingsPayload
from src.modules.embeddings.repository import PostEmbeddingsRepository
from src.modules.embeddings.schemas import PostForEmbedding, PostMediaForEmbedding
from src.modules.jobs.services import add_job, update_job_status
from src.modules.jobs.schemas import JobStatus, AddJob, UpdateJobStatus
from src.modules.db_milvus.repository import MilvusRepository
from src.shared.llm.openai_embedder import OpenAIEmbedder


async def create_embedding_collection(collection_name: str):
    # Create Milvus collection for post embeddings (assuming 1024-dimensional embeddings)
    MilvusRepository.create_collection(collection_name, 1024)


async def store_embeddings_in_milvus(collection_name: str, psql_ids: List[UUID], embeddings: torch.Tensor):
    # Connect to Milvus
    MilvusRepository._connect()
    try:
        # Get the collection
        collection = Collection(
            name=collection_name,
            using="milvus_ops"
        )

        # Insert the embeddings in batch
        collection.insert([
            [str(psql_id) for psql_id in psql_ids],  # psql_ids as varchar
            [embedding.tolist() for embedding in embeddings]  # embeddings as float vectors
        ])

        # Flush to make sure data is persisted
        collection.flush()
    finally:
        MilvusRepository._disconnect()


async def process_post_items(post_items: List[PostForEmbedding], embedder: OpenAIEmbedder, collection_name: str):
    try:
        # Prepare data for batch processing
        texts_to_embed = []
        valid_post_items = []

        # Process each post to get combined text
        for post_item in post_items:
            # Get media for this post
            media_items = await PostEmbeddingsRepository.get_media_for_post(post_item.post_id)

            # Combine post text with media descriptions
            combined_text = ""

            # Add post text if available
            if post_item.post_text:
                combined_text += post_item.post_text + " "

            # Add descriptions from media
            for media_item in media_items:
                if media_item.description:
                    combined_text += media_item.description + " "

            # Only process if we have text to embed
            if combined_text.strip():
                texts_to_embed.append(combined_text.strip())
                valid_post_items.append(post_item)

        # If we have texts to embed
        if texts_to_embed:
            print(f"Received request to embed multiple: {len(texts_to_embed)} items")
            # Generate embeddings in batch
            embeddings = embedder.get_embedding(texts_to_embed)

            # Store embeddings in Milvus in batch
            psql_ids = [post_item.post_id for post_item in valid_post_items]
            await store_embeddings_in_milvus(collection_name, psql_ids, embeddings)
    except Exception as e:
        print(f"Warning: Error processing batch of posts: {e}")
        # Process individually as fallback
        for post_item in post_items:
            try:
                await process_single_post_item(post_item, embedder, collection_name)
            except Exception as single_e:
                print(f"Warning: Error processing post {post_item.post_id}: {single_e}")


async def process_single_post_item(post_item: PostForEmbedding, embedder: OpenAIEmbedder, collection_name: str):
    """Process a single post item for embedding"""
    try:
        # Get media for this post
        media_items = await PostEmbeddingsRepository.get_media_for_post(post_item.post_id)

        # Combine post text with media descriptions
        combined_text = ""

        # Add post text if available
        if post_item.post_text:
            combined_text += post_item.post_text + " "

        # Add descriptions from media
        for media_item in media_items:
            if media_item.description:
                combined_text += media_item.description + " "

        # If we have text to embed
        if combined_text.strip():
            # Generate embedding
            embedding = embedder.get_embedding([combined_text.strip()])

            # Store in Milvus
            await store_embeddings_in_milvus(collection_name, [post_item.post_id], embedding)
    except Exception as e:
        print(f"Warning: Error processing post {post_item.post_id}: {e}")


async def background_process_by_export(export_id: UUID, model_name: str, job_id: UUID, collection_name: str):
    # Update job status to in progress
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.IN_PROGRESS))

    # Initialize embedder
    embedder = OpenAIEmbedder(model_name=model_name)

    # Create Milvus collection
    await create_embedding_collection(collection_name)

    # Process posts in batches
    page_size = 100  # Process 100 posts at a time
    embedding_batch_size = 32  # Process embeddings in batches of 32
    page = 0

    while True:
        posts_to_process = await PostEmbeddingsRepository.get_posts_for_embedding_by_export_id(
            export_id, page_size, page * page_size
        )

        if not posts_to_process:
            break

        # Process posts in embedding batches
        for i in range(0, len(posts_to_process), embedding_batch_size):
            batch = posts_to_process[i:i + embedding_batch_size]
            await process_post_items(batch, embedder, collection_name)

        if len(posts_to_process) < page_size:
            break

        page += 1

    # Update job status to completed
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.COMPLETED))

    print(f"Finished background processing for export: {export_id}")


async def start_post_embedding_generation_by_export(
    export_id: UUID,
    payload: GeneratePostEmbeddingsPayload,
    background_tasks: BackgroundTasks
):
    # Create a job for tracking this background process
    job_metadata = f"Generate embeddings for posts in export {export_id}"
    job = await add_job(AddJob(status=JobStatus.PENDING, metadata=job_metadata))

    # Create a unique collection name based on export_id
    collection_name = f"post_embeddings_{str(export_id).replace('-', '_')}"

    background_tasks.add_task(
        background_process_by_export,
        export_id,
        payload.model_name,
        job.id,
        collection_name
    )
