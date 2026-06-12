# -*- coding: utf-8 -*-
"""
数字贸易新闻可视化工具
基于已有的数据和分析结果生成多种图表

主要功能：
1. 配置中文字体，解决matplotlib中文乱码问题
2. 从 analyzer.py 和 extractor.py 获取分析结果
3. 生成7种不同类型的图表并保存为PNG文件
"""

# ========== 1. 导入必要的库 ==========
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns  # 导入seaborn库

# ========== 全局样式设置 ==========
plt.style.use('seaborn-v0_8-whitegrid')
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 13
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.titleweight'] = 'bold'

# ========== 统一配色方案 ==========
COLORS = {
    'restrictive': '#C0392B',  # 限制型/负面：深红
    'open': '#2E86AB',          # 开放型/正面：商务蓝
    'neutral': '#95A5A6'        # 中性：中灰
}
MULTI_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37']

# 从 data_sample.py 导入新闻列表
from data_sample import news_list
# 从 extractor.py 导入提取函数
from extractor import extract_and_merge


def create_chart1(df):
    """
    创建饼图：开放型/限制型/中性新闻的占比
    
    参数：
        df (DataFrame): 包含新闻标签的数据表
    """
    # 统计各类型新闻数量
    label_counts = df["新闻标签"].value_counts()
    
    # 设置颜色（按标签顺序重新排列）
    colors = []
    for label in label_counts.index:
        if label == '开放型':
            colors.append(COLORS['open'])
        elif label == '限制型':
            colors.append(COLORS['restrictive'])
        else:
            colors.append(COLORS['neutral'])
    
    # 创建饼图
    plt.figure(figsize=(10, 6))
    plt.pie(label_counts.values, 
            labels=label_counts.index, 
            colors=colors,
            autopct='%1.1f%%',  # 显示百分比
            startangle=90,       # 起始角度
            textprops={'fontsize': 13},
            shadow=False)        # 去掉阴影
    
    # 添加标题
    plt.title('数字贸易新闻类型分布')
    
    # 添加图例
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 0.9))
    
    # 保存图片
    plt.savefig('chart1.png', dpi=150, bbox_inches='tight')
    print("图表1已保存：chart1.png")
    
    # 关闭当前图形，准备下一张图
    plt.close()


def create_chart2(df):
    """
    创建柱状图：各国家/地区出现次数对比
    
    参数：
        df (DataFrame): 包含国家数据的数据表
    """
    # 统计各国出现次数
    country_counts = df["国家"].value_counts()
    
    # 创建柱状图
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    bars = ax.bar(country_counts.index, 
                  country_counts.values, 
                  width=0.6,  # 柱子宽度设为0.6
                  color=MULTI_COLORS[:len(country_counts)])
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., 
                height,
                f'{height}',
                ha='center', va='bottom', fontsize=13)  # 顶部数字字号13
    
    # 添加标题和标签
    ax.set_title('新闻涉及国家/地区分布')
    ax.set_xlabel('国家/地区')
    ax.set_ylabel('出现次数')
    
    # 旋转x轴标签，避免重叠
    plt.xticks(rotation=45, ha='right')
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart2.png', dpi=150, bbox_inches='tight')
    print("图表2已保存：chart2.png")
    
    plt.close()


def create_chart3(df):
    """
    创建柱状图：各主题出现次数对比
    
    参数：
        df (DataFrame): 包含主题数据的数据表
    """
    # 统计各主题出现次数
    topic_counts = df["主题"].value_counts()
    
    # 创建柱状图
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    bars = ax.bar(topic_counts.index, 
                  topic_counts.values, 
                  width=0.6,  # 柱子宽度设为0.6
                  color=MULTI_COLORS[:len(topic_counts)])
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., 
                height,
                f'{height}',
                ha='center', va='bottom', fontsize=13)  # 顶部数字字号13
    
    # 添加标题和标签
    ax.set_title('数字贸易热点主题分布')
    ax.set_xlabel('主题')
    ax.set_ylabel('出现次数')
    
    # 旋转x轴标签
    plt.xticks(rotation=45, ha='right')
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart3.png', dpi=150, bbox_inches='tight')
    print("图表3已保存：chart3.png")
    
    plt.close()


