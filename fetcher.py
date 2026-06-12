# -*- coding: utf-8 -*-
"""
数字贸易新闻抓取器
从多个RSS源抓取最新科技/贸易相关新闻

主要功能：
1. 从多个RSS源抓取新闻
2. 过滤与数字贸易相关的新闻
3. 整理成统一格式的列表
4. 保存为JSON文件供其他模块使用
"""

# 导入需要的库
import feedparser  # 用于解析RSS订阅源
import json        # 用于保存JSON文件
from datetime import datetime  # 用于处理日期格式


def fetch_rss_feed(url, source_name):
    """
    从单个RSS源抓取新闻
    
    参数：
        url (str): RSS源的网址
        source_name (str): 来源名称（如"TechCrunch"）
    
    返回：
        list: 抓取到的新闻列表，每条新闻是一个字典
    """
    # 用于存储从该RSS源抓取的新闻
    news_items = []
    
    try:
        # 解析RSS源，获取所有条目
        # feedparser会自动处理XML格式的RSS数据
        feed = feedparser.parse(url)
        
        # 遍历RSS中的每条新闻
        # feed.entries 包含了所有新闻条目
        for entry in feed.entries:
            # 提取新闻的基本信息
            # 注意：不同RSS源的字段可能略有不同，这里使用常见的字段名
            title = entry.get('title', '')  # 获取标题，如果不存在则返回空字符串
            summary = entry.get('summary', '')  # 获取摘要/内容
            
            # 获取发布日期
            # RSS中日期字段可能有不同的名字，我们尝试几种常见的
            published = entry.get('published', '') or entry.get('updated', '')
            
            # 将日期统一格式化为 YYYY-MM-DD
            # feedparser会自动解析日期为结构化数据
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # 使用解析后的日期结构（元组格式）
                date_obj = datetime(*entry.published_parsed[:6])
                date_str = date_obj.strftime('%Y-%m-%d')
            else:
                # 如果无法解析日期，使用当前日期作为默认值
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # 将提取的信息组成字典
            news_item = {
                'title': title,
                'content': summary,
                'source': source_name,
                'date': date_str
            }
            
            # 添加到列表中
            news_items.append(news_item)
        
        return news_items
        
    except Exception as e:
        # 如果网络请求失败或解析出错，打印错误信息并返回空列表
        # 这样不会影响其他RSS源的抓取
        print(f"警告：从 {source_name} 抓取新闻时出错：{str(e)}")
        return []


def filter_trade_news(news_list):
    """
    过滤与数字贸易相关的新闻
    
    参数：
        news_list (list): 原始新闻列表
    
    返回：
        list: 过滤后只保留数字贸易相关的新闻
    """
    # 定义数字贸易相关的关键词
    # 只保留标题或摘要中包含这些关键词的新闻
    keywords = [
        'digital',      # 数字的
        'trade',        # 贸易
        'data',         # 数据
        'AI',           # 人工智能
        'platform',     # 平台
        'e-commerce',   # 电子商务
        'ecommerce',    # 电子商务（不带连字符的写法）
        'regulation',   # 监管
        'privacy',      # 隐私
        'tariff',       # 关税
        'tech'          # 科技
    ]
    
    # 存储过滤后的新闻
    filtered_news = []
    
    for news in news_list:
        # 将标题和摘要合并，转换为小写以便不区分大小写匹配
        text = (news['title'] + ' ' + news['content']).lower()
        
        # 检查是否包含任意一个关键词
        # 使用 any() 函数：只要有一个关键词匹配就返回True
        if any(keyword.lower() in text for keyword in keywords):
            filtered_news.append(news)
    
    return filtered_news


def fetch_all_news():
    """
    主函数：从所有RSS源抓取并过滤新闻
    
    返回：
        list: 过滤后的新闻列表（real_news_list）
    """
    print("=" * 60)
    print("          数字贸易新闻抓取")
    print("=" * 60)
    
    # 定义要抓取的RSS源
    # 格式：(RSS网址, 来源名称)
    rss_sources = [
        ('https://techcrunch.com/feed/', 'TechCrunch'),
        ('http://feeds.bbci.co.uk/news/technology/rss.xml', 'BBC'),
        ('https://www.theverge.com/rss/index.xml', 'The Verge'),
        ('https://www.wired.com/feed/rss', 'Wired')
    ]
    
    # 存储所有抓取到的新闻（过滤前）
    all_raw_news = []
    
    # 存储统计信息，用于打印报告
    stats = []
    
    # 逐个RSS源抓取
    for url, source_name in rss_sources:
        print(f"\n正在从 {source_name} 抓取新闻...")
        
        # 抓取该RSS源的新闻
        raw_news = fetch_rss_feed(url, source_name)
        
        # 记录该源抓取到的数量
        raw_count = len(raw_news)
        
        # 过滤数字贸易相关的新闻
        filtered = filter_trade_news(raw_news)
        filtered_count = len(filtered)
        
        # 保存统计信息
        stats.append({
            'source': source_name,
            'raw_count': raw_count,
            'filtered_count': filtered_count
        })
        
        # 将过滤后的新闻加入总列表
        all_raw_news.extend(filtered)
        
        print(f"  抓到 {raw_count} 条，过滤后剩 {filtered_count} 条")
    
    return all_raw_news, stats


# ========== 主程序 ==========

if __name__ == "__main__":
    # 执行抓取
    real_news_list, stats = fetch_all_news()
    
    # 打印统计摘要
    print("\n" + "=" * 60)
    print("          抓取结果统计")
    print("=" * 60)
    
    for stat in stats:
        print(f"{stat['source']}: 原始 {stat['raw_count']} 条 → 过滤后 {stat['filtered_count']} 条")
    
    print(f"\n总计过滤后新闻：{len(real_news_list)} 条")
    
    # 打印前5条新闻的标题和来源
    print("\n" + "=" * 60)
    print("          前5条新闻预览")
    print("=" * 60)
    
    for i, news in enumerate(real_news_list[:5], 1):
        print(f"\n{i}. [{news['source']}] {news['date']}")
        print(f"   {news['title'][:80]}...")  # 只显示前80个字符
    
    # 如果抓取到新闻，保存为JSON文件
    if len(real_news_list) > 0:
        # 定义保存的文件名
        output_file = 'real_news.json'
        
        # 将新闻列表保存为JSON格式
        # ensure_ascii=False 确保中文正常显示，indent=2 美化格式
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(real_news_list, f, ensure_ascii=False, indent=2)
        
        print(f"\n已将 {len(real_news_list)} 条新闻保存到 {output_file}")
    else:
        print("\n未抓取到任何新闻，跳过保存文件。")
