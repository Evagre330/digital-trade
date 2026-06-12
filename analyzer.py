# -*- coding: utf-8 -*-
"""
数字贸易新闻分析器
基于 data_sample.py 中的新闻数据进行关键词分析和指数计算

主要功能：
1. 定义开放型和限制型两组关键词
2. 对每条新闻进行关键词匹配和统计
3. 根据关键词数量打标签（开放型/限制型/中性）
4. 计算DTOI和RII指数
5. 使用pandas输出分析结果表格
"""

# 导入需要的库
import pandas as pd

# 从 data_sample.py 导入新闻列表
from data_sample import news_list


def analyze_news():
    """
    分析新闻列表的主函数
    """
    # ========== 1. 定义关键词组 ==========
    # 【修改说明】扩充了关键词词典，增加了更多相关词汇以提高分类准确性
    
    # 开放型关键词：表示促进数字贸易发展的词汇
    # 这些词通常与合作、开放、自由流动相关
    open_keywords = [
        "cross-border cooperation",    # 跨境合作
        "free flow of data",          # 数据自由流动
        "digital partnership",        # 数字伙伴关系
        "e-commerce expansion",       # 电商扩张
        "trade facilitation",         # 贸易便利化
        "digital trade agreement",    # 数字贸易协议
        "data sharing",               # 数据共享
        "digital connectivity",       # 数字互联互通
        "open data",                  # 开放数据
        "bilateral agreement",        # 双边协议
        "multilateral",               # 多边的
        "liberalization",             # 自由化
        "interoperability",           # 互操作性
        "mutual recognition",         # 相互认可
        "digital economy agreement",  # 数字经济协议
        "expand",                     # 扩张/扩大
        "launch",                     # 启动/推出
        "partner",                    # 伙伴/合作
        "collaborate",                # 协作
        "facilitate",                 # 促进/便利
        "streamline"                  # 简化/优化流程
    ]
    
    # 限制型关键词：表示对数字贸易有约束或限制的词汇
    # 这些词通常与管制、限制、征税相关
    restriction_keywords = [
        "restriction",           # 限制
        "ban",                   # 禁令
        "tariff",                # 关税
        "digital tax",           # 数字税
        "data localization",     # 数据本地化
        "cybersecurity review",  # 网络安全审查
        "fine",                  # 罚款
        "regulation",            # 监管
        "compliance",            # 合规
        "antitrust",             # 反垄断
        "privacy law",           # 隐私法
        "data protection",       # 数据保护
        "mandatory",             # 强制性的
        "enforce",               # 强制执行
        "prohibit",              # 禁止
        "block",                 # 阻挡/封锁
        "sanction",              # 制裁
        "barrier",               # 壁垒/障碍
        "levy",                  # 征税/征收
        "investigate",           # 调查
        "scrutiny",              # 审查/监管
        "penalize",              # 惩罚
        "require",               # 要求
        "localization",          # 本地化
        "sovereignty"            # 主权
    ]

    # ========== 2. 初始化统计变量 ==========
    
    # 统计各类型新闻数量
    open_count = 0           # 开放型新闻数量
    restriction_count = 0    # 限制型新闻数量
    neutral_count = 0        # 中性新闻数量
    
    # 统计关键词出现总次数
    total_open_keywords = 0    # 开放型关键词出现总次数
    total_restriction_keywords = 0  # 限制型关键词出现总次数
    
    # 存储每条新闻的分析结果
    analysis_results = []

    # ========== 3. 逐条分析新闻 ==========
    
    for news in news_list:
        # 获取新闻的标题和正文，转换为小写以便不区分大小写匹配
        title = news["title"].lower()
        content = news["content"].lower()
        
        # 组合标题和正文进行关键词匹配
        full_text = title + " " + content
        
        # 统计当前新闻的关键词数量
        open_word_count = 0    # 当前新闻包含的开放型关键词数量
        restriction_word_count = 0  # 当前新闻包含的限制型关键词数量
        
        # 检查每个开放型关键词是否出现在新闻中
        for keyword in open_keywords:
            if keyword.lower() in full_text:
                open_word_count += 1
        
        # 检查每个限制型关键词是否出现在新闻中
        for keyword in restriction_keywords:
            if keyword.lower() in full_text:
                restriction_word_count += 1
        
        # 更新全局关键词统计
        total_open_keywords += open_word_count
        total_restriction_keywords += restriction_word_count
        
        # ========== 4. 根据关键词数量打标签 ==========
        # 【修改说明】优化了分类逻辑，减少中性新闻的数量
        # 新的判断规则：
        # - 开放型：开放词数量 > 限制词数量
        # - 限制型：限制词数量 > 开放词数量
        # - 限制型：两者相等但都大于0（偏保守判断）
        # - 中性：两者相等且都为0（只有这种情况才标记为中性）
        if open_word_count > restriction_word_count:
            label = "开放型"
            open_count += 1
        elif restriction_word_count > open_word_count:
            label = "限制型"
            restriction_count += 1
        elif open_word_count == restriction_word_count and open_word_count > 0:
            # 两者相等但都大于0时，标记为限制型（偏保守判断）
            label = "限制型"
            restriction_count += 1
        else:
            # 两者相等且都为0时，标记为中性
            label = "中性"
            neutral_count += 1
        
        # 记录当前新闻的分析结果
        analysis_results.append({
            "标题": news["title"],
            "来源": news["source"],
            "日期": news["date"],
            "标签": label,
            "开放词数量": open_word_count,
            "限制词数量": restriction_word_count
        })
    
    # ========== 5. 计算指数 ==========
    
    total_news = len(news_list)  # 总新闻数量
    
    # DTOI：数字贸易开放指数
    # 计算公式：(开放类新闻数量 - 限制类新闻数量) / 总新闻数量
    # 范围：-1 到 +1，正值表示开放趋势，负值表示限制趋势
    dto = (open_count - restriction_count) / total_news
    
    # RII：限制强度指数
    # 计算公式：限制型关键词出现总次数 / 所有关键词出现总次数
    # 范围：0 到 1，值越大表示限制趋势越强
    total_keywords = total_open_keywords + total_restriction_keywords
    if total_keywords > 0:
        rii = total_restriction_keywords / total_keywords
    else:
        rii = 0  # 防止除以0的情况
    
    # 计算各类型新闻占比
    open_percent = (open_count / total_news) * 100
    restriction_percent = (restriction_count / total_news) * 100
    neutral_percent = (neutral_count / total_news) * 100
    
    # ========== 6. 输出分析结果 ==========
    
    print("=" * 60)
    print("          数字贸易新闻分析报告")
    print("=" * 60)
    
    # 打印指数结果
    print("\n【关键指数】")
    print(f"数字贸易开放指数 (DTOI): {dto:.4f}")
    print(f"限制强度指数 (RII): {rii:.4f}")
    
    # 打印各类型新闻占比
    print("\n【新闻类型分布】")
    print(f"开放型新闻: {open_count}条 ({open_percent:.1f}%)")
    print(f"限制型新闻: {restriction_count}条 ({restriction_percent:.1f}%)")
    print(f"中性新闻: {neutral_count}条 ({neutral_percent:.1f}%)")
    
    # 打印关键词统计
    print("\n【关键词统计】")
    print(f"开放型关键词出现次数: {total_open_keywords}次")
    print(f"限制型关键词出现次数: {total_restriction_keywords}次")
    print(f"关键词总出现次数: {total_keywords}次")
    
    # ========== 7. 使用 pandas 输出详细表格 ==========
    
    print("\n" + "=" * 60)
    print("          新闻分析详情表格")
    print("=" * 60)
    
    # 将分析结果转换为 DataFrame
    df = pd.DataFrame(analysis_results)
    
    # 设置显示选项，确保中文正常显示
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_colwidth', 50)  # 限制列宽度
    
    # 打印 DataFrame
    print(df.to_string(index=False))


# 如果直接运行此文件，则执行分析函数
if __name__ == "__main__":
    analyze_news()