def create_chart4(df):
    """
    创建折线图：按月份显示开放型和限制型新闻数量的变化趋势
    
    参数：
        df (DataFrame): 包含日期和标签数据的数据表
    """
    # 从日期字段提取月份
    df['月份'] = pd.to_datetime(df['日期']).dt.month
    
    # 按月份和标签分组统计数量
    monthly_data = df.groupby(['月份', '新闻标签'])['标题'].count().unstack(fill_value=0)
    
    # 创建折线图
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    # 绘制开放型新闻趋势线
    ax.plot(monthly_data.index, 
            monthly_data.get('开放型', 0), 
            marker='o',          # 圆形标记
            linestyle='-',       # 实线
            color=COLORS['open'],     # 商务蓝
            linewidth=2.5,        # 线条加粗到2.5
            markersize=8,         # 点的大小设为8
            label='开放型')
    
    # 绘制限制型新闻趋势线
    ax.plot(monthly_data.index, 
            monthly_data.get('限制型', 0), 
            marker='s',          # 方形标记
            linestyle='--',      # 虚线
            color=COLORS['restrictive'],     # 深红
            linewidth=2.5,        # 线条加粗到2.5
            markersize=8,         # 点的大小设为8
            label='限制型')
    
    # 添加标题和标签
    ax.set_title('开放型vs限制型新闻月度趋势')
    ax.set_xlabel('月份')
    ax.set_ylabel('新闻数量')
    
    # 设置x轴刻度为1-6月
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    
    # 添加图例
    ax.legend()
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart4.png', dpi=150, bbox_inches='tight')
    print("图表4已保存：chart4.png")
    
    plt.close()


def create_chart5(df):
    """
    创建水平柱状图：每个国家的情绪分布
    
    参数：
        df (DataFrame): 包含国家和情绪数据的数据表
    """
    # 按国家和情绪分组统计数量
    sentiment_data = df.groupby(['国家', '情绪'])['标题'].count().unstack(fill_value=0)
    
    # 按国家总新闻数排序
    sentiment_data['总计'] = sentiment_data.sum(axis=1)
    sentiment_data = sentiment_data.sort_values('总计', ascending=True)
    sentiment_data = sentiment_data.drop('总计', axis=1)
    
    # 设置颜色
    colors = {'restrictive': COLORS['restrictive'], 'positive': COLORS['open'], 'neutral': COLORS['neutral']}
    
    # 创建水平柱状图
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    # 堆叠水平柱状图
    bottom = pd.Series([0]*len(sentiment_data), index=sentiment_data.index)
    for sentiment in ['restrictive', 'positive', 'neutral']:
        ax.barh(sentiment_data.index, 
                sentiment_data.get(sentiment, 0), 
                left=bottom,
                color=colors.get(sentiment, '#9CA3AF'),
                label=sentiment)
        bottom += sentiment_data.get(sentiment, 0)
    
    # 添加标题和标签
    ax.set_title('各国数字贸易情绪分布')
    ax.set_xlabel('新闻数量')
    ax.set_ylabel('国家/地区')
    
    # 添加图例（将英文标签改为中文）
    handles, labels = ax.get_legend_handles_labels()
    label_mapping = {'restrictive': '限制型', 'positive': '积极型', 'neutral': '中性'}
    new_labels = [label_mapping.get(label, label) for label in labels]
    ax.legend(handles, new_labels)
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart5.png', dpi=150, bbox_inches='tight')
    print("图表5已保存：chart5.png")
    
    plt.close()


