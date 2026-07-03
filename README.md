# Embedding Service

## Responsibility

The Embedding Service manages knowledge indexing and similarity-based retrieval for the AI-Aided Consultant Platform.

It is responsible for transforming text and PDF knowledge sources into vector embeddings, storing them in Supabase PostgreSQL with pgvector, and retrieving relevant knowledge chunks based on semantic similarity.

The service supports the RAG pipeline used by the AI Service. When the AI Service needs context for a submitted case, it calls the Embedding Service with a query. The Embedding Service embeds the query, performs vector similarity search, and returns the most relevant text or PDF chunks.

The Embedding Service does not generate final recommendations. Recommendation generation is handled by the AI Service, while the Embedding Service focuses only on indexing, embedding, vector persistence, and retrieval.

## Tech Stack

* FastAPI
* Python
* Hugging Face Inference API
* Sentence Transformer embedding model
* Supabase
* PostgreSQL
* pgvector
* pypdf
* Pydantic
* Swagger / OpenAPI
* Docker / Docker Compose

## Architecture

The Embedding Service follows Clean Architecture principles. The code is separated into the following layers:

* API: exposes HTTP endpoints through FastAPI routers.
* Application: contains use cases and application services for text embedding, PDF embedding, PDF status retrieval, and similarity search.
* Domain: contains entities and interfaces used by the application layer.
* Infrastructure: contains technical implementations such as PDF chunking, text cleaning, Hugging Face embedding generation, and Supabase repositories.

The Application layer depends on abstractions such as `IEmbeddingModel`, `ITextCleaner`, `ITextRepository`, `IPDFRepository`, `IPDFChunker`, and `ISimilarityRepository`.

The Infrastructure layer implements these abstractions using Hugging Face for embedding generation and Supabase PostgreSQL with pgvector for vector storage and similarity search.

Dependency creation is centralized in `api/dependencies.py`, while controllers remain focused on HTTP request and response handling.

## Main Endpoints

| Method | Endpoint                       | Description                                                   |
| ------ | ------------------------------ | ------------------------------------------------------------- |
| `POST` | `/embedding/text`              | Embeds and stores a text knowledge item.                      |
| `POST` | `/embedding/pdf`               | Uploads a PDF, chunks it, embeds its chunks, and stores them. |
| `GET`  | `/embedding/{pdf_id}/status`   | Retrieves the processing status of an uploaded PDF.           |
| `POST` | `/embedding/similarity-search` | Searches for semantically similar text or PDF chunks.         |
| `GET`  | `/health`                      | Returns the health status of the service.                     |

## Main Components

* `embed_text_controller`: exposes the text embedding endpoint.
* `embed_pdf_controller`: exposes PDF upload and PDF status endpoints.
* `similarity_controller`: exposes the semantic similarity search endpoint.
* `api/dependencies.py`: centralizes dependency creation for application services and infrastructure implementations.
* `EmbedTextService`: handles text cleaning, embedding generation, and persistence.
* `EmbedPdfService`: handles PDF chunking, chunk cleaning, embedding generation, and persistence.
* `PdfStatusService`: retrieves the processing status of an uploaded PDF.
* `SimilarityService`: handles query cleaning, query embedding, and similarity search.
* `EmbeddingRecord`: domain entity representing a stored text embedding.
* `SimilarityResult`: domain entity representing a retrieved similarity search result.
* `IEmbeddingModel`: abstraction for embedding generation.
* `ITextCleaner`: abstraction for text cleaning.
* `ITextRepository`: abstraction for text embedding persistence.
* `IPDFRepository`: abstraction for PDF metadata and PDF chunk persistence.
* `IPDFChunker`: abstraction for PDF chunking.
* `ISimilarityRepository`: abstraction for vector similarity search.
* `BasicCleaner`: infrastructure implementation for simple text normalization.
* `PdfChunker`: infrastructure implementation for extracting and chunking PDF text.
* `HFEmbeddingModel`: infrastructure implementation that calls Hugging Face to generate embeddings.
* `SupabaseTextRepository`: Supabase implementation for storing text embeddings.
* `SupabasePdfRepository`: Supabase implementation for storing PDF metadata and chunks.
* `SupabaseSimilarityRepository`: Supabase implementation for calling the vector similarity search RPC.

## Data Flow

### Text Embedding Flow

