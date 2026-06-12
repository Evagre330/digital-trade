# -*- coding: utf-8 -*-
"""
真实新闻数据分析器
基于 fetcher.py 抓取的真实新闻数据进行分析和可视化

主要功能：
1. 从 real_news.json 文件加载真实新闻数据
2. 复用 analyzer.py 的关键词词典和分类逻辑
3. 复用 extractor.py 的信息提取逻辑
4. 生成分析报告和图表
5. 与模拟数据进行对比分析
"""

# ========== 1. 导入必要的库 ==========
import json
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# 配置中文字体，解决中文乱码问题
plt.style.use('seaborn-v0_8-whitegrid')
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 13
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.titleweight'] = 'bold'

# ========== 2. 复用 analyzer.py 的关键词词典 ==========
# 开放型关键词
OPEN_KEYWORDS = [
    "cross-border cooperation", "free flow of data", "digital partnership",
    "e-commerce expansion", "trade facilitation", "digital trade agreement",
    "data sharing", "digital connectivity", "open data", "bilateral agreement",
    "multilateral", "liberalization", "interoperability", "mutual recognition",
    "digital economy agreement", "expand", "launch", "partner", "collaborate",
    "facilitate", "streamline"
]

# 限制型关键词
RESTRICTION_KEYWORDS = [
    "restriction", "ban", "tariff", "digital tax", "data localization",
    "cybersecurity review", "fine", "regulation", "compliance", "antitrust",
    "privacy law", "data protection", "mandatory", "enforce", "prohibit",
    "block", "sanction", "barrier", "levy", "investigate", "scrutiny",
    "penalize", "require", "localization", "sovereignty"
]

# 统一配色方案
COLORS = {
    'restrictive': '#C0392B',  # 限制型/负面：深红
    'open': '#2E86AB',          # 开放型/正面：商务蓝
    'neutral': '#95A5A6'        # 中性：中灰
}
MULTI_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37']


def analyze_news_label(news_list):
    """
    复用 analyzer.py 的分类逻辑，为每条新闻打标签
    
    参数：
        news_list (list): 新闻列表
    
    返回：
        list: 标签列表
    """
    labels = []
    
    for news in news_list:
        title = news["title"].lower()
        content = news.get("content", "").lower()
        full_text = title + " " + content
        
        open_count = sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
        restrict_count = sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
        
        # 应用分类逻辑：偏保守判断
        if open_count > restrict_count:
            labels.append("开放型")
        elif restrict_count > open_count:
            labels.append("限制型")
        elif open_count == restrict_count and open_count > 0:
            labels.append("限制型")
        else:
            labels.append("中性")
    
    return labels


def extract_country(text):
    """
    复用 extractor.py 的国家提取逻辑
    
    参数：
        text (str): 要分析的文本
    
    返回：
        str: 匹配到的国家/地区或平台名称
    """
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
    
    text_lower = text.lower()
    
    for keywords, country in country_mappings:
        for keyword in keywords:
            if keyword in text_lower:
                return country
    
    return "Other"


def extract_type(text):
    """
    复用 extractor.py 的类型判断逻辑
    
    参数：
        text (str): 要分析的文本
    
    返回：
        str: 新闻类型
    """
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
    
    for news_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return news_type
    
    return "other"


def extract_sentiment(text):
    """
    复用 extractor.py 的情绪分析逻辑
    
    参数：
        text (str): 要分析的文本
    
    返回：
        str: 情绪类型
    """
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
    
    restrictive_count = sum(1 for word in restrictive_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)
    
    if restrictive_count > positive_count:
        return "restrictive"
    elif positive_count > restrictive_count:
        return "positive"
    else:
        return "neutral"


def extract_topic(text):
    """
    复用 extractor.py 的主题识别逻辑
    
    参数：
        text (str): 要分析的文本
    
    返回：
        str: 新闻主题
    """
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
    
    for topic, keywords in topic_mappings:
        for keyword in keywords:
            if keyword in text_lower:
                return topic
    
    return "other"