def create_chart6(df):
    """
    创建热力图：各国数字贸易议题热力图
    
    参数：
        df (DataFrame): 包含国家和主题数据的数据表
    """
    # 统计每个国家在每个主题上出现的新闻数量，做成矩阵
    heatmap_data = df.groupby(['国家', '主题'])['标题'].count().unstack(fill_value=0)
    
    # 创建热力图
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    
    # 使用seaborn绘制热力图
    sns.heatmap(heatmap_data, 
                cmap='YlOrRd',      # 颜色映射：黄色到橙色到红色
                annot=True,         # 在每个格子里显示数字
                fmt='d',            # 数字格式：整数
                linewidths=0.5,     # 格子之间的线宽
                cbar_kws={'label': '新闻数量'},  # 颜色条标签
                ax=ax)
    
    # 添加标题
    ax.set_title('各国数字贸易议题热力图')
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart6.png', dpi=150, bbox_inches='tight')
    print("图表6已保存：chart6.png")
    
    plt.close()


def create_chart7(df):
    """
    创建关键词词频月度变化图：开放型vs限制型关键词月度词频变化
    
    参数：
        df (DataFrame): 包含日期数据的数据表
    """
    # 定义开放型和限制型关键词（与analyzer.py保持一致）
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
    
    # 从data_sample.py导入新闻列表
    from data_sample import news_list
    
    # 按月份统计关键词出现次数
    monthly_open_counts = []
    monthly_restriction_counts = []
    
    for month in range(1, 7):  # 1-6月
        open_count = 0
        restriction_count = 0
        
        for news in news_list:
            # 检查新闻日期是否属于当前月份
            news_date = pd.to_datetime(news['date'])
            if news_date.month == month:
                # 组合标题和正文
                full_text = (news['title'] + " " + news['content']).lower()
                
                # 统计开放型关键词
                for keyword in open_keywords:
                    if keyword.lower() in full_text:
                        open_count += 1
                
                # 统计限制型关键词
                for keyword in restriction_keywords:
                    if keyword.lower() in full_text:
                        restriction_count += 1
        
        monthly_open_counts.append(open_count)
        monthly_restriction_counts.append(restriction_count)
    
    # 创建折线图
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    # 绘制开放型关键词词频趋势线
    ax.plot(range(1, 7), 
            monthly_open_counts, 
            marker='o',          # 圆形标记
            linestyle='-',       # 实线
            color=COLORS['open'],     # 商务蓝
            linewidth=2.5,        # 线条加粗到2.5
            markersize=8,         # 点的大小设为8
            label='开放型关键词')
    
    # 绘制限制型关键词词频趋势线
    ax.plot(range(1, 7), 
            monthly_restriction_counts, 
            marker='s',          # 方形标记
            linestyle='--',      # 虚线
            color=COLORS['restrictive'],     # 深红
            linewidth=2.5,        # 线条加粗到2.5
            markersize=8,         # 点的大小设为8
            label='限制型关键词')
    
    # 添加标题和标签
    ax.set_title('开放型vs限制型关键词月度词频变化')
    ax.set_xlabel('月份')
    ax.set_ylabel('关键词出现次数')
    
    # 设置x轴刻度为1-6月
    plt.xticks(range(1, 7), ['1月', '2月', '3月', '4月', '5月', '6月'])
    
    # 添加图例
    ax.legend()
    
    # 去掉上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('chart7.png', dpi=150, bbox_inches='tight')
    print("图表7已保存：chart7.png")
    
    plt.close()


def main():
    """
    主函数：生成所有图表
    """
    print("=" * 60)
    print("          数字贸易新闻可视化")
    print("=" * 60)
    print("\n正在生成图表...\n")
    
    # 获取提取和分析的数据
    df = extract_and_merge()
    
    # 生成7张图表
    create_chart1(df)  # 饼图：新闻类型分布
    create_chart2(df)  # 柱状图：国家分布
    create_chart3(df)  # 柱状图：主题分布
    create_chart4(df)  # 折线图：月度趋势
    create_chart5(df)  # 水平柱状图：情绪分布
    create_chart6(df)  # 热力图：各国议题热力图
    create_chart7(df)  # 折线图：关键词词频月度变化
    
    print("\n所有图表已生成完成！")
    print("保存的文件：chart1.png ~ chart7.png")


# 如果直接运行此文件，则执行主函数
if __name__ == "__main__":
    main()
