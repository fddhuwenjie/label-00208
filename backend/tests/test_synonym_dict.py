"""同义词词典单元测试"""

import pytest

from app.utils.synonym_dict import SynonymDict, get_synonym_dict


class TestSynonymDict:
    """同义词词典测试类"""
    
    @pytest.fixture
    def synonym_dict(self):
        """创建同义词词典实例"""
        return SynonymDict()
    
    def test_get_synonyms_main_word(self, synonym_dict):
        """测试获取主词的同义词"""
        synonyms = synonym_dict.get_synonyms("人工智能")
        
        assert "人工智能" in synonyms
        assert "AI" in synonyms
        assert "机器学习" in synonyms
        assert len(synonyms) > 1
    
    def test_get_synonyms_synonym_word(self, synonym_dict):
        """测试从同义词反查"""
        synonyms = synonym_dict.get_synonyms("AI")
        
        assert "人工智能" in synonyms
        assert "AI" in synonyms
    
    def test_get_synonyms_unknown_word(self, synonym_dict):
        """测试未知词"""
        synonyms = synonym_dict.get_synonyms("完全未知的词汇xyz")
        
        assert synonyms == ["完全未知的词汇xyz"]
    
    def test_expand_query_single_word(self, synonym_dict):
        """测试单词查询扩展"""
        expanded = synonym_dict.expand_query("就业")
        
        assert "就业" in expanded
        assert "OR" in expanded
        assert "工作" in expanded or "岗位" in expanded
    
    def test_expand_query_no_synonyms(self, synonym_dict):
        """测试无同义词的查询"""
        expanded = synonym_dict.expand_query("测试词汇")
        
        # 未知词不会被括号包围
        assert "OR" not in expanded or "测试" not in expanded
    
    def test_get_all_synonyms_for_query(self, synonym_dict):
        """测试获取查询中所有同义词"""
        all_syns = synonym_dict.get_all_synonyms_for_query("人工智能 就业")
        
        assert "人工智能" in all_syns
        assert "AI" in all_syns
        assert "就业" in all_syns
        assert "工作" in all_syns
    
    def test_add_synonym(self, synonym_dict):
        """测试添加同义词"""
        synonym_dict.add_synonym("测试主词", ["测试同义词1", "测试同义词2"])
        
        synonyms = synonym_dict.get_synonyms("测试主词")
        
        assert "测试主词" in synonyms
        assert "测试同义词1" in synonyms
        assert "测试同义词2" in synonyms
    
    def test_get_main_word(self, synonym_dict):
        """测试获取主词"""
        main = synonym_dict.get_main_word("AI")
        
        assert main == "人工智能"
    
    def test_get_main_word_unknown(self, synonym_dict):
        """测试未知词返回自身"""
        main = synonym_dict.get_main_word("未知词")
        
        assert main == "未知词"
    
    def test_singleton(self):
        """测试单例模式"""
        dict1 = get_synonym_dict()
        dict2 = get_synonym_dict()
        
        assert dict1 is dict2


class TestSynonymDictCoverage:
    """同义词词典覆盖率测试"""
    
    def test_economic_synonyms(self):
        """测试经济领域同义词"""
        sd = SynonymDict()
        
        assert len(sd.get_synonyms("经济")) > 1
        assert len(sd.get_synonyms("就业")) > 1
        assert len(sd.get_synonyms("收入")) > 1
    
    def test_tech_synonyms(self):
        """测试科技领域同义词"""
        sd = SynonymDict()
        
        assert len(sd.get_synonyms("技术")) > 1
        assert len(sd.get_synonyms("创新")) > 1
    
    def test_social_synonyms(self):
        """测试社会领域同义词"""
        sd = SynonymDict()
        
        assert len(sd.get_synonyms("教育")) > 1
        assert len(sd.get_synonyms("医疗")) > 1
    
    def test_debate_synonyms(self):
        """测试辩论常用同义词"""
        sd = SynonymDict()
        
        assert len(sd.get_synonyms("优势")) > 1
        assert len(sd.get_synonyms("问题")) > 1
        assert len(sd.get_synonyms("发展")) > 1