1. The client sends a `POST /embedding/text` request.
2. The request contains the text to store as reusable knowledge.
3. The controller reads the authenticated user ID from the `X-User-Id` header.
4. The controller calls `EmbedTextService`.
5. `EmbedTextService` cleans the input text using `ITextCleaner`.
6. The cleaned text is sent to `IEmbeddingModel`.
7. `HFEmbeddingModel` calls Hugging Face and receives an embedding vector.
8. The service creates an `EmbeddingRecord` containing the raw text, cleaned text, consultant ID, and embedding.
9. The record is saved using `ITextRepository`.
10. `SupabaseTextRepository` stores the record in the `previous_cases_embeddings` table.
11. The API returns the generated embedding record ID.

### PDF Embedding Flow

1. The client sends a `POST /embedding/pdf` request with a PDF file.
2. The controller validates that the uploaded file is a PDF.
3. The controller reads the authenticated user ID from the `X-User-Id` header.
4. The controller calls `EmbedPdfService`.
5. `EmbedPdfService` creates a PDF metadata record with status `pending`.
6. `PdfChunker` extracts text from the PDF.
7. The extracted text is split into overlapping chunks.
8. Each chunk is cleaned using `ITextCleaner`.
9. Each cleaned chunk is embedded using `IEmbeddingModel`.
10. Each chunk is stored using `IPDFRepository`.
11. `SupabasePdfRepository` stores the chunks in the `pdf_chunks` table.
12. After all chunks are stored successfully, the PDF status is updated to `ready`.
13. If processing fails, the PDF status is updated to `error`.
14. The API returns the generated PDF ID.

### PDF Status Flow

1. The client sends a `GET /embedding/{pdf_id}/status` request.
2. The controller calls `PdfStatusService`.
3. `PdfStatusService` asks `IPDFRepository` for the PDF status.
4. `SupabasePdfRepository` retrieves the status from the `pdf_files` table.
5. If the PDF exists, the API returns its status.
6. If the PDF does not exist, the API returns `404 Not Found`.

### Similarity Search Flow

1. The AI Service or another client sends a `POST /embedding/similarity-search` request.
2. The request contains a query, result limit, search scope, and minimum similarity threshold.
3. The controller reads the authenticated user ID from the `X-User-Id` header.
4. The controller calls `SimilarityService`.
5. `SimilarityService` cleans the query using `ITextCleaner`.
6. The cleaned query is embedded using `IEmbeddingModel`.
7. `SimilarityService` calls `ISimilarityRepository`.
8. `SupabaseSimilarityRepository` calls the `similarity_search` RPC function in Supabase.
9. Supabase compares the query embedding with stored embeddings using pgvector.
10. Results with similarity greater than or equal to the requested threshold are returned.
11. The API returns the most relevant text and PDF chunks.

## RAG Pipeline Role

The Embedding Service represents the retrieval part of the RAG pipeline.

Its responsibilities are:

* indexing reusable knowledge
* extracting PDF text
* chunking documents
* cleaning text
* generating embeddings
* storing vectors
* performing similarity search
* returning relevant context chunks

The AI Service is responsible for using the retrieved context to generate recommendations or draft advice.

The consultant remains responsible for validating, editing, or replacing the generated recommendation before sending the final advice to the user.

## Communication With Other Services

| Service      | Communication Type                | Purpose                                                                                   |
| ------------ | --------------------------------- | ----------------------------------------------------------------------------------------- |
| API Gateway  | HTTP Request / HTTP Header        | Routes external requests and provides authenticated user information through `X-User-Id`. |
| AI Service   | HTTP Request                      | Requests relevant knowledge chunks for RAG-based recommendation generation.               |
| Case Service | HTTP Request | Send validated cases for indexing as reusable experience.                |
| Supabase     | HTTP / PostgREST / RPC            | Stores embeddings, PDF metadata, PDF chunks, and executes vector similarity search.       |
| Hugging Face | HTTP API                          | Generates embedding vectors from text and query content.                                  |

## Database Tables

The service uses Supabase PostgreSQL with pgvector.

### `previous_cases_embeddings`

Stores reusable text knowledge or validated previous cases.

| Column          | Purpose                                         |
| --------------- | ----------------------------------------------- |
| `id`            | Unique identifier of the stored text embedding. |
| `consultant_id` | Owner of the knowledge item.                    |
| `raw_text`      | Original text content.                          |
| `cleaned_text`  | Cleaned version of the text used for embedding. |
| `embedding`     | Vector representation of the cleaned text.      |
| `created_at`    | Creation timestamp.                             |

### `pdf_files`

Stores metadata about uploaded PDF documents.

| Column          | Purpose                                            |
| --------------- | -------------------------------------------------- |
| `id`            | Unique identifier of the PDF file.                 |
| `consultant_id` | Owner of the uploaded PDF.                         |
| `filename`      | Original PDF filename.                             |
| `status`        | Processing status: `pending`, `ready`, or `error`. |
| `created_at`    | Creation timestamp.                                |
| `updated_at`    | Last update timestamp.                             |

