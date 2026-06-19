RULES = [
    ("Agent开发", ("agent", "智能体", "rag", "langchain", "langchain4j")),
    ("大模型应用", ("大模型", "llm", "aigc", "prompt")),
    ("Java后端", ("java", "spring", "微服务")),
    ("算法工程", ("算法", "pytorch", "训练", "微调")),
    ("数据分析", ("数据分析", "商业分析", "bi")),
    ("测试开发", ("测试开发", "自动化测试", "质量工程")),
]


def classify_direction(position: str, keywords: str = "") -> str:
    text = f"{position} {keywords}".lower()
    for direction, terms in RULES:
        if any(term in text for term in terms):
            return direction
    return "其他"
