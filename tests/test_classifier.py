from job_tracker.classifier import classify_direction


def test_agent_keywords_have_highest_priority():
    assert classify_direction("Java Agent开发", "RAG LangChain4j") == "Agent开发"


def test_common_directions_are_classified():
    assert classify_direction("Spring Boot后端实习", "Java 微服务") == "Java后端"
    assert classify_direction("算法实习生", "PyTorch 模型训练") == "算法工程"
    assert classify_direction("未知岗位", "") == "其他"
