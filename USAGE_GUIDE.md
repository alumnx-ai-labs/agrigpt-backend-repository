# Multimodal RAG Service - Usage Guide

## Quick Start

### 1. Install Dependencies

Make sure you have all required packages installed:

```bash
pip install -r requirements.txt
```

Key dependencies for multimodal support:
- `torch` - PyTorch for CLIP model
- `transformers` - Hugging Face transformers library
- `PyMuPDF` (fitz) - PDF and image extraction
- `pillow` - Image processing
- `pinecone-client` - Vector database

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-chatbot-index
GOOGLE_API_KEY=your_google_api_key  # For LLM (Gemini)
```

### 3. Run the Service

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Key Features

### Multimodal Processing
- **Text Extraction**: Extracts and chunks text from PDF pages
- **Image Extraction**: Extracts images from PDF pages (filters out small logos/icons)
- **Separate Embeddings**: Creates CLIP embeddings separately for text and images
- **Unified Storage**: Stores both text and image embeddings in the same Pinecone index

### Cross-Modal Retrieval
- Text queries can retrieve both text chunks and images
- All embeddings are in the same 512-dimensional space
- Results include page numbers for easy reference

## API Endpoints

### 1. Upload PDF
```bash
POST /upload-pdf
Content-Type: multipart/form-data

file: <pdf_file>
```

**Response:**
```json
{
  "message": "PDF processed successfully. Added 15 text chunks and 3 images to knowledge base.",
  "filename": "document.pdf",
  "text_chunks": 15,
  "images": 3,
  "total_vectors": 18
}
```

### 2. Chat/Query
```bash
POST /chat
Content-Type: application/json

{
  "query": "What are the main agricultural practices mentioned?",
  "chat_history": []
}
```

**Response:**
```json
{
  "response": "Based on the documents, the main practices include...",
  "sources": [
    "document.pdf - Page 5, Chunk 1",
    "document.pdf - Page 7, Image: document_page7_img1.png"
  ]
}
```

### 3. Health Check
```bash
GET /health
```

### 4. Clear Knowledge Base
```bash
DELETE /clear-knowledge-base
```

## How It Works

### PDF Processing Flow

1. **PDF Loading**: Uses PyMuPDF to open the PDF
2. **Page-by-Page Processing**:
   - Extract text from each page
   - Extract images from each page (size filter: min 100x100)
   - Maintain page number metadata

3. **Text Processing**:
   - Split text into chunks (1000 chars, 200 overlap)
   - Generate CLIP text embeddings (512-dim)
   - Store with metadata: `content_type="text"`, `page_number`, etc.

4. **Image Processing**:
   - Save images temporarily
   - Generate CLIP image embeddings (512-dim)
   - Store with metadata: `content_type="image"`, `page_number`, `image_path`, etc.
   - Clean up temporary files

5. **Vector Storage**:
   - Upload to Pinecone in batches (100 vectors per batch)
   - All vectors in same index with dimension 512

### Query Flow

1. **Query Embedding**: Convert user query to CLIP text embedding
2. **Vector Search**: Search Pinecone for top-k similar vectors
3. **Result Formatting**: Format results with content type and page numbers
4. **LLM Generation**: Pass context to Gemini LLM for answer generation
5. **Source Attribution**: Return sources with page numbers

## Metadata Structure

### Text Chunks
```python
{
    "content_type": "text",
    "source": "document.pdf",
    "pdf_name": "document",
    "page_number": 5,
    "chunk": 2,
    "text": "chunk content...",
    "total_pages": 20
}
```

### Images
```python
{
    "content_type": "image",
    "source": "document.pdf",
    "pdf_name": "document",
    "page_number": 5,
    "image_index": 1,
    "image_path": "/tmp/.../document_page5_img1.png",
    "image_filename": "document_page5_img1.png",
    "image_size": "800x600",
    "page_text": "surrounding text context...",
    "total_pages": 20
}
```

## Advanced Usage

### Filter by Content Type

You can modify the `query` method to filter results:

```python
# Only retrieve text chunks
answer, sources = await rag_service.query(
    query="your question",
    content_type="text"
)

# Only retrieve images
answer, sources = await rag_service.query(
    query="your question",
    content_type="image"
)

# Retrieve both (default)
answer, sources = await rag_service.query(
    query="your question"
)
```

### Direct Vector Operations

You can also interact with Pinecone directly:

```python
# Query with custom parameters
query_embedding = rag_service.generate_text_embedding("your query")
results = rag_service.vectorstore.query(
    vector=query_embedding,
    top_k=10,
    filter={"content_type": "image"}  # Filter to images only
)
```

## Troubleshooting

### CLIP Model Download
- First run will download ~500MB model
- Ensure internet connection
- Model cached in `~/.cache/huggingface/`

### Image Extraction Issues
- Small images (<100x100) are filtered out
- Some PDFs may have embedded images that can't be extracted
- Check logs for extraction errors

### Pinecone Index
- Index dimension must be 512 (CLIP dimension)
- If you have an existing 768-dim index, create a new one
- Index name configurable via `PINECONE_INDEX_NAME` env var

### Memory Usage
- CLIP model loads into memory (CPU or GPU)
- Large PDFs with many images may use significant memory
- Consider batch processing for very large documents

## Performance Tips

1. **GPU Acceleration**: CLIP runs faster on GPU if available
2. **Batch Processing**: Images processed in batches for efficiency
3. **Caching**: CLIP model cached after first load
4. **Index Optimization**: Use appropriate Pinecone index type for your scale

## Next Steps

- Add image query support (query with uploaded images)
- Implement hybrid search (combine multiple query types)
- Add result ranking/filtering options
- Optimize for large-scale document processing

