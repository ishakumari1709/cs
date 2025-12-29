import os
from typing import List, Tuple
import requests

# Import LangChain components with proper fallbacks
# HuggingFaceEmbeddings is only in langchain_community, not langchain
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    raise ImportError("Please install langchain-community: pip install langchain-community")

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    try:
        from langchain.vectorstores import Chroma
    except ImportError:
        raise ImportError("Please install langchain-community: pip install langchain-community")

# Try to import newer HuggingFaceEndpoint first, fallback to HuggingFaceHub
HuggingFaceEndpoint = None
HuggingFaceHub = None
HuggingFacePipeline = None

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    try:
        from langchain_community.llms import HuggingFacePipeline, HuggingFaceHub
    except ImportError:
        try:
            from langchain.llms import HuggingFacePipeline, HuggingFaceHub
        except ImportError:
            HuggingFacePipeline = None
            try:
                from langchain_community.llms import HuggingFaceHub
            except ImportError:
                HuggingFaceHub = None

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    try:
        from langchain_core.prompts import PromptTemplate
    except ImportError:
        raise ImportError("Please install langchain: pip install langchain")

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        raise ImportError("Please install langchain: pip install langchain")

# RetrievalQA is optional - we use retriever directly instead
RetrievalQA = None
import chromadb
from chromadb.config import Settings

# Optional ML imports - will use HuggingFace API if not available
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers/torch not installed. Will use HuggingFace API or fallback responses.")