def generate_charts(df, prefix='real_'):
    """
    生成7张图表，复用 visualize.py 的逻辑
    
    参数：
        df (DataFrame): 包含分析结果的数据表
        prefix (str): 图表文件名前缀
    """
    # 图表1：饼图 - 新闻类型分布
    plt.figure(figsize=(10, 6))
    label_counts = df["新闻标签"].value_counts()
    colors = []
    for label in label_counts.index:
        if label == '开放型':
            colors.append(COLORS['open'])
        elif label == '限制型':
            colors.append(COLORS['restrictive'])
        else:
            colors.append(COLORS['neutral'])
    plt.pie(label_counts.values, labels=label_counts.index, colors=colors,
            autopct='%1.1f%%', startangle=90, textprops={'fontsize': 13}, shadow=False)
    plt.title('数字贸易新闻类型分布')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 0.9))
    plt.savefig(f'{prefix}chart1.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表1已保存：{prefix}chart1.png")
    
    # 图表2：柱状图 - 国家分布
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    country_counts = df["国家"].value_counts()
    bars = ax.bar(country_counts.index, country_counts.values, width=0.6, 
                  color=MULTI_COLORS[:len(country_counts)])
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height}',
                ha='center', va='bottom', fontsize=13)
    ax.set_title('新闻涉及国家/地区分布')
    ax.set_xlabel('国家/地区')
    ax.set_ylabel('出现次数')
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart2.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表2已保存：{prefix}chart2.png")
    
    # 图表3：柱状图 - 主题分布
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    topic_counts = df["主题"].value_counts()
    bars = ax.bar(topic_counts.index, topic_counts.values, width=0.6, 
                  color=MULTI_COLORS[:len(topic_counts)])
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height}',
                ha='center', va='bottom', fontsize=13)
    ax.set_title('数字贸易热点主题分布')
    ax.set_xlabel('主题')
    ax.set_ylabel('出现次数')
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart3.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表3已保存：{prefix}chart3.png")
    
    # 图表4：折线图 - 月度趋势
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    df['月份'] = pd.to_datetime(df['date']).dt.month
    monthly_data = df.groupby(['月份', '新闻标签'])['标题'].count().unstack(fill_value=0)
    ax.plot(monthly_data.index, monthly_data.get('开放型', 0), marker='o', linestyle='-',
            color=COLORS['open'], linewidth=2.5, markersize=8, label='开放型')
    ax.plot(monthly_data.index, monthly_data.get('限制型', 0), marker='s', linestyle='--',
            color=COLORS['restrictive'], linewidth=2.5, markersize=8, label='限制型')
    ax.set_title('开放型vs限制型新闻月度趋势')
    ax.set_xlabel('月份')
    ax.set_ylabel('新闻数量')
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart4.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表4已保存：{prefix}chart4.png")
    
    # 图表5：水平柱状图 - 情绪分布
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    sentiment_data = df.groupby(['国家', '情绪'])['标题'].count().unstack(fill_value=0)
    sentiment_data['总计'] = sentiment_data.sum(axis=1)
    sentiment_data = sentiment_data.sort_values('总计', ascending=True)
    sentiment_data = sentiment_data.drop('总计', axis=1)
    sent_colors = {'restrictive': COLORS['restrictive'], 'positive': COLORS['open'], 'neutral': COLORS['neutral']}
    bottom = pd.Series([0]*len(sentiment_data), index=sentiment_data.index)
    for sentiment in ['restrictive', 'positive', 'neutral']:
        ax.barh(sentiment_data.index, sentiment_data.get(sentiment, 0), left=bottom,
                color=sent_colors.get(sentiment, '#9CA3AF'), label=sentiment)
        bottom += sentiment_data.get(sentiment, 0)
    ax.set_title('各国数字贸易情绪分布')
    ax.set_xlabel('新闻数量')
    ax.set_ylabel('国家/地区')
    handles, labels = ax.get_legend_handles_labels()
    label_mapping = {'restrictive': '限制型', 'positive': '积极型', 'neutral': '中性'}
    new_labels = [label_mapping.get(label, label) for label in labels]
    ax.legend(handles, new_labels)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart5.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表5已保存：{prefix}chart5.png")
    
    # 图表6：热力图 - 各国议题
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    heatmap_data = df.groupby(['国家', '主题'])['标题'].count().unstack(fill_value=0)
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d', linewidths=0.5,
                cbar_kws={'label': '新闻数量'}, ax=ax)
    ax.set_title('各国数字贸易议题热力图')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart6.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表6已保存：{prefix}chart6.png")
    
    # 图表7：折线图 - 关键词词频
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    monthly_open_counts = []
    monthly_restriction_counts = []
    for month in range(1, 7):
        open_count = 0
        restrict_count = 0
        for _, row in df.iterrows():
            if pd.to_datetime(row['date']).month == month:
                full_text = (row['标题'] + " " + str(row.get('content', ''))).lower()
                open_count += sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
                restrict_count += sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
        monthly_open_counts.append(open_count)
        monthly_restriction_counts.append(restrict_count)
    ax.plot(range(1, 7), monthly_open_counts, marker='o', linestyle='-',
            color=COLORS['open'], linewidth=2.5, markersize=8, label='开放型关键词')
    ax.plot(range(1, 7), monthly_restriction_counts, marker='s', linestyle='--',
            color=COLORS['restrictive'], linewidth=2.5, markersize=8, label='限制型关键词')
    ax.set_title('开放型vs限制型关键词月度词频变化')
    ax.set_xlabel('月份')
    ax.set_ylabel('关键词出现次数')
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f'{prefix}chart7.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表7已保存：{prefix}chart7.png")


