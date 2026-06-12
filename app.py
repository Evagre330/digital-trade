# -*- coding: utf-8 -*-
"""
数字贸易新闻智能分析系统 - Streamlit Web应用
基于 data_sample.py 和 real_news.json 的新闻数据进行可视化和分析

主要功能：
1. 支持模拟数据和真实数据两种数据源
2. 计算并展示 DTOI 和 RRI 关键指数
3. 生成7种可视化图表
4. 展示详细的新闻分析表格
"""

# ========== 1. 导入必要的库 ==========
import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import json
import feedparser
import os
from datetime import datetime

# 配置中文字体，解决 matplotlib 中文乱码问题
plt.style.use('seaborn-v0_8-whitegrid')

# 尝试加载项目目录下的中文字体文件
font_path = os.path.join(os.path.dirname(__file__), 'NotoSansSC-Regular.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    matplotlib.rcParams['font.sans-serif'] = ['Noto Sans SC']
else:
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 13
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.titleweight'] = 'bold'

# 统一配色方案
COLORS = {
    'restrictive': '#C0392B',  # 限制型/负面：深红
    'open': '#2E86AB',          # 开放型/正面：商务蓝
    'neutral': '#95A5A6'        # 中性：中灰
}
MULTI_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37']


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


def classify_news_label(title, content):
    """
    根据关键词匹配为新闻打标签
    
    参数：
        title (str): 新闻标题
        content (str): 新闻正文
    
    返回：
        str: 标签（开放型/限制型/中性）
    """
    full_text = (title + " " + content).lower()
    
    # 统计开放型和限制型关键词出现次数
    open_count = sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
    restrict_count = sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
    
    # 应用分类逻辑：偏保守判断
    if open_count > restrict_count:
        return "开放型"
    elif restrict_count > open_count:
        return "限制型"
    elif open_count == restrict_count and open_count > 0:
        return "限制型"
    else:
        return "中性"


def extract_country(text):
    """
    从文本中提取国家/地区或平台信息
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
    返回：
        str: 匹配到的国家/地区或平台名称
    """
    # 定义国家/地区和平台的关键词映射
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
    判断新闻类型
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
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
    判断新闻情绪
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
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
    识别新闻主题
    
    参数：
        text (str): 要分析的文本（标题+正文）
    
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


def analyze_news_list(news_list):
    """
    分析新闻列表，返回完整的数据框和分析结果
    
    参数：
        news_list (list): 新闻列表
    
    返回：
        tuple: (DataFrame, dto, rii, total_news)
    """
    results = []
    
    # 遍历每条新闻，提取信息和分类
    for news in news_list:
        title = news.get("title", "")
        content = news.get("content", "")
        source = news.get("source", "")
        date = news.get("date", "")
        
        full_text = title + " " + content
        
        # 提取各项信息
        country = extract_country(full_text)
        news_type = extract_type(full_text)
        sentiment = extract_sentiment(full_text)
        topic = extract_topic(full_text)
        label = classify_news_label(title, content)
        
        results.append({
            "标题": title,
            "来源": source,
            "日期": date,
            "国家": country,
            "类型": news_type,
            "情绪": sentiment,
            "主题": topic,
            "标签": label
        })
    
    # 创建 DataFrame
    df = pd.DataFrame(results)
    
    # 计算指数
    total_news = len(df)
    open_count = len(df[df["标签"] == "开放型"])
    restriction_count = len(df[df["标签"] == "限制型"])
    
    # DTOI: 数字贸易开放指数
    dto = (open_count - restriction_count) / total_news if total_news > 0 else 0
    
    # 计算关键词总数用于 RII
    total_open_kw = 0
    total_restrict_kw = 0
    for news in news_list:
        full_text = (news.get("title", "") + " " + news.get("content", "")).lower()
        total_open_kw += sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
        total_restrict_kw += sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
    
    # RII: 限制强度指数
    total_keywords = total_open_kw + total_restrict_kw
    rii = total_restrict_kw / total_keywords if total_keywords > 0 else 0
    
    return df, dto, rii, total_news


def fetch_rss_news(rss_url):
    """
    从自定义RSS源抓取新闻
    
    参数：
        rss_url (str): RSS源地址
    
    返回：
        list: 抓取到的新闻列表
    """
    news_items = []
    
    try:
        # 解析RSS源
        feed = feedparser.parse(rss_url)
        
        # 提取来源名称
        source_name = feed.feed.get('title', 'Custom RSS')[:30]
        
        # 遍历新闻条目
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '') or entry.get('description', '')
            
            # 处理日期
            published = entry.get('published', '') or entry.get('updated', '')
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                date_obj = datetime(*entry.published_parsed[:6])
                date_str = date_obj.strftime('%Y-%m-%d')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            news_items.append({
                'title': title,
                'content': summary,
                'source': source_name,
                'date': date_str
            })
        
        return news_items
        
    except Exception as e:
        st.error(f"抓取RSS源失败：{str(e)}")
        return []


