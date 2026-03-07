"""数据统计服务 - 增强版数据分析与可视化支持"""

import re
from typing import Optional
from collections import Counter, defaultdict
from dataclasses import dataclass

import pandas as pd

from app.models.document import Document
from app.utils.logger import get_logger

logger = get_logger("data_statistics")


@dataclass
class NumericData:
    """数值数据"""
    value: float
    unit: str
    context: str
    source_file: str
    source_location: str


@dataclass
class DataStatistics:
    """数据统计结果"""
    total_documents: int
    total_paragraphs: int
    total_characters: int
    
    numeric_data_count: int
    percentage_data_count: int
    year_references_count: int
    
    top_keywords: list[tuple[str, int]]
    data_sources: list[dict]
    
    argument_stats: dict
    evidence_stats: dict


class DataStatisticsService:
    """数据统计服务"""
    
    def __init__(self):
        # 数值提取正则
        self._number_pattern = re.compile(
            r'(?P<value>[\d,]+(?:\.\d+)?)\s*(?P<unit>%|万|亿|元|美元|人|个|家|项|次|件|套|吨|公斤|米|公里|平方米|亩|度|瓦|千瓦)?'
        )
        self._percentage_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*%')
        self._year_pattern = re.compile(r'(19|20)\d{2}年?')
        self._currency_pattern = re.compile(r'[\d,]+(?:\.\d+)?\s*(万元|亿元|元|美元|万美元|亿美元)')
    
    def extract_numeric_data(self, text: str, source_file: str = "") -> list[NumericData]:
        """从文本中提取数值数据"""
        results = []
        
        for match in self._number_pattern.finditer(text):
            value_str = match.group("value").replace(",", "")
            unit = match.group("unit") or ""
            
            try:
                value = float(value_str)
                if value == 0:
                    continue
                
                # 获取上下文
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].strip()
                
                results.append(NumericData(
                    value=value,
                    unit=unit,
                    context=context,
                    source_file=source_file,
                    source_location=f"位置 {match.start()}"
                ))
            except ValueError:
                continue
        
        return results
    
    def extract_percentages(self, text: str) -> list[tuple[float, str]]:
        """提取百分比数据"""
        results = []
        
        for match in self._percentage_pattern.finditer(text):
            try:
                value = float(match.group(1))
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].strip()
                results.append((value, context))
            except ValueError:
                continue
        
        return results
    
    def extract_year_references(self, text: str) -> list[str]:
        """提取年份引用"""
        return list(set(self._year_pattern.findall(text)))
    
    def extract_currency_values(self, text: str) -> list[tuple[str, str]]:
        """提取货币数值"""
        results = []
        
        for match in self._currency_pattern.finditer(text):
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].strip()
            results.append((match.group(0), context))
        
        return results
    
    def analyze_documents(self, documents: list[Document]) -> DataStatistics:
        """分析文档集合的统计数据"""
        total_characters = 0
        total_paragraphs = 0
        all_numeric_data = []
        all_percentages = []
        all_years = []
        keyword_counter = Counter()
        
        for doc in documents:
            text = doc.full_text
            total_characters += len(text)
            total_paragraphs += len(doc.paragraphs)
            
            # 提取数值
            numeric_data = self.extract_numeric_data(text, doc.file_name)
            all_numeric_data.extend(numeric_data)
            
            # 提取百分比
            percentages = self.extract_percentages(text)
            all_percentages.extend(percentages)
            
            # 提取年份
            years = self.extract_year_references(text)
            all_years.extend(years)
            
            # 关键词统计
            try:
                import jieba.analyse
                keywords = jieba.analyse.extract_tags(text[:5000], topK=20)
                for kw in keywords:
                    keyword_counter[kw] += 1
            except Exception:
                pass
        
        return DataStatistics(
            total_documents=len(documents),
            total_paragraphs=total_paragraphs,
            total_characters=total_characters,
            numeric_data_count=len(all_numeric_data),
            percentage_data_count=len(all_percentages),
            year_references_count=len(set(all_years)),
            top_keywords=keyword_counter.most_common(30),
            data_sources=[],
            argument_stats={},
            evidence_stats={}
        )
    
    def analyze_excel_data(self, df: pd.DataFrame) -> dict:
        """分析 Excel 数据"""
        analysis = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "numeric_columns": [],
            "text_columns": [],
            "summary_stats": {}
        }
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                analysis["numeric_columns"].append(col)
                analysis["summary_stats"][col] = {
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "sum": float(df[col].sum()) if not pd.isna(df[col].sum()) else None,
                }
            else:
                analysis["text_columns"].append(col)
        
        return analysis
    
    def format_data_reference(
        self,
        value: float,
        unit: str,
        context: str,
        source: str,
        style: str = "apa"
    ) -> str:
        """格式化数据引用"""
        formatted_value = f"{value:,.2f}" if value % 1 != 0 else f"{int(value):,}"
        
        if style == "apa":
            return f"{formatted_value}{unit}（{source}）"
        elif style == "mla":
            return f"{formatted_value}{unit} ({source})"
        else:
            return f"{formatted_value}{unit} - 来源：{source}"
    
    def generate_chart_data(
        self,
        data: list[tuple[str, float]],
        chart_type: str = "bar"
    ) -> dict:
        """生成图表数据（用于前端渲染）"""
        labels = [item[0] for item in data]
        values = [item[1] for item in data]
        
        return {
            "type": chart_type,
            "labels": labels,
            "values": values,
            "datasets": [{
                "data": values,
                "backgroundColor": self._generate_colors(len(values))
            }]
        }
    
    def _generate_colors(self, count: int) -> list[str]:
        """生成图表颜色"""
        base_colors = [
            "#6366F1", "#8B5CF6", "#EC4899", "#F43F5E", "#F97316",
            "#EAB308", "#22C55E", "#14B8A6", "#06B6D4", "#3B82F6"
        ]
        return [base_colors[i % len(base_colors)] for i in range(count)]


