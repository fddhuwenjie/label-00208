"""语义分析服务 - 基于 Sentence-Transformers 深度语义嵌入

支持两种模式：
1. 深度语义模式（默认）：使用 Sentence-Transformers 预训练模型
2. TF-IDF 降级模式：当深度模型不可用时自动启用

可通过环境变量 DISABLE_SEMANTIC_MODEL=true 强制使用 TF-IDF 模式
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Optional
from collections import Counter

import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import VECTOR_DIR, SIMILARITY_THRESHOLD, DISABLE_SEMANTIC_MODEL
from app.models.document import Document
from app.utils.logger import semantic_logger as logger

# 延迟加载 sentence-transformers，避免启动时间过长
_sentence_model = None
_model_name = "paraphrase-multilingual-MiniLM-L12-v2"
_model_load_failed = False  # 标记模型是否加载失败
_tfidf_vectorizer = None  # TF-IDF 降级方案


def is_using_fallback_mode() -> bool:
    """检查是否使用 TF-IDF 降级模式"""
    return DISABLE_SEMANTIC_MODEL or _model_load_failed


def get_sentence_model():
    """
    延迟加载 Sentence Transformer 模型
    
    加载失败时会自动标记 _model_load_failed，后续调用将使用 TF-IDF 降级
    """
    global _sentence_model, _model_load_failed
    
    if DISABLE_SEMANTIC_MODEL:
        logger.info("深度语义模型已禁用（DISABLE_SEMANTIC_MODEL=true），使用 TF-IDF 方案")
        _model_load_failed = True
        return None
    
    if _model_load_failed:
        return None
    
    if _sentence_model is None:
        logger.info(f"正在加载语义模型 {_model_name}（首次加载需要下载，可能需要几分钟）...")
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer(_model_name)
            logger.info("语义模型加载完成")
        except ImportError as e:
            logger.warning(f"sentence-transformers 未安装，降级到 TF-IDF 方案: {e}")
            _model_load_failed = True
            return None
        except Exception as e:
            logger.warning(f"加载语义模型失败，降级到 TF-IDF 方案: {e}")
            _model_load_failed = True
            return None
    return _sentence_model


def get_tfidf_vectorizer():
    """获取 TF-IDF 向量化器（降级方案）"""
    global _tfidf_vectorizer
    if _tfidf_vectorizer is None:
        _tfidf_vectorizer = TfidfVectorizer(
            tokenizer=lambda x: list(jieba.cut(x)),
            max_features=5000,
            ngram_range=(1, 2)
        )
    return _tfidf_vectorizer


class SemanticAnalyzer:
    """语义分析器 - 基于深度学习的语义嵌入"""
    
    def __init__(self):
        self.vector_dir = Path(VECTOR_DIR)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        
        # 文档缓存
        self._doc_texts = {}
        self._doc_ids = []
        self._doc_embeddings = None
        
        # 预定义的语义概念库（用于增强联想）
        self._concept_library = self._build_concept_library()
        
        # 加载缓存
        self._load_cache()
    
    def _build_concept_library(self) -> dict:
        """构建语义概念库 - 用于增强语义联想"""
        return {
            "年轻人": ["青年", "年轻一代", "Z世代", "90后", "00后", "年轻人收入", "年轻人就业", 
                     "年轻人消费", "年轻人压力", "年轻人心理", "年轻人婚姻", "年轻人生育",
                     "青年失业", "青年创业", "大学生", "毕业生"],
            "就业": ["工作", "职业", "失业", "招聘", "求职", "劳动力市场", "就业率", 
                    "失业率", "灵活就业", "创业", "工资", "薪资", "收入"],
            "经济": ["GDP", "增长", "发展", "通胀", "消费", "投资", "贸易", 
                    "金融", "财政", "税收", "货币政策", "经济周期"],
            "教育": ["学校", "学生", "教师", "课程", "学习", "培训", "高考", 
                    "大学", "义务教育", "职业教育", "素质教育", "教育公平"],
            "科技": ["技术", "创新", "人工智能", "AI", "互联网", "数字化", 
                    "自动化", "智能", "大数据", "云计算", "5G"],
            "环境": ["生态", "污染", "碳排放", "气候", "绿色", "新能源", 
                    "可持续", "环保", "减排", "清洁能源"],
            "社会": ["公共", "公民", "群体", "阶层", "城市", "农村", 
                    "社区", "民生", "福利", "保障", "养老", "医疗"],
            "政策": ["法律", "法规", "政府", "监管", "制度", "改革", 
                    "规划", "措施", "方案", "执行"],
        }
    
    def _tokenize(self, text: str) -> list[str]:
        """中文分词"""
        words = jieba.cut(text)
        return [w.strip() for w in words if len(w.strip()) >= 2 and not self._is_stopword(w)]
    
    def _is_stopword(self, word: str) -> bool:
        """检查是否为停用词"""
        stopwords = {
            "的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他",
            "她", "它", "我们", "你们", "他们", "这个", "那个", "什么",
            "为什么", "怎么", "如何", "可以", "能够", "应该", "需要",
            "但是", "因为", "所以", "如果", "虽然", "或者", "而且",
            "并且", "然后", "之后", "之前", "通过", "进行", "使用",
            "以及", "对于", "关于", "其中", "包括", "根据", "按照",
        }
        return word in stopwords
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        编码单个文本为向量
        
        优先使用 Sentence Transformer，失败时降级到 TF-IDF
        """
        model = get_sentence_model()
        
        if model is not None:
            try:
                embedding = model.encode(text, convert_to_numpy=True)
                return embedding
            except Exception as e:
                logger.warning(f"Sentence Transformer 编码失败，降级到 TF-IDF: {e}")
        
        # TF-IDF 降级方案
        return self._encode_tfidf_single(text)
    
    def _encode_tfidf_single(self, text: str) -> np.ndarray:
        """使用 TF-IDF 编码单个文本（降级方案）"""
        try:
            vectorizer = get_tfidf_vectorizer()
            # 需要用已有文档库来 fit，如果还没有则返回空
            if not self._doc_texts:
                # 使用简单的词袋方式
                words = list(jieba.cut(text))
                return np.array([hash(w) % 10000 / 10000.0 for w in words[:100]])
            
            # 使用已有文档库 fit
            all_texts = list(self._doc_texts.values()) + [text]
            try:
                tfidf_matrix = vectorizer.fit_transform(all_texts)
                return tfidf_matrix[-1].toarray().flatten()
            except Exception:
                return np.array([])
        except Exception as e:
            logger.error(f"TF-IDF 编码失败: {e}")
            return np.array([])
    
    def encode_batch(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """
        批量编码文本
        
        优先使用 Sentence Transformer，失败时降级到 TF-IDF
        """
        model = get_sentence_model()
        
        if model is not None:
            try:
                embeddings = model.encode(
                    texts, 
                    convert_to_numpy=True,
                    batch_size=batch_size,
                    show_progress_bar=True
                )
                return embeddings
            except Exception as e:
                logger.warning(f"Sentence Transformer 批量编码失败，降级到 TF-IDF: {e}")
        
        # TF-IDF 降级方案
        return self._encode_tfidf_batch(texts)
    
    def _encode_tfidf_batch(self, texts: list[str]) -> np.ndarray:
        """使用 TF-IDF 批量编码（降级方案）"""
        try:
            vectorizer = get_tfidf_vectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            return tfidf_matrix.toarray()
        except Exception as e:
            logger.error(f"TF-IDF 批量编码失败: {e}")
            return np.array([])
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def find_similar_concepts(
        self,
        keyword: str,
        top_k: int = 15,
        threshold: float = None
    ) -> list[tuple[str, float]]:
        """
        基于深度语义嵌入查找与关键词相关的概念
        
        真正理解语义关系，如"年轻人"能找到"就业"、"消费"、"压力"等
        """
        if threshold is None:
            threshold = SIMILARITY_THRESHOLD
        
        results = []
        
        # 方法1: 从概念库中找语义相关的词
        keyword_embedding = self.encode_single(keyword)
        if len(keyword_embedding) > 0:
            # 获取概念库中所有词
            all_concepts = set()
            for category, concepts in self._concept_library.items():
                all_concepts.add(category)
                all_concepts.update(concepts)
            
            # 编码所有概念
            concept_list = list(all_concepts)
            if concept_list:
                concept_embeddings = self.encode_batch(concept_list)
                
                # 计算相似度
                for i, concept in enumerate(concept_list):
                    if concept != keyword:
                        sim = self.similarity(keyword_embedding, concept_embeddings[i])
                        if sim >= threshold:
                            results.append((concept, float(sim)))
        
        # 方法2: 从已索引文档中提取相关关键词
        doc_keywords = self._extract_keywords_from_docs(keyword)
        for word, score in doc_keywords:
            if word not in [r[0] for r in results]:
                results.append((word, score * 0.8))  # 稍微降权
        
        # 去重并排序
        concept_scores = {}
        for concept, score in results:
            if concept in concept_scores:
                concept_scores[concept] = max(concept_scores[concept], score)
            else:
                concept_scores[concept] = score
        
        sorted_concepts = sorted(concept_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_concepts[:top_k]
    
    def _extract_keywords_from_docs(
        self,
        keyword: str,
        top_k: int = 20
    ) -> list[tuple[str, float]]:
        """从包含关键词的文档中提取相关关键词"""
        related_texts = []
        
        for doc_id, text in self._doc_texts.items():
            if keyword.lower() in text.lower():
                # 提取关键词周围的上下文
                idx = text.lower().find(keyword.lower())
                start = max(0, idx - 200)
                end = min(len(text), idx + len(keyword) + 200)
                context = text[start:end]
                related_texts.append(context)
        
        if not related_texts:
            return []
        
        # 合并文本并提取关键词
        combined_text = " ".join(related_texts)
        keywords = jieba.analyse.extract_tags(combined_text, topK=top_k, withWeight=True)
        
        # 过滤掉原关键词
        filtered = [(w, s) for w, s in keywords if w.lower() != keyword.lower() and len(w) >= 2]
        return filtered
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.3
    ) -> list[tuple[str, float, str]]:
        """
        语义搜索 - 在所有已索引文档中查找语义相似的内容
        
        Returns:
            [(doc_id, similarity_score, matched_text), ...]
        """
        if self._doc_embeddings is None or len(self._doc_embeddings) == 0:
            return []
        
        query_embedding = self.encode_single(query)
        if len(query_embedding) == 0:
            return []
        
        results = []
        for i, doc_id in enumerate(self._doc_ids):
            sim = self.similarity(query_embedding, self._doc_embeddings[i])
            if sim >= threshold:
                text_preview = self._doc_texts.get(doc_id, "")[:200]
                results.append((doc_id, float(sim), text_preview))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def analyze_cooccurrence(
        self,
        keyword: str,
        documents: list[Document],
        top_k: int = 15
    ) -> list[tuple[str, int]]:
        """分析关键词的共现词（保留原有功能）"""
        cooccur_counter = Counter()
        
        for doc in documents:
            text = doc.full_text
            
            if keyword.lower() not in text.lower():
                continue
            
            words = list(jieba.cut(text))
            keyword_lower = keyword.lower()
            
            for i, word in enumerate(words):
                if keyword_lower in word.lower():
                    start = max(0, i - 5)
                    end = min(len(words), i + 6)
                    
                    for j in range(start, end):
                        if j != i:
                            neighbor = words[j].strip()
                            if len(neighbor) >= 2 and not self._is_stopword(neighbor):
                                cooccur_counter[neighbor] += 1
        
        return cooccur_counter.most_common(top_k)
    
    def build_concept_tree(
        self,
        keyword: str,
        documents: list[Document],
        depth: int = 2
    ) -> dict:
        """构建概念-子概念树"""
        tree = {
            "keyword": keyword,
            "children": []
        }
        
        if depth <= 0:
            return tree
        
        # 使用语义联想获取相关概念
        related = self.find_similar_concepts(keyword, top_k=8)
        
        for concept, score in related:
            child = {
                "keyword": concept,
                "score": score,
                "children": []
            }
            
            if depth > 1:
                sub_related = self.find_similar_concepts(concept, top_k=5)
                for sub_concept, sub_score in sub_related:
                    if sub_concept != keyword:
                        child["children"].append({
                            "keyword": sub_concept,
                            "score": sub_score,
                            "children": []
                        })
            
            tree["children"].append(child)
        
        return tree
    
    def categorize_concepts(
        self,
        keyword: str,
        concepts: list[str]
    ) -> dict[str, list[str]]:
        """将概念按维度分类"""
        dimension_templates = {
            "经济维度": ["收入", "消费", "就业", "工资", "房价", "物价", "经济", "财务", "理财", "投资"],
            "社会维度": ["教育", "婚姻", "生育", "社交", "人际", "家庭", "社会", "公共"],
            "心理维度": ["压力", "焦虑", "心理", "情绪", "幸福", "满意", "健康", "精神"],
            "文化维度": ["价值观", "态度", "观念", "文化", "传统", "现代", "思想", "信仰"],
            "行为维度": ["行为", "习惯", "方式", "选择", "决策", "偏好", "趋势"],
        }
        
        categorized = {dim: [] for dim in dimension_templates}
        categorized["其他"] = []
        
        for concept in concepts:
            matched = False
            for dim, keywords in dimension_templates.items():
                for kw in keywords:
                    if kw in concept or concept in kw:
                        categorized[dim].append(concept)
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                categorized["其他"].append(concept)
        
        return {k: v for k, v in categorized.items() if v}
    
    def index_document(self, doc: Document) -> bool:
        """索引单个文档"""
        try:
            self._doc_ids.append(doc.id)
            self._doc_texts[doc.id] = doc.full_text[:5000]
            return True
        except Exception as e:
            logger.error(f"索引文档失败: {e}")
            return False
    
    def index_documents(
        self,
        documents: list[Document],
        progress_callback: callable = None
    ) -> int:
        """批量索引文档并生成语义嵌入"""
        success = 0
        total = len(documents)
        
        # 重置
        self._doc_ids = []
        self._doc_texts = {}
        
        # 收集文本
        texts = []
        for idx, doc in enumerate(documents):
            if progress_callback:
                progress_callback(idx + 1, total, f"处理文档: {doc.file_name}")
            
            self._doc_ids.append(doc.id)
            text = doc.full_text[:5000]
            self._doc_texts[doc.id] = text
            texts.append(text)
            success += 1
        
        # 批量生成语义嵌入
        if texts:
            if progress_callback:
                progress_callback(total, total, "正在生成语义嵌入（首次可能需要下载模型）...")
            
            try:
                self._doc_embeddings = self.encode_batch(texts)
                logger.info(f"成功为 {len(texts)} 个文档生成语义嵌入")
            except Exception as e:
                logger.error(f"生成语义嵌入失败: {e}")
                self._doc_embeddings = None
        
        # 保存缓存
        self._save_cache()
        
        return success
    
    def _save_cache(self):
        """保存缓存"""
        meta_file = self.vector_dir / "meta.json"
        embeddings_file = self.vector_dir / "embeddings.npy"
        
        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump({
                    "texts": self._doc_texts,
                    "doc_ids": self._doc_ids,
                }, f, ensure_ascii=False)
            
            if self._doc_embeddings is not None:
                np.save(str(embeddings_file), self._doc_embeddings)
                
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _load_cache(self):
        """加载缓存"""
        meta_file = self.vector_dir / "meta.json"
        embeddings_file = self.vector_dir / "embeddings.npy"
        
        try:
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self._doc_texts = meta.get("texts", {})
                    self._doc_ids = meta.get("doc_ids", [])
            
            if embeddings_file.exists():
                self._doc_embeddings = np.load(str(embeddings_file))
                
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        self._doc_embeddings = None
        self._doc_texts = {}
        self._doc_ids = []
        
        for f in self.vector_dir.glob("*"):
            try:
                f.unlink()
            except:
                pass


def get_semantic_suggestions(
    keyword: str,
    documents: list[Document],
    top_k: int = 12
) -> list[str]:
    """
    获取语义联想建议（简化接口）
    
    基于深度语义嵌入，真正理解语义关系
    """
    analyzer = SemanticAnalyzer()
    
    # 使用语义相似度查找相关概念
    similar_concepts = analyzer.find_similar_concepts(keyword, top_k=top_k)
    
    # 提取词列表
    suggestions = [word for word, score in similar_concepts]
    
    return suggestions


def analyze_stance(text: str, use_semantic: bool = True) -> tuple[str, float]:
    """
    分析文本的立场倾向（正方/反方/中立）
    
    使用两层分析：
    1. 语义嵌入分析（如果可用）
    2. 关键词匹配作为补充/降级方案
    
    Returns:
        (stance, confidence): 立场和置信度
    """
    # 正反方参考短语（用于语义相似度计算）
    pro_phrases = [
        "我支持这个观点", "这是有利的", "应该推行", "好处很多",
        "这是正确的做法", "值得支持", "利大于弊"
    ]
    con_phrases = [
        "我反对这个观点", "这是有害的", "不应该推行", "坏处很多",
        "这是错误的做法", "不值得支持", "弊大于利"
    ]
    
    # 尝试使用语义分析
    semantic_result = None
    if use_semantic and not is_using_fallback_mode():
        try:
            model = get_sentence_model()
            if model is not None:
                # 编码文本和参考短语
                text_embedding = model.encode(text, convert_to_numpy=True)
                pro_embeddings = model.encode(pro_phrases, convert_to_numpy=True)
                con_embeddings = model.encode(con_phrases, convert_to_numpy=True)
                
                # 计算与正方和反方短语的平均相似度
                pro_sim = float(np.mean([
                    np.dot(text_embedding, e) / (np.linalg.norm(text_embedding) * np.linalg.norm(e))
                    for e in pro_embeddings
                ]))
                con_sim = float(np.mean([
                    np.dot(text_embedding, e) / (np.linalg.norm(text_embedding) * np.linalg.norm(e))
                    for e in con_embeddings
                ]))
                
                diff = pro_sim - con_sim
                if abs(diff) < 0.05:
                    semantic_result = ("neutral", 0.5)
                elif diff > 0:
                    semantic_result = ("pro", min(0.5 + diff * 2, 0.95))
                else:
                    semantic_result = ("con", min(0.5 + abs(diff) * 2, 0.95))
        except Exception as e:
            logger.debug(f"语义立场分析失败: {e}")
    
    # 关键词匹配分析
    positive_keywords = [
        "支持", "赞成", "有利", "促进", "提高", "增强", "改善", "应该", 
        "好处", "优势", "积极", "推动", "有效", "成功", "正确", "必要",
        "有益", "利好", "值得", "合理", "可取", "肯定"
    ]
    negative_keywords = [
        "反对", "不赞成", "不利", "阻碍", "降低", "减弱", "恶化", "不应该",
        "坏处", "劣势", "消极", "阻挡", "无效", "失败", "错误", "不必要",
        "有害", "利空", "不值得", "不合理", "不可取", "否定"
    ]
    
    text_lower = text.lower()
    
    pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
    neg_count = sum(1 for kw in negative_keywords if kw in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        keyword_result = ("neutral", 0.5)
    elif pos_count > neg_count:
        keyword_result = ("pro", pos_count / total)
    elif neg_count > pos_count:
        keyword_result = ("con", neg_count / total)
    else:
        keyword_result = ("neutral", 0.5)
    
    # 综合结果：语义分析优先，关键词作为参考
    if semantic_result:
        # 如果两者一致，提高置信度；不一致则使用语义结果
        if semantic_result[0] == keyword_result[0]:
            return (semantic_result[0], min(semantic_result[1] * 1.2, 0.98))
        return semantic_result
    
    return keyword_result


def auto_classify_stance(text: str, debate_topic: str = None, use_semantic: bool = True) -> dict:
    """
    自动分类文本的辩论立场（增强版）
    
    使用语义嵌入分析 + 关键词匹配双重策略
    
    Args:
        text: 待分类文本
        debate_topic: 辩论主题（可选，用于增强分类准确度）
        use_semantic: 是否使用语义分析（默认开启）
        
    Returns:
        {
            "stance": "pro" | "con" | "neutral",
            "confidence": float,
            "keywords": list[str],  # 检测到的关键词
            "suggestion": str,  # 分类建议说明
            "method": str  # 使用的分析方法
        }
    """
    # 使用增强的立场分析
    stance, confidence = analyze_stance(text, use_semantic=use_semantic)
    
    # 检测关键词
    detected_keywords = []
    
    pro_keywords = ["支持", "赞成", "有利", "促进", "应该", "好处", "优势", "积极", "正确", "必要"]
    con_keywords = ["反对", "不赞成", "不利", "阻碍", "不应该", "坏处", "劣势", "消极", "错误", "不必要"]
    
    for kw in pro_keywords:
        if kw in text:
            detected_keywords.append(f"✓ {kw}")
    for kw in con_keywords:
        if kw in text:
            detected_keywords.append(f"✗ {kw}")
    
    # 确定使用的分析方法
    method = "语义分析" if (use_semantic and not is_using_fallback_mode()) else "关键词匹配"
    
    # 生成建议
    confidence_level = "高" if confidence >= 0.8 else ("中" if confidence >= 0.6 else "低")
    
    if stance == "pro":
        suggestion = f"文本倾向于支持观点（置信度: {confidence_level} {confidence:.0%}）"
    elif stance == "con":
        suggestion = f"文本倾向于反对观点（置信度: {confidence_level} {confidence:.0%}）"
    else:
        suggestion = "文本立场较为中立，建议人工判断"
    
    return {
        "stance": stance,
        "confidence": confidence,
        "keywords": detected_keywords,
        "suggestion": suggestion,
        "method": method
    }
