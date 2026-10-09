"""
Web Search tool (DuckDuckGo Instant Search / Mock Fallback).
"""

import json
import urllib.request
import urllib.parse

def web_search(query: str, max_results: int = 3) -> str:
    """查询互联网简要信息"""
    try:
        # 使用无需 API Key 的 DuckDuckGo Lite / API 格式检索
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "NanoAgent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        abstract = data.get("AbstractText", "")
        if abstract:
            return f"Search Result for '{query}': {abstract}"

        related = data.get("RelatedTopics", [])
        if related:
            snippets = []
            for item in related[:max_results]:
                if "Text" in item:
                    snippets.append(item["Text"])
            if snippets:
                return "\n".join(snippets)

        return f"未检索到针对 '{query}' 的摘要信息，请尝试更换关键词。"
    except Exception as e:
        # 网络环境不通时的优雅降级提示
        return f"[Web Search Notice] 无法连接到外部网络搜索引擎 ({str(e)})，建议使用本地数据分析。"
