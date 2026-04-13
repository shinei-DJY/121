# import requests
# from pydantic import Field
# # 定义心知天气API的工具类
# class WeatherTool:
#   city: str = Field(description="City name, include city and county")
#   def __init__(self, api_key) -> None:
#     self.api_key = api_key
#   def run(self, city):
#     city = city.split("\n")[0] # 清除多余的换行符，避免报错
#     url = f"https://api.seniverse.com/v3/weather/now.json?key={self.api_key}&location={city}&language=zh-Hans&unit=c"
#       # 构建 API 请求 URL 返回结果
#     response = requests.get(url)
#     if response.status_code == 200: # 请求成功
#         data = response.json() # 解析返回的JSON
#         weather = data["results"][0]["now"]["text"] # 天气信息
#         tem = data["results"][0]["now"]["temperature"] # 温度
#         return f"{city}的天气是{weather}, 温度是{tem}°C" # 返回格式化后的天气信息
#     else:
#         return f"无法获取{city}的天气信息。"
# api_key = "SBJVysU9a4KvOtgHs"
# weather_tool = WeatherTool(api_key)
# print(weather_tool.run("成都"))
# print(weather_tool.run("北京"))
import requests
from pydantic import Field
# 定义心知天气API的工具类
class WeatherTool:
    city: str = Field(description="City name, include city and county")
    def __init__(self, api_key) -> None:
        self.api_key = api_key
    def run(self, city):
        city = city.split("\n")[0] # 清除多余的换行符，避免报错
        url = f"https://api.seniverse.com/v3/weather/now.json?key={self.api_key}&location={city}&language=zh-Hans&unit=c"
        # 构建 API 请求 URL 返回结果
        response = requests.get(url)
        if response.status_code == 200: # 请求成功
            data = response.json() # 解析返回的JSON
            weather = data["results"][0]["now"]["text"] # 天气信息
            tem = data["results"][0]["now"]["temperature"] # 温度
            return f"{city}的天气是{weather}, 温度是{tem}°C" # 返回格式化后的天气信息
        else:
            return f"无法获取{city}的天气信息。"
api_key = "Skgx0703chLaxLUsi"
weather_tool = WeatherTool(api_key)
# print(weather_tool.run("成都"))
from langchain_openai import ChatOpenAI
chat_model = ChatOpenAI(
    openai_api_key="sk-6c48646da0024548b64ae63da43549ab", # ollama兼容OpenAIAPI的格式
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="deepseek-v3"
)
from langchain.agents import Tool # 用于封装工具
from datetime import datetime
import math

# 定义获取当前时间的函数
def get_current_time(input_str=""):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 定义科学计算器函数
def calculator(expression=""):
    try:
        if not expression or expression.strip() == "":
            return "请输入数学表达式，例如: 2+2, sqrt(16), log(100)"
        # 安全地计算数学表达式
        allowed_names = {
            "sqrt": math.sqrt,
            "pow": math.pow,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"

# 定义热榜查询工具类
class HotNewsTool:
    def get_hotlist(self, platform=""):
        # 这是一个示例实现，实际使用时可以接入真实的热榜API
        if not platform or platform.strip() == "":
            return "请输入平台名称，例如: 微博、知乎、百度"
        hotlists = {
            "微博": ["热搜1", "热搜2", "热搜3"],
            "知乎": ["热榜1", "热榜2", "热榜3"],
            "百度": ["热门1", "热门2", "热门3"]
        }
        return hotlists.get(platform, f"不支持查询 {platform} 的热榜")

hotnews_tool = HotNewsTool()

# 将API工具封装成langchain的TOOL对象
tools = [
Tool(
    name="天气查询",
    func=weather_tool.run,
    description="查询城市天气，输入应为城市名称"
),
Tool(
    name="当前时间",
    func=get_current_time,
    description="获取当前时间，无需输入参数"
),
Tool(
    name="科学计算器",
    func=calculator,
    description="执行数学计算，支持加减乘除、指数、对数等运算"
),
Tool(
    name="热榜查询",
    func=hotnews_tool.get_hotlist,
    description="查询平台热榜，输入应为平台名称"
)
]
from langchain_core.prompts import PromptTemplate
template = """请尽可能好地回答以下问题。你可以使用以下工具：

{tools}

请使用以下格式：

Question: 需要回答的问题
Thought: 你应该始终思考该做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复零次或多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始问题的最终答案

开始！

Question: {input}
Thought: {agent_scratchpad}"""
prompt = PromptTemplate.from_template(template)
# 导入 代理创建函数 和 代理执行器
from langchain.agents import create_react_agent, AgentExecutor
agent = create_react_agent(chat_model, tools, prompt)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
query = "成都天气怎么样"
response = agent_executor.invoke({"input": query})
print(response)