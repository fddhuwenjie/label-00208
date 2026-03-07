"""同义词词典模块 - 支持同义词扩展搜索"""

from typing import Optional


class SynonymDict:
    """同义词词典"""
    
    def __init__(self):
        self._synonyms = self._build_default_dict()
        self._reverse_index = self._build_reverse_index()
    
    def _build_default_dict(self) -> dict[str, list[str]]:
        """构建默认同义词词典（辩论/学术场景）"""
        return {
            # 经济相关
            "经济": ["经济发展", "经济增长", "GDP", "国民经济", "宏观经济"],
            "就业": ["工作", "岗位", "职业", "劳动", "雇佣", "招聘", "就业率"],
            "失业": ["下岗", "待业", "无业", "失业率"],
            "收入": ["工资", "薪资", "薪酬", "报酬", "薪水", "所得"],
            "消费": ["购买", "支出", "花费", "消费者"],
            "投资": ["投入", "注资", "融资", "资本"],
            "贸易": ["进出口", "出口", "进口", "国际贸易", "外贸"],
            "通胀": ["通货膨胀", "物价上涨", "CPI"],
            
            # 科技相关
            "人工智能": ["AI", "机器学习", "深度学习", "智能", "自动化"],
            "技术": ["科技", "技术发展", "技术进步", "科学技术"],
            "创新": ["创造", "发明", "革新", "创意"],
            "数字化": ["数字经济", "信息化", "互联网", "数字转型"],
            "自动化": ["机械化", "智能化", "无人化"],
            
            # 社会相关
            "教育": ["教学", "学习", "培训", "教育资源", "学校"],
            "医疗": ["医疗卫生", "医疗服务", "医疗资源", "看病", "就医", "健康"],
            "养老": ["养老金", "退休", "老龄化", "养老服务", "老年"],
            "住房": ["房产", "房地产", "房价", "房屋", "楼市", "购房"],
            "贫困": ["贫穷", "脱贫", "扶贫", "低收入"],
            "公平": ["平等", "公正", "均等", "正义"],
            "福利": ["社会福利", "保障", "社会保障", "福利制度"],
            
            # 环境相关
            "环境": ["环境保护", "生态", "生态环境", "自然环境"],
            "污染": ["环境污染", "污染物", "排放"],
            "碳排放": ["温室气体", "二氧化碳", "碳中和", "低碳"],
            "新能源": ["清洁能源", "可再生能源", "绿色能源", "太阳能", "风能"],
            "气候": ["气候变化", "全球变暖", "气候问题"],
            
            # 政策相关
            "政策": ["政策措施", "政策法规", "制度", "规定"],
            "法律": ["法规", "法律法规", "立法", "法制"],
            "监管": ["管理", "管控", "监督", "规范"],
            "改革": ["改革开放", "变革", "制度改革"],
            
            # 人口相关
            "人口": ["人口数量", "人口结构", "人口问题"],
            "生育": ["生育率", "出生率", "生育政策", "生育意愿"],
            "老龄化": ["人口老龄化", "老龄", "高龄化"],
            "年轻人": ["青年", "年轻一代", "青年人", "青年群体", "Z世代"],
            
            # 辩论常用
            "优势": ["优点", "好处", "利", "益处", "长处"],
            "劣势": ["缺点", "坏处", "弊", "弊端", "短处"],
            "影响": ["作用", "效果", "后果", "影响力"],
            "问题": ["难题", "困难", "挑战", "议题"],
            "发展": ["进步", "增长", "提升", "壮大"],
            "下降": ["减少", "降低", "下滑", "萎缩"],
            "增加": ["提升", "上升", "增长", "增多", "提高"],
            "原因": ["因素", "根源", "成因", "缘由"],
            "结果": ["后果", "结局", "成果", "效果"],
            "趋势": ["走向", "态势", "动向", "方向"],
            "研究": ["调研", "调查", "分析", "研究报告"],
            "数据": ["数据显示", "统计", "数据表明", "统计数据"],
        }
    
    def _build_reverse_index(self) -> dict[str, str]:
        """构建反向索引（同义词 -> 主词）"""
        reverse = {}
        for main_word, synonyms in self._synonyms.items():
            reverse[main_word] = main_word
            for syn in synonyms:
                reverse[syn] = main_word
        return reverse
    
    def get_synonyms(self, word: str) -> list[str]:
        """获取词的所有同义词（包括自身）"""
        word = word.strip()
        
        # 先查找是否是主词
        if word in self._synonyms:
            return [word] + self._synonyms[word]
        
        # 再查找是否是同义词
        main_word = self._reverse_index.get(word)
        if main_word:
            return [main_word] + self._synonyms.get(main_word, [])
        
        # 未找到同义词
        return [word]
    
    def expand_query(self, query: str) -> str:
        """扩展搜索查询（用 OR 连接同义词）"""
        import jieba
        
        words = list(jieba.cut(query))
        expanded_parts = []
        
        for word in words:
            word = word.strip()
            if len(word) < 2:
                continue
            
            synonyms = self.get_synonyms(word)
            
            if len(synonyms) > 1:
                # 有同义词，用 OR 连接
                expanded_parts.append(f"({' OR '.join(synonyms)})")
            else:
                expanded_parts.append(word)
        
        return " ".join(expanded_parts)
    
    def get_all_synonyms_for_query(self, query: str) -> list[str]:
        """获取查询中所有词的同义词列表"""
        import jieba
        
        words = list(jieba.cut(query))
        all_synonyms = set()
        
        for word in words:
            word = word.strip()
            if len(word) >= 2:
                synonyms = self.get_synonyms(word)
                all_synonyms.update(synonyms)
        
        return list(all_synonyms)
    
    def add_synonym(self, main_word: str, synonyms: list[str]):
        """添加同义词"""
        if main_word in self._synonyms:
            existing = set(self._synonyms[main_word])
            existing.update(synonyms)
            self._synonyms[main_word] = list(existing)
        else:
            self._synonyms[main_word] = synonyms
        
        # 更新反向索引
        for syn in synonyms:
            self._reverse_index[syn] = main_word
    
    def get_main_word(self, word: str) -> Optional[str]:
        """获取词的主词（规范形式）"""
        return self._reverse_index.get(word, word)


# 全局单例
_synonym_dict: Optional[SynonymDict] = None


def get_synonym_dict() -> SynonymDict:
    """获取同义词词典单例"""
    global _synonym_dict
    if _synonym_dict is None:
        _synonym_dict = SynonymDict()
    return _synonym_dict