def main():
    """
    主函数：分析真实新闻数据
    """
    print("=" * 60)
    print("          真实新闻数据分析")
    print("=" * 60)
    
    # 加载真实新闻数据
    try:
        with open('real_news.json', 'r', encoding='utf-8') as f:
            real_news_list = json.load(f)
        print(f"\n成功加载 {len(real_news_list)} 条真实新闻")
    except FileNotFoundError:
        print("错误：未找到 real_news.json 文件，请先运行 fetcher.py")
        return
    except Exception as e:
        print(f"加载文件时出错：{str(e)}")
        return
    
    # 对每条新闻进行信息提取
    extraction_results = []
    for news in real_news_list:
        full_text = news['title'] + " " + news.get('content', '')
        country = extract_country(full_text)
        news_type = extract_type(full_text)
        sentiment = extract_sentiment(full_text)
        topic = extract_topic(full_text)
        
        extraction_results.append({
            "标题": news['title'],
            "来源": news['source'],
            "date": news['date'],
            "国家": country,
            "类型": news_type,
            "情绪": sentiment,
            "主题": topic,
            "content": news.get('content', '')  # 保留用于后续分析
        })
    
    # 创建 DataFrame
    df = pd.DataFrame(extraction_results)
    
    # 添加新闻标签
    df['新闻标签'] = analyze_news_label(real_news_list)
    
    # 计算指数
    total_news = len(df)
    open_count = len(df[df['新闻标签'] == '开放型'])
    restriction_count = len(df[df['新闻标签'] == '限制型'])
    neutral_count = len(df[df['新闻标签'] == '中性'])
    
    # DTOI：数字贸易开放指数
    dto = (open_count - restriction_count) / total_news
    
    # 计算关键词出现次数用于 RII
    total_open_keywords = 0
    total_restriction_keywords = 0
    for _, row in df.iterrows():
        full_text = (row['标题'] + " " + str(row.get('content', ''))).lower()
        total_open_keywords += sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
        total_restriction_keywords += sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
    
    # RII：限制强度指数
    total_keywords = total_open_keywords + total_restriction_keywords
    rii = total_restriction_keywords / total_keywords if total_keywords > 0 else 0
    
    # 打印分析结果
    print("\n【关键指数】")
    print(f"数字贸易开放指数 (DTOI): {dto:.4f}")
    print(f"限制强度指数 (RII): {rii:.4f}")
    
    print("\n【新闻类型分布】")
    print(f"开放型新闻: {open_count}条 ({(open_count/total_news)*100:.1f}%)")
    print(f"限制型新闻: {restriction_count}条 ({(restriction_count/total_news)*100:.1f}%)")
    print(f"中性新闻: {neutral_count}条 ({(neutral_count/total_news)*100:.1f}%)")
    
    print("\n【国家分布】")
    country_stats = df["国家"].value_counts()
    for country, count in country_stats.items():
        print(f"{country}: {count}条")
    
    print("\n【主题分布】")
    topic_stats = df["主题"].value_counts()
    for topic, count in topic_stats.items():
        print(f"{topic}: {count}条")
    
    # 生成图表
    print("\n" + "=" * 60)
    print("          生成图表")
    print("=" * 60)
    generate_charts(df, prefix='real_')
    
    print("\n分析完成！真实新闻数据已生成图表 real_chart1.png ~ real_chart7.png")
    print("\n对比提示：")
    print("- 模拟数据图表：chart1.png ~ chart7.png")
    print("- 真实数据图表：real_chart1.png ~ real_chart7.png")


if __name__ == "__main__":
    main()