def create_chart1(df):
    """图表1：饼图 - 新闻类型分布"""
    fig, ax = plt.subplots(figsize=(6, 4))
    label_counts = df["标签"].value_counts()
    colors = []
    for label in label_counts.index:
        if label == '开放型':
            colors.append(COLORS['open'])
        elif label == '限制型':
            colors.append(COLORS['restrictive'])
        else:
            colors.append(COLORS['neutral'])
    ax.pie(label_counts.values, labels=label_counts.index, colors=colors,
           autopct='%1.1f%%', startangle=90, textprops={'fontsize': 13}, shadow=False)
    ax.set_title('数字贸易新闻类型分布', fontsize=16, fontweight='bold')
    return fig


def create_chart2(df):
    """图表2：柱状图 - 国家分布"""
    fig, ax = plt.subplots(figsize=(8, 4))
    country_counts = df["国家"].value_counts()
    bars = ax.bar(country_counts.index, country_counts.values, width=0.6, 
                  color=MULTI_COLORS[:len(country_counts)])
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                ha='center', va='bottom', fontsize=13)
    ax.set_title('新闻涉及国家/地区分布', fontsize=16, fontweight='bold')
    ax.set_xlabel('国家/地区')
    ax.set_ylabel('出现次数')
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig


def create_chart3(df):
    """图表3：柱状图 - 主题分布"""
    fig, ax = plt.subplots(figsize=(8, 4))
    topic_counts = df["主题"].value_counts()
    bars = ax.bar(topic_counts.index, topic_counts.values, width=0.6, 
                  color=MULTI_COLORS[:len(topic_counts)])
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                ha='center', va='bottom', fontsize=13)
    ax.set_title('数字贸易热点主题分布', fontsize=16, fontweight='bold')
    ax.set_xlabel('主题')
    ax.set_ylabel('出现次数')
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig


def create_chart4(df):
    """图表4：折线图 - 月度趋势"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    
    # 提取月份
    df_copy = df.copy()
    df_copy['月份'] = pd.to_datetime(df_copy['日期']).dt.month
    
    # 左图：月度新闻数量趋势
    ax1 = axes[0]
    monthly_data = df_copy.groupby(['月份', '标签'])['标题'].count().unstack(fill_value=0)
    ax1.plot(monthly_data.index, monthly_data.get('开放型', 0), marker='o', linestyle='-',
             color=COLORS['open'], linewidth=2.5, markersize=8, label='开放型')
    ax1.plot(monthly_data.index, monthly_data.get('限制型', 0), marker='s', linestyle='--',
             color=COLORS['restrictive'], linewidth=2.5, markersize=8, label='限制型')
    ax1.set_title('开放型vs限制型新闻月度趋势', fontsize=16, fontweight='bold')
    ax1.set_xlabel('月份')
    ax1.set_ylabel('新闻数量')
    plt.sca(ax1)
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    ax1.legend()
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 右图：关键词词频变化
    ax2 = axes[1]
    monthly_open_kw = []
    monthly_restrict_kw = []
    for month in range(1, 7):
        open_kw = 0
        restrict_kw = 0
        for _, row in df_copy[df_copy['月份'] == month].iterrows():
            full_text = (row['标题'] + " " + str(row.get('类型', ''))).lower()
            open_kw += sum(1 for kw in OPEN_KEYWORDS if kw.lower() in full_text)
            restrict_kw += sum(1 for kw in RESTRICTION_KEYWORDS if kw.lower() in full_text)
        monthly_open_kw.append(open_kw)
        monthly_restrict_kw.append(restrict_kw)
    
    ax2.plot(range(1, 7), monthly_open_kw, marker='o', linestyle='-',
             color=COLORS['open'], linewidth=2.5, markersize=8, label='开放型关键词')
    ax2.plot(range(1, 7), monthly_restrict_kw, marker='s', linestyle='--',
             color=COLORS['restrictive'], linewidth=2.5, markersize=8, label='限制型关键词')
    ax2.set_title('关键词月度词频变化', fontsize=16, fontweight='bold')
    ax2.set_xlabel('月份')
    ax2.set_ylabel('关键词出现次数')
    plt.sca(ax2)
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    ax2.legend()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig


def create_chart5(df):
    """图表5：热力图 - 各国议题"""
    fig, ax = plt.subplots(figsize=(8, 5))
    df_copy = df.copy()
    df_copy['月份'] = pd.to_datetime(df_copy['日期']).dt.month
    heatmap_data = df_copy.groupby(['国家', '主题'])['标题'].count().unstack(fill_value=0)
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d', linewidths=0.5,
                cbar_kws={'label': '新闻数量'}, ax=ax)
    ax.set_title('各国数字贸易议题热力图', fontsize=16, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig


# ========== 3. Streamlit 页面配置 ==========
st.set_page_config(
    page_title="数字贸易新闻智能分析系统",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== 4. 侧边栏 - 数据源选择 ==========
# 侧边栏标题和说明
st.sidebar.markdown("## 🌐 数字贸易新闻智能分析系统")
st.sidebar.markdown("本系统自动抓取、分类、分析全球数字贸易新闻，实时计算开放度与监管强度指数。")
st.sidebar.markdown("---")

# 数据源选择
st.sidebar.markdown("### 📊 数据来源")
data_source = st.sidebar.radio(
    "请选择数据源：",
    options=["使用模拟数据", "使用真实新闻数据"],
    index=0
)

# 自定义RSS源输入框
st.sidebar.markdown("---")
custom_rss = st.sidebar.text_input(
    "📡 自定义RSS源（可选）",
    placeholder="粘贴RSS地址，如：`https://techcrunch.com/feed/`",
    help="输入任意RSS地址，系统将自动抓取并分析最新新闻"
)

st.sidebar.markdown("---")

# 开始分析按钮
if st.sidebar.button("🚀 开始分析", type="primary", use_container_width=True):
    # 动态加载过程
    with st.status("正在分析中...", expanded=True) as status:
        # 第一步：加载数据
        st.write("📡 正在加载新闻数据...")
        
        # 初始化新闻数据
        news_list_data = None
        
        # 第一步：检查是否有自定义RSS源
        if custom_rss.strip():
            st.write(f"🔗 正在从自定义RSS源抓取新闻...")
            # 调用RSS抓取函数
            news_list_data = fetch_rss_news(custom_rss.strip())
            
            # 检查抓取结果
            if news_list_data and len(news_list_data) > 0:
                st.sidebar.success(f"✅ 已从自定义RSS抓取到 {len(news_list_data)} 条新闻")
                st.write(f"✅ 成功抓取到 {len(news_list_data)} 条新闻")
            else:
                st.sidebar.warning("⚠️ 未能从该RSS源获取到新闻，已切换到默认数据")
                news_list_data = None
        
        # 第二步：如果没有自定义RSS数据，使用默认数据源
        if news_list_data is None:
            if data_source == "使用模拟数据":
                # 从 data_sample.py 导入模拟数据
                from data_sample import news_list
                news_list_data = news_list
                st.write("✅ 已加载模拟数据")
            else:
                # 从 real_news.json 加载真实数据
                try:
                    with open('real_news.json', 'r', encoding='utf-8') as f:
                        news_list_data = json.load(f)
                    st.write("✅ 已加载真实新闻数据")
                except FileNotFoundError:
                    st.error("❌ 未找到 real_news.json 文件，请先运行 fetcher.py 获取数据！")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ 加载数据时出错：{str(e)}")
                    st.stop()
        
        # 第二步：分析数据
        st.write("🔍 正在进行关键词分析与分类...")
        df, dto, rii, total_news = analyze_news_list(news_list_data)
        
        # 第三步：生成图表
        st.write("📊 正在生成可视化图表...")
        
        # 完成状态更新
        status.update(label="分析完成！", state="complete")
    
    # ========== 5. 主页面 - 关键指数卡片 ==========
    st.title("数字贸易新闻智能分析系统")
    st.markdown("---")
    
    # 指标卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="DTOI 数字贸易开放指数",
            value=f"{dto:.4f}",
            delta="正值表示开放趋势" if dto > 0 else ("负值表示限制趋势" if dto < 0 else "中性"),
            help="数字贸易开放指数 = (开放类新闻 - 限制类新闻) / 总新闻数。正值表示开放趋势，负值表示限制趋势，范围-1到+1"
        )
    with col2:
        st.metric(
            label="RRI 监管强度指数",
            value=f"{rii:.4f}",
            delta="限制性关键词占比" if rii > 0 else "无限制性关键词",
            help="监管强度指数 = 限制型关键词出现次数 / 全部关键词出现次数。数值越高说明监管新闻越密集，范围0到1"
        )
    with col3:
        st.metric(
            label="新闻总条数",
            value=f"{total_news}",
            delta="条",
            help="本次分析的新闻样本总量"
        )
    
    st.markdown("---")
    
    # ========== 6. 主页面 - 图表展示 ==========
    st.subheader("可视化分析")
    
    # 计算统计数据用于自动解读
    # 新闻分类统计
    label_counts = df["标签"].value_counts()
    label_percent = (label_counts / total_news * 100).round(1)
    
    # 国家分布统计
    country_counts = df["国家"].value_counts()
    top_country = country_counts.index[0]
    top_country_count = country_counts.iloc[0]
    
    # 主题分布统计
    topic_counts = df["主题"].value_counts()
    top_topic = topic_counts.index[0]
    top_topic_count = topic_counts.iloc[0]
    
    # 月度趋势数据
    df['月份'] = pd.to_datetime(df['日期']).dt.month
    monthly_data = df.groupby(['月份', '标签'])['标题'].count().unstack(fill_value=0)
    latest_month = df['月份'].max()
    
    # 热力图数据（最活跃国家和主题）
    heatmap_data = df.groupby(['国家', '主题'])['标题'].count().unstack(fill_value=0)
    country_totals = heatmap_data.sum(axis=1)
    most_active_country = country_totals.idxmax()
    country_top_topic = heatmap_data.loc[most_active_country].idxmax()
    
    # 创建5个标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "新闻分类",
        "国家分布", 
        "热点主题",
        "趋势分析",
        "热力图"
    ])
    
    with tab1:
        st.markdown("#### 开放型/限制型/中性新闻占比")
        fig = create_chart1(df)
        st.pyplot(fig, use_container_width=True)
        # 自动解读
        if "限制型" in label_counts and label_percent["限制型"] == label_percent.max():
            st.info(f"📌 当前样本中限制型新闻占比最高（{label_percent['限制型']}%），反映全球数字贸易整体偏向监管收紧。")
        elif "开放型" in label_counts and label_percent["开放型"] == label_percent.max():
            st.info(f"📌 当前样本中开放型新闻占比最高（{label_percent['开放型']}%），反映全球数字贸易整体呈现开放趋势。")
        else:
            st.info(f"📌 当前样本中新闻类型分布较为均衡，中性新闻占比最高（{label_percent.get('中性', 0)}%）。")
    
    with tab2:
        st.markdown("#### 各国家/地区新闻分布")
        fig = create_chart2(df)
        st.pyplot(fig, use_container_width=True)
        # 自动解读
        st.info(f"📌 {top_country} 是本期数字贸易新闻中涉及最多的国家/地区，共 {top_country_count} 条相关报道。")
    
    with tab3:
        st.markdown("#### 数字贸易热点主题分布")
        fig = create_chart3(df)
        st.pyplot(fig, use_container_width=True)
        # 自动解读
        st.info(f"📌 {top_topic} 是当前最受关注的数字贸易议题，共出现 {top_topic_count} 次。")
    
    with tab4:
        st.markdown("#### 月度趋势分析")
        st.markdown("##### 新闻数量与关键词词频变化")
        fig = create_chart4(df)
        st.pyplot(fig, use_container_width=True)
        # 自动解读
        latest_open = monthly_data.get('开放型', pd.Series([0]*6)).iloc[latest_month-1] if latest_month <= len(monthly_data) else 0
        latest_restrict = monthly_data.get('限制型', pd.Series([0]*6)).iloc[latest_month-1] if latest_month <= len(monthly_data) else 0
        if latest_open > latest_restrict:
            st.info(f"📌 在最新月份（{latest_month}月），开放型新闻数量（{latest_open}条）多于限制型新闻（{latest_restrict}条），显示数字贸易政策环境趋于开放。")
        elif latest_restrict > latest_open:
            st.info(f"📌 在最新月份（{latest_month}月），限制型新闻数量（{latest_restrict}条）多于开放型新闻（{latest_open}条），显示数字贸易监管趋紧。")
        else:
            st.info(f"📌 在最新月份（{latest_month}月），开放型和限制型新闻数量持平，数字贸易政策环境保持平衡。")
    
    with tab5:
        st.markdown("#### 各国数字贸易议题热力图")
        fig = create_chart5(df)
        st.pyplot(fig, use_container_width=True)
        # 自动解读
        st.info(f"📌 {most_active_country} 在数字贸易议题上最为活跃，尤其集中在 {country_top_topic} 领域。")
    
    st.markdown("---")
    
    # ========== 7. 主页面 - 新闻数据表格 ==========
    st.subheader("新闻分析详情表格")
    
    # 显示数据表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "标题": st.column_config.TextColumn(
                "标题",
                width="large"
            ),
            "来源": st.column_config.TextColumn(
                "来源",
                width="medium"
            ),
            "日期": st.column_config.TextColumn(
                "日期",
                width="small"
            ),
            "国家": st.column_config.TextColumn(
                "国家",
                width="small"
            ),
            "类型": st.column_config.TextColumn(
                "类型",
                width="medium"
            ),
            "情绪": st.column_config.TextColumn(
                "情绪",
                width="small"
            ),
            "主题": st.column_config.TextColumn(
                "主题",
                width="medium"
            ),
            "标签": st.column_config.TextColumn(
                "标签",
                width="small"
            )
        }
    )
    
    # 统计信息
    st.markdown("#### 统计摘要")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**国家分布统计**")
        country_stats = df["国家"].value_counts()
        st.write(country_stats)
    
    with col2:
        st.markdown("**主题分布统计**")
        topic_stats = df["主题"].value_counts()
        st.write(topic_stats)

else:
    # 初始状态提示
    st.title("数字贸易新闻智能分析系统")
    st.info("👈 请在左侧侧边栏选择数据源，然后点击「开始分析」按钮")
    
    st.markdown("""
    ### 功能说明
    
    本系统提供以下分析功能：
    
    1. **关键指数** - DTOI数字贸易开放指数、RRI监管强度指数
    
    2. **可视化分析**
       - 新闻分类饼图
       - 国家分布柱状图
       - 热点主题柱状图
       - 月度趋势折线图
       - 国家×主题热力图
    
    3. **详细数据表格** - 包含标题、来源、日期、国家、类型、情绪、主题、标签等字段
    
    ### 数据源
    
    - **模拟数据**：使用 `data_sample.py` 中的15条模拟新闻
    - **真实数据**：使用 `real_news.json` 中的抓取新闻（需先运行 `fetcher.py`）
    """)