### `pdf_chunks`

Stores chunks extracted from uploaded PDF files.

| Column         | Purpose                                     |
| -------------- | ------------------------------------------- |
| `id`           | Unique identifier of the chunk.             |
| `pdf_id`       | Reference to the uploaded PDF file.         |
| `chunk_index`  | Order of the chunk inside the PDF.          |
| `raw_text`     | Original chunk text.                        |
| `cleaned_text` | Cleaned chunk text used for embedding.      |
| `embedding`    | Vector representation of the cleaned chunk. |
| `created_at`   | Creation timestamp.                         |

## Patterns Used

### Clean Architecture

The service separates code into API, Application, Domain, and Infrastructure layers.

This keeps use cases independent from technical details such as FastAPI, Hugging Face, Supabase, and pgvector.

### Repository Pattern

The Application layer depends on repository abstractions instead of depending directly on Supabase.

Examples:

* `ITextRepository`
* `IPDFRepository`
* `ISimilarityRepository`

The Infrastructure layer provides the concrete Supabase implementations.

Examples:

* `SupabaseTextRepository`
* `SupabasePdfRepository`
* `SupabaseSimilarityRepository`

### Adapter Pattern

External systems are wrapped behind internal interfaces.

Examples:

* `HFEmbeddingModel` adapts the Hugging Face API to the `IEmbeddingModel` interface.
* `SupabaseTextRepository` adapts Supabase persistence to the `ITextRepository` interface.
* `SupabaseSimilarityRepository` adapts Supabase RPC calls to the `ISimilarityRepository` interface.

This makes it possible to replace Hugging Face or Supabase later without changing the Application layer.

### Dependency Injection

FastAPI dependencies are centralized in `api/dependencies.py`.

This file creates and provides application services such as:

* `EmbedTextService`
* `EmbedPdfService`
* `PdfStatusService`
* `SimilarityService`

It also creates infrastructure implementations such as:

* `BasicCleaner`
* `PdfChunker`
* `HFEmbeddingModel`
* `SupabaseTextRepository`
* `SupabasePdfRepository`
* `SupabaseSimilarityRepository`

### RAG Retrieval Pattern

The service implements the retrieval side of Retrieval-Augmented Generation.

Stored knowledge is converted into embeddings and saved in a vector database. When a query arrives, the query is embedded and compared with stored vectors. The most similar chunks are returned as context for the AI Service.



## Environment Variables

The Embedding Service uses environment variables to configure external dependencies such as Hugging Face and Supabase.

| Variable               | Purpose                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------- |
| `SUPABASE_URL`         | Base URL of the Supabase project. Example: `https://your-project-ref.supabase.co`.    |
| `SUPABASE_KEY`         | Supabase backend API key. Use a secret key or service role key on the server side.    |
| `HF_TOKEN`             | Hugging Face token used to call the embedding model.                                  |
| `EMBEDDING_MODEL_NAME` | Hugging Face embedding model name. Default: `sentence-transformers/all-MiniLM-L6-v2`. |
| `EMBEDDING_DIMENSION`  | Expected embedding vector dimension. For `all-MiniLM-L6-v2`, use `384`.               |

Example local `.env` file:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_supabase_secret_or_service_role_key

HF_TOKEN=your_huggingface_token
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```


## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the service locally:

```bash
uvicorn main:app --reload
```

By default, the service runs on:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Example Requests

### Embed Text

```http
POST /embedding/text
X-User-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

```json
{
  "text": "This is a previous consultation experience that can be reused later."
}
```

Example response:

```json
{
  "id": "generated-uuid"
}
```

### Upload PDF

```http
POST /embedding/pdf
X-User-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: multipart/form-data
```

Form field:

```text
file: document.pdf
```

Example response:

```json
{
  "pdf_id": "generated-pdf-uuid"
}
```

### Check PDF Status

```http
GET /embedding/{pdf_id}/status
```

Example response:

```json
{
  "status": "ready"
}
```

### Similarity Search

```http
POST /embedding/similarity-search
X-User-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

```json
{
  "query": "The user needs advice about choosing the right software architecture for a project.",
  "k": 10,
  "scope": "both",
  "min_similarity": 0.7
}
```

Example response:

```json
{
  "results": [
    {
      "id": "result-id",
      "source": "pdf",
      "raw_text": "Relevant retrieved context...",
      "pdf_id": "pdf-id",
      "similarity": 0.82
    }
  ]
}
```