def get_document_statistics(documents: list[Document]) -> dict:
    """获取文档统计信息（简化接口）"""
    service = DataStatisticsService()
    stats = service.analyze_documents(documents)
    
    return {
        "total_documents": stats.total_documents,
        "total_paragraphs": stats.total_paragraphs,
        "total_characters": stats.total_characters,
        "numeric_data_count": stats.numeric_data_count,
        "percentage_data_count": stats.percentage_data_count,
        "year_references_count": stats.year_references_count,
        "top_keywords": stats.top_keywords[:15],
    }


def extract_data_for_chart(documents: list[Document], keyword: str) -> list[dict]:
    """提取与关键词相关的数据用于图表"""
    service = DataStatisticsService()
    results = []
    
    for doc in documents:
        text = doc.full_text
        if keyword.lower() not in text.lower():
            continue
        
        # 提取数值数据
        numeric_data = service.extract_numeric_data(text, doc.file_name)
        
        for data in numeric_data:
            if keyword.lower() in data.context.lower():
                results.append({
                    "value": data.value,
                    "unit": data.unit,
                    "context": data.context,
                    "source": data.source_file
                })
    
    return results[:20]  # 最多返回20条


def format_statistics_markdown(stats: dict) -> str:
    """将统计数据格式化为 Markdown"""
    lines = [
        "## 文档库统计",
        "",
        f"- **文档总数**: {stats['total_documents']}",
        f"- **段落总数**: {stats['total_paragraphs']}",
        f"- **字符总数**: {stats['total_characters']:,}",
        "",
        "### 数据提取",
        "",
        f"- 数值数据: {stats['numeric_data_count']} 条",
        f"- 百分比数据: {stats['percentage_data_count']} 条",
        f"- 年份引用: {stats['year_references_count']} 个",
        "",
        "### 热门关键词",
        "",
    ]
    
    for kw, count in stats.get("top_keywords", [])[:10]:
        lines.append(f"- {kw}: {count} 次")
    
    return "\n".join(lines)
