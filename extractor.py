# -*- coding: utf-8 -*-
"""
数字贸易新闻信息提取器
基于 data_sample.py 中的新闻数据提取国家、类型、情绪和主题信息

主要功能：
1. 从新闻标题和正文中提取国家/地区信息
2. 判断新闻类型（regulation/cooperation/restriction等）
3. 分析新闻情绪（restrictive/positive/neutral）
4. 识别新闻主题（data localization/digital trade agreement等）
5. 合并 analyzer.py 的分析结果
6. 输出完整的 DataFrame 和统计摘要
"""

# 导入需要的库
import pandas as pd

# 从 data_sample.py 导入新闻列表
from data_sample import news_list

# 从 analyzer.py 导入分析函数（用于获取已有的标签）
from analyzer import analyze_news


def extract_country(text):
    """
    从文本中提取国家/地区或平台信息
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
    返回：
        str: 匹配到的国家/地区或平台名称，如果未匹配到返回"Other"
    """
    # 定义国家/地区和平台的关键词映射
    # 格式：关键词列表 -> 标准名称
    country_mappings = [
        (["eu", "european union"], "EU"),
        (["us", "united states", "america"], "US"),
        (["china"], "China"),
        (["russia"], "Russia"),
        (["india"], "India"),
        (["brazil"], "Brazil"),
        (["uk", "britain"], "UK"),
        (["japan"], "Japan"),
        (["singapore"], "Singapore"),
        (["california"], "California"),
        (["france"], "France"),
        (["amazon"], "Amazon"),
        (["meta"], "Meta"),
        (["apple"], "Apple")
    ]
    
    # 将文本转换为小写进行匹配
    text_lower = text.lower()
    
    # 按顺序检查每个国家/平台的关键词
    for keywords, country in country_mappings:
        for keyword in keywords:
            if keyword in text_lower:
                return country
    
    # 如果没有匹配到任何国家/平台，返回"Other"
    return "Other"


def extract_type(text):
    """
    判断新闻类型
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
    返回：
        str: 新闻类型，从以下选项中选择：
             regulation / cooperation / restriction / taxation / 
             expansion / compliance / data_protection
    """
    # 定义各类新闻类型的关键词
    type_keywords = {
        "regulation": ["regulation", "regulatory", "rule", "policy"],
        "cooperation": ["cooperation", "partnership", "agreement", 
                        "collaborate", "bilateral", "multilateral"],
        "restriction": ["restriction", "ban", "block", "prohibit", 
                        "limit", "restrict"],
        "taxation": ["tax", "tariff", "levy", "duty", "impose"],
        "expansion": ["expand", "expansion", "launch", "extend", 
                      "expand to", "new market"],
        "compliance": ["compliance", "comply", "enforce", "mandatory"],
        "data_protection": ["data protection", "privacy", "gdpr", 
                           "personal data", "data security"]
    }
    
    text_lower = text.lower()
    
    # 按优先级顺序检查各类关键词
    # 注意：有些关键词可能出现在多个类别中，所以检查顺序很重要
    for news_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return news_type
    
    # 如果没有匹配到任何类型，返回"other"
    return "other"


def extract_sentiment(text):
    """
    判断新闻情绪
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
    返回：
        str: 情绪类型，从以下选项中选择：
             restrictive / positive / neutral
    """
    # 定义情绪关键词
    restrictive_words = [
        "restriction", "ban", "block", "prohibit", "fine", "penalize",
        "tax", "tariff", "levy", "investigate", "scrutiny", "sanction",
        "barrier", "require", "mandatory", "enforce", "regulation",
        "compliance", "data localization", "privacy law", "antitrust"
    ]
    
    positive_words = [
        "cooperation", "agreement", "partnership", "expand", "launch",
        "facilitate", "free flow", "open", "liberalization",
        "digital trade", "data sharing", "connectivity", "collaborate",
        "mutual recognition", "interoperability"
    ]
    
    text_lower = text.lower()
    
    # 统计限制型和积极型关键词出现次数
    restrictive_count = sum(1 for word in restrictive_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)
    
    # 判断情绪
    if restrictive_count > positive_count:
        return "restrictive"
    elif positive_count > restrictive_count:
        return "positive"
    else:
        return "neutral"


