from typing import List, Dict, Any, Optional
import os
import asyncio
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.schema import Document
from app.core.config import settings
from loguru import logger
import chromadb
from chromadb.config import Settings as ChromaSettings

class RAGService:
    """RAG (Retrieval-Augmented Generation) 服务"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        self._initialize()
    
    def _initialize(self):
        """初始化RAG服务"""
        try:
            logger.info("初始化RAG服务...")
            
            # 初始化文本分割器
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", ";", ":", "，", " ", ""]
            )
            
            # 初始化嵌入模型
            # 优先尝试使用 SiliconFlow API，如果配置了 API Key
            silicon_key = getattr(settings, 'SILICONFLOW_API_KEY', '') or os.getenv('SILICONFLOW_API_KEY')
            
            if silicon_key:
                try:
                    from app.services.embeddings import SiliconFlowEmbeddings
                    # 获取配置的模型名称，默认为 BGE-M3
                    embedding_model = getattr(settings, 'SILICONFLOW_EMBEDDING_MODEL', 'BAAI/bge-m3')
                    logger.info(f"使用 SiliconFlow 嵌入模型: {embedding_model}")
                    
                    self.embeddings = SiliconFlowEmbeddings(
                        api_key=silicon_key,
                        model=embedding_model,
                        base_url=getattr(settings, 'SILICONFLOW_API_BASE', 'https://api.siliconflow.cn/v1')
                    )
                except Exception as e:
                    logger.warning(f"SiliconFlow 嵌入模型初始化失败，回退到本地模型: {e}")
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name=settings.EMBEDDING_MODEL,
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
            else:
                logger.info("使用本地 HuggingFace 嵌入模型...")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            
            # 初始化向量数据库
            self._initialize_vectorstore()
            
            logger.info("RAG服务初始化完成")
            
        except Exception as e:
            logger.error(f"RAG服务初始化失败: {str(e)}")
            # 不要在这里 raise，否则整个应用会崩溃或者返回 500
            # 我们允许 RAG 服务降级运行（即没有向量库功能）
            # raise 
    
    def _initialize_vectorstore(self):
        """初始化向量数据库"""
        try:
            # 确保向量数据库目录存在
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            
            # 配置Chroma客户端
            chroma_client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 初始化向量存储
            try:
                self.vectorstore = Chroma(
                    client=chroma_client,
                    collection_name="chemistry_knowledge",
                    embedding_function=self.embeddings
                )
                logger.info(f"向量数据库初始化完成，路径: {settings.VECTOR_DB_PATH}")
            except Exception as e:
                logger.error(f"ChromaDB 初始化失败: {e}")
                # 尝试重置或重建
                logger.warning("尝试重建 ChromaDB 客户端...")
                # 这里可以添加重建逻辑，或者只是记录错误
                raise e
            
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {str(e)}")
            raise
    
    async def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """从目录加载文档"""
        try:
            logger.info(f"开始从目录加载文档: {directory_path}")
            
            documents = []
            
            # 支持的文件类型
            file_types = {
                '.pdf': PyPDFLoader,
                '.txt': TextLoader,
                '.md': TextLoader
            }
            
            directory = Path(directory_path)
            if not directory.exists():
                logger.warning(f"目录不存在: {directory_path}")
                return documents
            
            # 遍历目录中的文件
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in file_types:
                    try:
                        loader_class = file_types[file_path.suffix.lower()]
                        loader = loader_class(str(file_path))
                        
                        # 加载文档
                        file_documents = await asyncio.get_event_loop().run_in_executor(
                            None, loader.load
                        )
                        
                        # 添加元数据
                        for doc in file_documents:
                            doc.metadata.update({
                                'source': str(file_path),
                                'file_type': file_path.suffix.lower(),
                                'file_name': file_path.name
                            })
                        
                        documents.extend(file_documents)
                        logger.info(f"已加载文档: {file_path} ({len(file_documents)} 个片段)")
                        
                    except Exception as e:
                        logger.error(f"加载文档失败 {file_path}: {str(e)}")
                        continue
            
            logger.info(f"文档加载完成，共 {len(documents)} 个文档")
            return documents
            
        except Exception as e:
            logger.error(f"从目录加载文档失败: {str(e)}")
            raise

    async def clear_database(self) -> bool:
        """清空向量数据库"""
        try:
            if self.vectorstore:
                # 删除集合并重新初始化
                self.vectorstore.delete_collection()
                self._initialize_vectorstore()
                logger.info("向量数据库已清空")
                return True
            return False
        except Exception as e:
            logger.error(f"清空数据库失败: {str(e)}")
            return False

    async def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            if not self.vectorstore:
                return {"count": 0, "files": []}
            
            # 获取所有数据
            data = self.vectorstore.get()
            metadatas = data.get("metadatas", [])
            
            files = {}
            for meta in metadatas:
                if meta and "file_name" in meta:
                    fname = meta["file_name"]
                    if fname not in files:
                        files[fname] = {"count": 0, "source": meta.get("source")}
                    files[fname]["count"] += 1
            
            file_list = [{"name": k, "chunks": v["count"], "path": v["source"]} for k, v in files.items()]
            
            return {
                "total_chunks": len(metadatas),
                "file_count": len(files),
                "files": file_list
            }
        except Exception as e:
            logger.error(f"获取数据库统计失败: {str(e)}")
            return {"error": str(e)}
    
    async def add_documents(self, documents: List[Document]) -> None:
        """添加文档到向量数据库"""
        try:
            if not documents:
                logger.warning("没有文档需要添加")
                return
            
            logger.info(f"开始处理 {len(documents)} 个文档")
            
            # 分割文档
            split_documents = []
            for doc in documents:
                splits = self.text_splitter.split_documents([doc])
                split_documents.extend(splits)
            
            logger.info(f"文档分割完成，共 {len(split_documents)} 个片段")
            
            # 批量添加到向量数据库
            batch_size = 100
            for i in range(0, len(split_documents), batch_size):
                batch = split_documents[i:i + batch_size]
                await asyncio.get_event_loop().run_in_executor(
                    None, self.vectorstore.add_documents, batch
                )
                logger.info(f"已添加批次 {i//batch_size + 1}/{(len(split_documents)-1)//batch_size + 1}")
            
            logger.info("文档添加完成")
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise
    
    async def search_documents(
        self, 
        query: str, 
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        try:
            logger.info(f"搜索查询: {query[:100]}...")
            
            if not self.vectorstore:
                logger.error("向量数据库未初始化")
                return []
            
            # 执行相似性搜索
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.similarity_search_with_score(
                    query, k=top_k
                )
            )
            
            # 过滤结果并格式化
            filtered_results = []
            for doc, score in results:
                if score >= score_threshold:
                    filtered_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': score
                    })
            
            logger.info(f"搜索完成，返回 {len(filtered_results)} 个结果")
            return filtered_results
            
        except Exception as e:
            logger.error(f"文档搜索失败: {str(e)}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if not self.vectorstore:
                return {"error": "向量数据库未初始化"}
            
            # 获取集合信息
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "document_count": count,
                "collection_name": collection.name,
                "embedding_model": settings.EMBEDDING_MODEL
            }
            
        except Exception as e:
            logger.error(f"获取集合统计信息失败: {str(e)}")
            return {"error": str(e)}
    
    async def clear_collection(self) -> bool:
        """清空集合"""
        try:
            if not self.vectorstore:
                logger.error("向量数据库未初始化")
                return False
            
            # 删除所有文档
            collection = self.vectorstore._collection
            collection.delete()
            
            logger.info("集合已清空")
            return True
            
        except Exception as e:
            logger.error(f"清空集合失败: {str(e)}")
            return False