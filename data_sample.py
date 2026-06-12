# -*- coding: utf-8 -*-
"""
数字贸易新闻模拟数据文件
用于测试和演示数字贸易新闻列表功能

本文件包含15条模拟的数字贸易新闻，涵盖以下类型：
1. 数据本地化限制
2. 跨境数字合作
3. 数字关税或平台税
4. 电商跨境扩张
5. AI相关贸易政策
6. 平台监管（反垄断）
7. 隐私法/数据保护法
"""

# 新闻列表：每个元素是一个字典，包含 title(标题)、content(正文)、source(来源)、date(日期)
news_list = [
    # ========== 1. 数据本地化限制 ==========
    # 这类新闻通常涉及某国政府要求外国企业的数据必须存储在本国服务器上

    {
        "title": "India Mandates Local Storage of Payment Data",
        "content": "India's central bank has ordered all payment system providers to store transaction data locally within the country, affecting major tech firms operating in the region.",
        "source": "Reuters",
        "date": "2024-02-15"
    },
    {
        "title": "Russia Enforces Data Localization Law for Tech Companies",
        "content": "Russian authorities have begun enforcing strict data localization requirements, requiring all foreign tech companies to store citizen data on domestic servers by July.",
        "source": "Bloomberg",
        "date": "2024-04-22"
    },

    # ========== 2. 跨境数字合作 ==========
    # 这类新闻涉及两个或多个国家/地区签署数字贸易协议或合作备忘录

    {
        "title": "EU and Singapore Sign Digital Trade Agreement",
        "content": "The European Union and Singapore have signed a comprehensive digital trade agreement aimed at facilitating cross-border data flows and reducing regulatory barriers.",
        "source": "WTO",
        "date": "2024-03-10"
    },
    {
        "title": "Japan and US Expand Digital Partnership",
        "content": "Japan and the United States have announced an expanded digital partnership focusing on AI governance, semiconductor supply chains, and cross-border data sharing.",
        "source": "Reuters",
        "date": "2024-05-08"
    },

    # ========== 3. 数字关税或平台税 ==========
    # 这类新闻涉及针对数字服务征收的关税或特别税

    {
        "title": "UK Introduces Digital Services Tax Review",
        "content": "The UK government has launched a review of its Digital Services Tax, considering adjustments to align with international consensus on platform taxation.",
        "source": "Bloomberg",
        "date": "2024-01-28"
    },
    {
        "title": "France to Implement New Tech Levy",
        "content": "France will implement a new technology levy targeting large digital platforms, expecting to collect over 500 million euros annually from qualified companies.",
        "source": "Reuters",
        "date": "2024-06-05"
    },

    # ========== 4. 电商跨境扩张 ==========
    # 这类新闻涉及电商平台或企业向新市场扩张

    {
        "title": "Amazon Expands Prime Delivery to Southeast Asia",
        "content": "Amazon has announced the expansion of its Prime delivery service to Vietnam, Thailand, and Malaysia, offering faster cross-border shipping for regional consumers.",
        "source": "TechCrunch",
        "date": "2024-02-28"
    },
    {
        "title": "Shopee Launches Cross-Border E-commerce Hub",
        "content": "Shopee has launched a new cross-border e-commerce hub in the Philippines, enabling small merchants to access markets in Indonesia, Malaysia, and Singapore.",
        "source": "TechCrunch",
        "date": "2024-04-15"
    },

    # ========== 5. AI相关贸易政策 ==========
    # 这类新闻涉及人工智能技术的贸易政策、出口管制或监管框架

    {
        "title": "US Imposes AI Chip Export Restrictions",
        "content": "The United States has expanded its export controls on advanced AI chips and computing equipment, restricting sales to certain countries without special licenses.",
        "source": "Bloomberg",
        "date": "2024-03-22"
    },
    {
        "title": "EU Proposes AI Act Trade Implications Assessment",
        "content": "The European Commission has published an assessment of the trade implications of its proposed AI Act, highlighting potential barriers for non-EU AI service providers.",
        "source": "OECD",
        "date": "2024-05-30"
    },
    {
        "title": "China Releases Generative AI Trade Guidelines",
        "content": "China's Ministry of Commerce has released new guidelines for generative AI products, establishing rules for cross-border AI service provision.",
        "source": "Reuters",
        "date": "2024-06-12"
    },

    # ========== 6. 平台监管（反垄断） ==========
    # 这类新闻涉及对大型科技平台的市场监管、反垄断调查或处罚

    {
        "title": "EU Fines Meta for Data Privacy Breach",
        "content": "The European Union has fined Meta 1.2 billion euros for violating GDPR rules by transferring European user data to US servers without adequate protection.",
        "source": "Reuters",
        "date": "2024-05-22"
    },
    {
        "title": "UK Opens Investigation into Apple App Store",
        "content": "Britain's competition regulator has opened a formal investigation into Apple's App Store practices, examining whether they constitute anti-competitive behavior.",
        "source": "Bloomberg",
        "date": "2024-03-05"
    },

    # ========== 7. 隐私法/数据保护法 ==========
    # 这类新闻涉及数据保护法规的制定、实施或更新

    {
        "title": "Brazil Enacts New Data Protection Framework",
        "content": "Brazil has enacted a comprehensive data protection framework modeled after GDPR, establishing strict rules for how companies handle personal information of Brazilian citizens.",
        "source": "WTO",
        "date": "2024-04-02"
    },
    {
        "title": "California Updates Consumer Privacy Regulations",
        "content": "California has updated its consumer privacy regulations, expanding consumer rights and increasing penalties for non-compliant businesses handling user data.",
        "source": "OECD",
        "date": "2024-06-18"
    }
]

# 如果直接运行此文件，则打印所有新闻标题用于测试
if __name__ == "__main__":
    print("=== 数字贸易新闻列表 ===")
    print(f"共 {len(news_list)} 条新闻\n")
    for i, news in enumerate(news_list, 1):
        print(f"{i}. [{news['source']}] {news['date']}")
        print(f"   标题: {news['title']}")
        print(f"   摘要: {news['content'][:50]}...")
        print()