def extract_topic(text):
    """
    识别新闻主题
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
    返回：
        str: 新闻主题，从以下选项中选择：
             data localization / digital trade agreement / platform regulation /
             AI trade policy / e-commerce / privacy law / antitrust / digital tax
    """
    # 定义主题关键词映射
    topic_mappings = [
        ("data localization", ["data localization", "local storage", "domestic server"]),
        ("digital trade agreement", ["digital trade agreement", "digital partnership",
                                    "bilateral agreement", "digital economy agreement"]),
        ("platform regulation", ["platform", "antitrust", "competition", "investigation"]),
        ("AI trade policy", ["ai", "artificial intelligence", "chip", "semiconductor"]),
        ("e-commerce", ["e-commerce", "online retail", "cross-border trade", "amazon", "shopee"]),
        ("privacy law", ["privacy", "gdpr", "data protection", "personal data"]),
        ("antitrust", ["antitrust", "monopoly", "anti-competitive"]),
        ("digital tax", ["digital tax", "digital services tax", "tech levy"])
    ]
    
    text_lower = text.lower()
    
    # 按顺序检查每个主题的关键词
    for topic, keywords in topic_mappings:
        for keyword in keywords:
            if keyword in text_lower:
                return topic
    
    # 如果没有匹配到任何主题，返回"other"
    return "other"


def extract_and_merge():
    """
    主函数：提取信息并合并分析结果
    
    返回：
        DataFrame: 包含所有提取字段和分析结果的完整数据表
    """
    # ========== 1. 提取每条新闻的信息 ==========
    
    # 存储提取结果
    extraction_results = []
    
    for news in news_list:
        # 组合标题和正文进行分析
        full_text = news["title"] + " " + news["content"]
        
        # 提取各项信息
        country = extract_country(full_text)
        news_type = extract_type(full_text)
        sentiment = extract_sentiment(full_text)
        topic = extract_topic(full_text)
        
        # 记录提取结果
        extraction_results.append({
            "标题": news["title"],
            "来源": news["source"],
            "日期": news["date"],
            "国家": country,
            "类型": news_type,
            "情绪": sentiment,
            "主题": topic
        })
    
    # 将提取结果转换为 DataFrame
    extract_df = pd.DataFrame(extraction_results)
    
    # ========== 2. 获取 analyzer.py 的分析结果 ==========
    
    # 调用 analyze_news 的逻辑来获取标签信息
    # 为了保持简洁，我们直接复制 analyzer.py 的分析逻辑来获取标签
    
    # 定义关键词（与 analyzer.py 保持一致）
    open_keywords = [
        "cross-border cooperation", "free flow of data", "digital partnership",
        "e-commerce expansion", "trade facilitation", "digital trade agreement",
        "data sharing", "digital connectivity", "open data", "bilateral agreement",
        "multilateral", "liberalization", "interoperability", "mutual recognition",
        "digital economy agreement", "expand", "launch", "partner", "collaborate",
        "facilitate", "streamline"
    ]
    
    restriction_keywords = [
        "restriction", "ban", "tariff", "digital tax", "data localization",
        "cybersecurity review", "fine", "regulation", "compliance", "antitrust",
        "privacy law", "data protection", "mandatory", "enforce", "prohibit",
        "block", "sanction", "barrier", "levy", "investigate", "scrutiny",
        "penalize", "require", "localization", "sovereignty"
    ]
    
    # 获取每条新闻的标签
    labels = []
    for news in news_list:
        title = news["title"].lower()
        content = news["content"].lower()
        full_text = title + " " + content
        
        open_count = sum(1 for kw in open_keywords if kw.lower() in full_text)
        restrict_count = sum(1 for kw in restriction_keywords if kw.lower() in full_text)
        
        # 应用分类逻辑
        if open_count > restrict_count:
            labels.append("开放型")
        elif restrict_count > open_count:
            labels.append("限制型")
        elif open_count == restrict_count and open_count > 0:
            labels.append("限制型")
        else:
            labels.append("中性")
    
    # ========== 3. 合并数据 ==========
    
    # 将标签添加到提取结果 DataFrame 中
    extract_df["新闻标签"] = labels
    
    # ========== 4. 计算统计摘要 ==========
    
    # 国家出现次数统计
    country_stats = extract_df["国家"].value_counts().reset_index()
    country_stats.columns = ["国家", "出现次数"]
    
    # 主题出现次数统计
    topic_stats = extract_df["主题"].value_counts().reset_index()
    topic_stats.columns = ["主题", "出现次数"]
    
    # ========== 5. 输出结果 ==========
    
    print("=" * 70)
    print("          数字贸易新闻信息提取报告")
    print("=" * 70)
    
    # 打印完整的 DataFrame
    print("\n【详细提取结果】")
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_colwidth', 40)
    print(extract_df.to_string(index=False))
    
    # 打印统计摘要
    print("\n" + "=" * 70)
    print("          统计摘要")
    print("=" * 70)
    
    print("\n【国家/地区分布】")
    print(country_stats.to_string(index=False))
    
    print("\n【主题分布】")
    print(topic_stats.to_string(index=False))
    
    # 返回完整的 DataFrame（方便其他程序调用）
    return extract_df


# 如果直接运行此文件，则执行提取和合并函数
if __name__ == "__main__":
    extract_and_merge()