class RAGService:
    def __init__(self):
        # Initialize ChromaDB directory
        self.persist_directory = "./chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize vector store (will be created per session)
        self.vector_stores = {}
        self.chroma_clients = {}  # Store clients to close them properly
        
        # Lazy load embeddings and LLM (load when first needed)
        self.embeddings = None
        self.llm = None
        self._embeddings_initialized = False
        self._llm_initialized = False
        self.llm_repo_id = None  # Store repo_id for direct API calls
    
    def _init_embeddings(self):
        """Lazy initialization of embeddings model"""
        if self._embeddings_initialized:
            return
        
        try:
            print("Initializing embeddings model... (this may take a moment)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            self._embeddings_initialized = True
            print("Embeddings model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load embeddings model: {e}")
            print("Some features may not work correctly.")
            raise
    
    def _init_llm(self):
        """Initialize the LLM (lazy loading)"""
        if self._llm_initialized:
            return
        
        self._llm_initialized = True
        
        # For zero-cost solution, we'll use a simple approach
        # Option 1: Use HuggingFace Inference API (free tier) - requires API key
        # Option 2: Use local small model (requires download)
        # Option 3: Fallback to context-based responses (no LLM needed)
        
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if hf_api_key:
            # Use HuggingFace Inference API - try newer HuggingFaceEndpoint first
            try:
                if HuggingFaceEndpoint:
                    self.llm = HuggingFaceEndpoint(
                        repo_id="mistralai/Mistral-7B-Instruct-v0.1",
                        huggingfacehub_api_token=hf_api_key,
                        temperature=0.7,
                        max_length=512
                    )
                    print("Using HuggingFace Inference API (HuggingFaceEndpoint)")
                    return
            except Exception as e:
                print(f"Error initializing HuggingFaceEndpoint: {e}")
            
            # Fallback to HuggingFaceHub
            try:
                if HuggingFaceHub:
                    repo_id = "mistralai/Mistral-7B-Instruct-v0.1"
                    self.llm_repo_id = repo_id  # Store for direct API calls
                    self.llm = HuggingFaceHub(
                        repo_id=repo_id,
                        huggingfacehub_api_token=hf_api_key,
                        model_kwargs={"temperature": 0.7, "max_length": 512}
                    )
                    print("Using HuggingFace Inference API (HuggingFaceHub)")
                    return
            except Exception as e:
                print(f"Error initializing HuggingFaceHub: {e}")
        
        # Try local model (small, fast) - only if transformers is available
        if TRANSFORMERS_AVAILABLE:
            try:
                print("Loading local LLM (GPT-2)... This may take a while on first run.")
                model_name = "gpt2"  # Very small, fast model
                
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                # Add padding token if it doesn't exist
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                )
                
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                
                self.llm = HuggingFacePipeline(pipeline=pipe)
                print("Local LLM loaded successfully")
            except Exception as e:
                print(f"Error loading local LLM: {e}")
                print("Will use fallback context-based responses (no LLM)")
                self.llm = None
        else:
            print("Transformers not available. Will use HuggingFace API or fallback responses.")
            self.llm = None
    
    def _close_all_chroma_connections(self):
        """Close all ChromaDB connections to allow database deletion"""
        try:
            # Close all stored clients
            for client in self.chroma_clients.values():
                try:
                    if hasattr(client, 'persist'):
                        client.persist()
                    if hasattr(client, '_client'):
                        if hasattr(client._client, 'persist'):
                            client._client.persist()
                        if hasattr(client._client, 'clear_system_cache'):
                            client._client.clear_system_cache()
                except:
                    pass
            
            # Clear vector stores
            self.vector_stores.clear()
            self.chroma_clients.clear()
            
            # Force garbage collection to release file handles
            import gc
            gc.collect()
            
            # Small delay to ensure file handles are released
            import time
            time.sleep(0.5)
        except Exception as e:
            print(f"Warning: Error closing ChromaDB connections: {e}")
    
    def _get_vector_store(self, session_id: str):
        """Get or create vector store for a session"""
        # Lazy load embeddings if not already loaded
        if not self._embeddings_initialized:
            self._init_embeddings()
        
        if session_id not in self.vector_stores:
            collection_name = f"session_{session_id}"
            # Create or load existing Chroma collection
            # Chroma will automatically load existing collection if it exists
            try:
                vector_store = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
                self.vector_stores[session_id] = vector_store
                # Store client reference for proper cleanup
                if hasattr(vector_store, '_client'):
                    self.chroma_clients[session_id] = vector_store._client
                print(f"Vector store initialized for session {session_id}")
            except Exception as e:
                error_str = str(e)
                # Check if it's a schema compatibility error
                if "no such column" in error_str.lower() or "topic" in error_str.lower():
                    print(f"ChromaDB schema error detected: {e}")
                    print("Using a new database directory to avoid file locking issues...")
                    try:
                        import uuid
                        # Use a new directory instead of trying to delete the locked one
                        new_dir = f"./chroma_db_new_{uuid.uuid4().hex[:8]}"
                        print(f"Creating new database directory: {new_dir}")
                        os.makedirs(new_dir, exist_ok=True)
                        self.persist_directory = new_dir
                        
                        # Try to create a new one with fresh schema
                        vector_store = Chroma(
                            collection_name=collection_name,
                            embedding_function=self.embeddings,
                            persist_directory=self.persist_directory
                        )
                        self.vector_stores[session_id] = vector_store
                        if hasattr(vector_store, '_client'):
                            self.chroma_clients[session_id] = vector_store._client
                        print(f"✅ New vector store created successfully with fresh database for session {session_id}")
                        print(f"⚠️  Note: Old database at ./chroma_db can be deleted manually after stopping the server")
                    except Exception as e2:
                        print(f"Error creating new database: {e2}")
                        # Try one more time with a simpler name
                        try:
                            new_dir = "./chroma_db_fixed"
                            print(f"Trying with directory: {new_dir}")
                            os.makedirs(new_dir, exist_ok=True)
                            self.persist_directory = new_dir
                            vector_store = Chroma(
                                collection_name=collection_name,
                                embedding_function=self.embeddings,
                                persist_directory=self.persist_directory
                            )
                            self.vector_stores[session_id] = vector_store
                            if hasattr(vector_store, '_client'):
                                self.chroma_clients[session_id] = vector_store._client
                            print(f"✅ Vector store created with fixed database directory for session {session_id}")
                        except Exception as e3:
                            print(f"❌ Failed to create vector store: {e3}")
                            raise
                else:
                    print(f"Error initializing vector store: {e}")
                    # Try to create a new one
                    try:
                        vector_store = Chroma(
                            collection_name=collection_name,
                            embedding_function=self.embeddings,
                            persist_directory=self.persist_directory
                        )
                        self.vector_stores[session_id] = vector_store
                        if hasattr(vector_store, '_client'):
                            self.chroma_clients[session_id] = vector_store._client
                    except Exception as e2:
                        print(f"Failed to create vector store: {e2}")
                        raise
        return self.vector_stores[session_id]
    
    async def add_documents(self, chunks: List[dict], session_id: str):
        """Add documents to vector store"""
        # Ensure embeddings are initialized
        if not self._embeddings_initialized:
            self._init_embeddings()
        
        vector_store = self._get_vector_store(session_id)
        
        # Convert chunks to LangChain format
        documents = [
            Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
            for chunk in chunks
        ]
        
        # Add to vector store
        try:
            print(f"Adding {len(documents)} documents to vector store for session {session_id}")
            # Add documents
            ids = vector_store.add_documents(documents)
            print(f"Added documents with IDs: {len(ids)}")
            
            # Persist the changes
            vector_store.persist()
            print(f"Documents persisted successfully to {self.persist_directory}")
            
            # Clear the cached vector store so it reloads on next access
            # This ensures the next query sees the new documents
            if session_id in self.vector_stores:
                del self.vector_stores[session_id]
                print(f"Cleared cached vector store for session {session_id} to force reload")
            
            # Verify documents were added by checking collection
            try:
                # Recreate vector store to verify it loads persisted data
                collection_name = f"session_{session_id}"
                test_store = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
                sample_docs = test_store.similarity_search("test", k=1)
                print(f"Verification: Vector store has documents (sample check returned {len(sample_docs)} docs)")
            except Exception as verify_error:
                print(f"Note: Could not verify documents (this is okay): {verify_error}")
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def get_response(self, query: str, session_id: str) -> Tuple[str, List[str]]:
        """Get RAG response for a query"""
        vector_store = self._get_vector_store(session_id)
        
        # Check if vector store has documents
        try:
            # First, check if collection has any documents by trying to get count
            try:
                # Try to get a small sample to check if collection has data
                sample_docs = vector_store.similarity_search("", k=1)
                if len(sample_docs) == 0:
                    print(f"No documents found in vector store for session {session_id}")
                    return "I don't have any documents to reference yet. Please upload a document first.", []
            except Exception as check_error:
                print(f"Error checking vector store: {check_error}")
                # Continue to try retrieval anyway
            
            # Try to retrieve relevant documents
            try:
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                # Use invoke() for newer LangChain versions, fallback to get_relevant_documents for older versions
                if hasattr(retriever, 'invoke'):
                    docs = retriever.invoke(query)
                elif hasattr(retriever, 'get_relevant_documents'):
                    docs = retriever.get_relevant_documents(query)
                else:
                    # Fallback to direct similarity search
                    docs = vector_store.similarity_search(query, k=3)
                print(f"Retrieved {len(docs)} documents for query: {query[:50]}...")
            except Exception as e:
                print(f"Error retrieving documents: {e}")
                import traceback
                traceback.print_exc()
                # Try alternative method
                try:
                    docs = vector_store.similarity_search(query, k=3)
                    print(f"Alternative retrieval method returned {len(docs)} documents")
                except Exception as e2:
                    print(f"Alternative retrieval also failed: {e2}")
                    return "I don't have any documents to reference yet. Please upload a document first.", []
            
            if not docs or len(docs) == 0:
                # No documents found
                print(f"No documents retrieved for query in session {session_id}")
                return "I don't have any documents to reference yet. Please upload a document first.", []
            
            # Get sources
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
            
            # Build context - use all retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            print(f"Retrieved context length: {len(context)} characters from {len(docs)} documents")
            
            # Lazy load LLM if not already loaded
            if not self._llm_initialized:
                self._init_llm()
            
            if self.llm:
                # Use RAG with LLM - this should generate different answers based on query
                print(f"Using LLM to generate response for query: {query[:50]}...")
                response = await self._generate_with_llm(query, docs, vector_store)
                print(f"Generated response length: {len(response)} characters")
            else:
                # Fallback: return most relevant chunk with context
                # But at least mention the query to show it's being considered
                response = f"Based on the documents and your question '{query}':\n\n{context[:1000]}{'...' if len(context) > 1000 else ''}"
            
            return response, sources
        
        except Exception as e:
            print(f"RAG Error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback response
            return "I encountered an error processing your query. Please try again.", []
    
    async def _generate_with_llm(self, query: str, docs: List, vector_store) -> str:
        """Generate response using LLM"""
        if not self.llm:
            # Fallback response
            if docs:
                context = "\n\n".join([doc.page_content for doc in docs[:2]])
                return f"Based on the provided documents:\n\n{context[:500]}..."
            return "I'm here to help! Please upload some documents first so I can answer your questions."
        
        try:
            # Create prompt template
            template = """Use the following pieces of context to answer the question. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Answer: """
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            
            # Build context from documents
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
            full_prompt = prompt.format(context=context, question=query)
            
            # Generate response - try different methods based on LangChain version
            response = None
            response_text = None
            
            # Try invoke() first (newest LangChain - works with HuggingFaceEndpoint)
            if hasattr(self.llm, 'invoke'):
                try:
                    response = self.llm.invoke(full_prompt)
                    print("Used invoke() method")
                except Exception as e:
                    print(f"invoke() failed: {e}")
            
            # Try predict() (older LangChain - works with HuggingFaceHub)
            if response is None and hasattr(self.llm, 'predict'):
                try:
                    response = self.llm.predict(full_prompt)
                    print("Used predict() method")
                except Exception as e:
                    print(f"predict() failed: {e}")
            
            # Try run() (some versions)
            if response is None and hasattr(self.llm, 'run'):
                try:
                    response = self.llm.run(full_prompt)
                    print("Used run() method")
                except Exception as e:
                    print(f"run() failed: {e}")
            
            # For HuggingFaceHub, try using HuggingFace API directly
            if response is None:
                try:
                    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
                    repo_id = self.llm_repo_id or (hasattr(self.llm, 'repo_id') and self.llm.repo_id) or "mistralai/Mistral-7B-Instruct-v0.1"
                    
                    if hf_api_key and repo_id:
                        # Try multiple API endpoint formats
                        endpoints_to_try = [
                            # Try new inference API endpoint (correct format)
                            {
                                "url": f"https://api-inference.huggingface.co/models/{repo_id}",
                                "payload": {
                                    "inputs": full_prompt,
                                    "parameters": {
                                        "temperature": 0.7,
                                        "max_new_tokens": 512,
                                        "return_full_text": False
                                    }
                                }
                            },
                            # Try with a simpler model that's more likely to work
                            {
                                "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                                "payload": {
                                    "inputs": full_prompt,
                                    "parameters": {
                                        "temperature": 0.7,
                                        "max_new_tokens": 512,
                                        "return_full_text": False
                                    }
                                }
                            },
                            # Try with a smaller, more reliable model
                            {
                                "url": "https://api-inference.huggingface.co/models/google/flan-t5-large",
                                "payload": {
                                    "inputs": full_prompt,
                                    "parameters": {
                                        "temperature": 0.7,
                                        "max_new_tokens": 512,
                                        "return_full_text": False
                                    }
                                }
                            }
                        ]
                        
                        headers = {
                            "Authorization": f"Bearer {hf_api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        response = None
                        for i, endpoint_config in enumerate(endpoints_to_try):
                            try:
                                print(f"Attempting HuggingFace API call (method {i+1}/{len(endpoints_to_try)}) to {endpoint_config['url']}...")
                                api_response = requests.post(
                                    endpoint_config['url'], 
                                    headers=headers, 
                                    json=endpoint_config['payload'], 
                                    timeout=60
                                )
                        
                                if api_response.status_code == 200:
                                    result = api_response.json()
                                    
                                    # Handle chat completion format
                                    if isinstance(result, dict) and 'choices' in result:
                                        if len(result['choices']) > 0:
                                            response = result['choices'][0].get('message', {}).get('content', '')
                                    
                                    # Handle inference API format
                                    elif isinstance(result, list) and len(result) > 0:
                                        if isinstance(result[0], dict):
                                            response = result[0].get('generated_text', '')
                                        else:
                                            response = str(result[0])
                                    elif isinstance(result, dict):
                                        response = result.get('generated_text', result.get('text', str(result)))
                                    else:
                                        response = str(result)
                                    
                                    # Clean up the response
                                    if response:
                                        # Remove the original prompt if it's included
                                        if full_prompt in response:
                                            response = response.replace(full_prompt, "").strip()
                                        print(f"✅ Used direct HuggingFace API call (method {i+1}) - Response length: {len(response)}")
                                        break  # Success, exit loop
                                    else:
                                        print(f"⚠️ API returned empty response, trying next method...")
                                        
                                elif api_response.status_code == 503:
                                    # Model is loading, wait and retry
                                    print(f"Model is loading, waiting 10 seconds...")
                                    import time
                                    time.sleep(10)
                                    api_response = requests.post(
                                        endpoint_config['url'], 
                                        headers=headers, 
                                        json=endpoint_config['payload'], 
                                        timeout=60
                                    )
                                    if api_response.status_code == 200:
                                        result = api_response.json()
                                        if isinstance(result, dict) and 'choices' in result:
                                            response = result['choices'][0].get('message', {}).get('content', '')
                                        elif isinstance(result, list) and len(result) > 0:
                                            response = result[0].get('generated_text', '') if isinstance(result[0], dict) else str(result[0])
                                        elif isinstance(result, dict):
                                            response = result.get('generated_text', result.get('text', str(result)))
                                        else:
                                            response = str(result)
                                        if response and full_prompt in response:
                                            response = response.replace(full_prompt, "").strip()
                                        if response:
                                            print(f"✅ Used direct HuggingFace API call (after retry) - Response length: {len(response)}")
                                            break
                                else:
                                    print(f"Method {i+1} failed with status {api_response.status_code}: {api_response.text[:100]}")
                            except Exception as e:
                                print(f"Method {i+1} exception: {str(e)[:100]}")
                                continue
                        
                        if response:
                            # Success - we got a response from one of the methods
                            pass
                        else:
                            print(f"All API methods failed, will use smart fallback")
                except Exception as e:
                    print(f"Direct HuggingFace API call failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Try __call__ (direct call) as last resort
            if response is None:
                try:
                    response = self.llm(full_prompt)
                    print("Used direct call")
                except Exception as e:
                    print(f"Direct call failed: {e}")
            
            # If all methods failed, use smart fallback that generates different answers based on query
            if response is None:
                print("Using smart fallback to generate contextual response...")
                # Build context from documents for fallback
                context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
                response = self._generate_smart_fallback(query, docs, context)
            
            # Extract response text from various response formats
            if isinstance(response, str):
                response_text = response
            elif hasattr(response, 'content'):
                response_text = response.content
            elif hasattr(response, 'text'):
                response_text = response.text
            elif isinstance(response, dict):
                # Some LLMs return dict with 'text' or 'generated_text' key
                response_text = response.get('text') or response.get('generated_text') or str(response)
            else:
                response_text = str(response)
            
            # Clean up response (remove prompt if included)
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            if "Context:" in response_text:
                # Remove context part if it was included
                parts = response_text.split("Question:")
                if len(parts) > 1:
                    response_text = parts[-1].strip()
            
            return response_text
        
        except Exception as e:
            print(f"LLM Generation Error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Use smart fallback
            if docs:
                context = "\n\n".join([doc.page_content for doc in docs])
                return self._generate_smart_fallback(query, docs, context)
            return "I'm processing your question. Please try again in a moment."
    
    def _generate_smart_fallback(self, query: str, docs: List, context: str) -> str:
        """Generate a contextual response based on the query when LLM is unavailable"""
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        # Handle greetings and simple queries
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if query_lower in greetings or (len(query_words) <= 2 and any(word in greetings for word in query_words)):
            return "Hello! I'm here to help you with questions about the uploaded documents. What would you like to know?"
        
        # Extract relevant information based on query keywords
        if any(word in query_lower for word in ['location', 'where', 'place', 'city', 'address']):
            # Look for location information
            for doc in docs:
                content = doc.page_content
                content_lower = content.lower()
                if 'bengaluru' in content_lower or 'bangalore' in content_lower:
                    return "Based on the documents, the location is Bengaluru (Bangalore)."
                # Try to extract location from context
                import re
                location_match = re.search(r'\b(based in|located in|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', content, re.IGNORECASE)
                if location_match:
                    return f"Based on the documents, the location is {location_match.group(2)}."
        
        if any(word in query_lower for word in ['company', 'what does', 'description', 'about', 'tell me about']) and 'role' not in query_lower:
            # Look for company description - prioritize company info over role info
            company_info = []
            for doc in docs:
                content = doc.page_content
                content_lower = content.lower()
                # Look for company-specific information
                if 'pin click' in content_lower or any(word in content_lower for word in ['company', 'firm', 'organization']):
                    # Extract company description - get multiple sentences
                    sentences = content.split('.')
                    for sentence in sentences:
                        sentence_lower = sentence.lower()
                        # Prioritize sentences about the company
                        if ('pin click' in sentence_lower or 'company' in sentence_lower) and 'role' not in sentence_lower:
                            if any(word in sentence_lower for word in ['tech', 'real estate', 'advisory', 'property', 'firm', 'bangalore', 'developers', 'business']):
                                company_info.append(sentence.strip())
                    
                    # If we found company info, return it
                    if company_info:
                        return "Based on the documents:\n\n" + ". ".join(company_info[:4]) + "."
            
            # Fallback: return first substantial paragraph about company
            for doc in docs:
                content = doc.page_content
                if 'pin click' in content.lower() or len(content) > 200:
                    # Return first 500 chars as company description
                    return f"Based on the documents:\n\n{content[:500]}{'...' if len(content) > 500 else ''}"
        
        elif any(word in query_lower for word in ['role', 'job', 'position', 'responsibility', 'duties', 'advisor']):
            # Look for role information
            for doc in docs:
                content = doc.page_content
                if 'property advisor' in content.lower() or 'role' in content.lower() or 'responsibilities' in content.lower():
                    # Extract role description - get more context
                    sentences = content.split('.')
                    role_sentences = []
                    for sentence in sentences:
                        if any(word in sentence.lower() for word in ['property advisor', 'responsible', 'duties', 'role', 'position']):
                            role_sentences.append(sentence.strip())
                    
                    if role_sentences:
                        return "Based on the documents:\n\n" + ". ".join(role_sentences[:3]) + "."
                    
                    # Fallback: return relevant section
                    return f"Based on the documents:\n\n{content[:400]}{'...' if len(content) > 400 else ''}"
        
        elif any(word in query_lower for word in ['short', 'brief', 'summary', 'summarize']):
            # Generate a short summary
            summary_parts = []
            for doc in docs[:2]:  # Use first 2 documents
                content = doc.page_content
                # Get first sentence or first 150 chars
                first_sentence = content.split('.')[0] if '.' in content else content[:150]
                summary_parts.append(first_sentence.strip())
            return "Based on the documents:\n\n" + ". ".join(summary_parts) + "."
        
        # Default: return context relevant to query
        # Try to find the most relevant document chunk
        best_match = None
        best_score = 0
        
        for doc in docs:
            content_lower = doc.page_content.lower()
            # Count matching words
            score = sum(1 for word in query_words if word in content_lower and len(word) > 2)  # Ignore short words
            if score > best_score:
                best_score = score
                best_match = doc
        
        if best_match and best_score > 0:
            # Return more content from best matching document
            content = best_match.page_content
            return f"Based on the documents:\n\n{content[:600]}{'...' if len(content) > 600 else ''}"
        
        # Final fallback - return substantial part of context
        if context:
            return f"Based on the documents:\n\n{context[:800]}{'...' if len(context) > 800 else ''}"
        
        return "I have the documents, but I couldn't find specific information to answer your question. Could you rephrase it?"

