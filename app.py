import os
import requests
import google.generativeai as genai
from datetime import datetime

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def fetch_global_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=8&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []

def summarize_with_ai(title, description):
    prompt = f"""
    請將以下英文新聞標題與內容翻譯成台灣常用的繁體中文，並為我總結出 3 個重點。
    新聞標題：{title}
    新聞內容：{description}
    請嚴格遵守以下輸出格式（不要包含任何 markdown 的 `**` 或額外文字）：
    標題：[翻譯後的中文標題]
    摘要：
    - [重點一]
    - [重點二]
    - [重點三]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"標題：{title}\n摘要：\n- 無法產生摘要。"

def generate_html(news_list):
    today_str = datetime.today().strftime('%Y-%m-%d')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>全球新聞每日情報站</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 text-gray-900 font-sans">
        <div class="max-w-4xl mx-auto px-4 py-12">
            <header class="text-center mb-16">
                <h1 class="text-4xl font-extrabold text-indigo-600 tracking-tight mb-2">🌍 全球新聞每日情報站</h1>
                <p class="text-gray-500">AI 自動統整全球焦點 • 更新時間：{today_str}</p>
            </header>
            <main class="space-y-8">
    """
    for article in news_list:
        if not article.get('title') or not article.get('description'):
            continue
        ai_result = summarize_with_ai(article['title'], article['description'])
        lines = ai_result.split("\n")
        display_title = lines[0].replace("標題：", "").strip() if lines else article['title']
        display_summary = "<br>".join(lines[1:]) if len(lines) > 1 else "暫無摘要"
        
        html_content += f"""
                <article class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <h2 class="text-xl font-bold text-gray-800 mb-3">{display_title}</h2>
                    <div class="text-gray-600 text-sm leading-relaxed mb-4">{display_summary}</div>
                    <div class="flex justify-between items-center text-xs text-gray-400">
                        <span>來源：{article['source']['name']}</span>
                        <a href="{article['url']}" target="_blank" class="text-indigo-500 hover:underline font-medium">閱讀原文 →</a>
                    </div>
                </article>
        """
    html_content += """
            </main>
            <footer class="text-center mt-16 text-xs text-gray-400">
                <p>© 2026 全球新聞每日情報站 - Powered by Gemini AI</p>
            </footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    print("正在抓取全球焦點新聞...")
    raw_news = fetch_global_news()
    print(f"成功抓取 {len(raw_news)} 則新聞，正在請 AI 進行統整翻譯...")
    generate_html(raw_news)
    print("網頁更新成功！")
