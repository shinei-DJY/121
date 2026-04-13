import requests
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

# 定义今日老婆 API 工具类
class TodayWifeTool:
    def run(self, id=""):
        """获取今日老婆图片
        参数:
            id: 可选，传入ID可在同一天固定返回同一张图片
        """
        try:
            if id and id.strip():
                url = f"https://api.pearktrue.cn/api/today_wife?id={id}"
            else:
                url = "https://api.pearktrue.cn/api/today_wife"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    wife_data = data.get("data", {})
                    image_url = wife_data.get("image_url")
                    role_name = wife_data.get("role_name")
                    width = wife_data.get("width")
                    height = wife_data.get("height")
                    return f"今日老婆: {role_name}\n图片链接: {image_url}\n尺寸: {width}x{height}"
                else:
                    return f"获取失败: {data.get('msg', '未知错误')}"
            else:
                return f"请求失败，状态码: {response.status_code}"
        except Exception as e:
            return f"发生错误: {str(e)}"

# 定义 Steam 喜加一 API 工具类
class SteamPlusOneTool:
    def run(self, input_str=""):
        """获取最新的 Steam 喜加一游戏信息
        """
        try:
            url = "https://api.pearktrue.cn/api/steamplusone/"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    game_name = data.get("name")
                    game_type = data.get("type")
                    start_time = data.get("starttime")
                    end_time = data.get("endtime")
                    perpetual = data.get("perpetual")
                    source = data.get("source")
                    game_url = data.get("url")
                    
                    result = f"Steam 喜加一: {game_name}\n"
                    result += f"类别: {game_type}\n"
                    result += f"开始时间: {start_time}\n"
                    result += f"结束时间: {end_time}\n"
                    result += f"是否永久: {perpetual}\n"
                    result += f"来源商店: {source}\n"
                    result += f"活动链接: {game_url}"
                    return result
                else:
                    return f"获取失败: {data.get('msg', '未知错误')}"
            else:
                return f"请求失败，状态码: {response.status_code}"
        except Exception as e:
            return f"发生错误: {str(e)}"

# 定义今日油价 API 工具类
class OilPriceTool:
    def run(self, province=""):
        """获取指定省份的今日油价
        参数:
            province: 省份名称，如"安徽"
        """
        try:
            if not province or province.strip() == "":
                return "请输入省份名称，例如: 安徽、北京、上海"
            
            url = "https://api.pearktrue.cn/api/oilprice"
            params = {"type": "get", "province": province}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    oil_data = data.get("data", {})
                    time = oil_data.get("time")
                    province_data = oil_data.get("province", {})
                    province_name = province_data.get("pri_name")
                    gasoline_92 = province_data.get("gasoline_92")
                    gasoline_95 = province_data.get("gasoline_95")
                    gasoline_98 = province_data.get("gasoline_98")
                    diesel_0 = province_data.get("diesel_0")
                    next_update = oil_data.get("next_update_time")
                    
                    result = f"{province_name} 今日油价 ({time}):\n"
                    result += f"92号汽油: {gasoline_92}元/升\n"
                    result += f"95号汽油: {gasoline_95}元/升\n"
                    result += f"98号汽油: {gasoline_98}元/升\n"
                    result += f"0号柴油: {diesel_0}元/升\n"
                    result += f"下次更新时间: {next_update}"
                    return result
                else:
                    return f"获取失败: {data.get('msg', '未知错误')}"
            else:
                return f"请求失败，状态码: {response.status_code}"
        except Exception as e:
            return f"发生错误: {str(e)}"

# 初始化工具实例
today_wife_tool = TodayWifeTool()
steam_plus_one_tool = SteamPlusOneTool()
oil_price_tool = OilPriceTool()

# 配置大模型（使用 agent_test.py 中的配置）
chat_model = ChatOpenAI(
    openai_api_key="sk-6c48646da0024548b64ae63da43549ab",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="deepseek-v3"
)

# 封装工具
tools = [
    Tool(
        name="今日老婆",
        func=today_wife_tool.run,
        description="获取二次元老婆图片，可选传入ID以在同一天固定返回同一张图片"
    ),
    Tool(
        name="Steam喜加一",
        func=steam_plus_one_tool.run,
        description="获取最新的Steam免费游戏信息"
    ),
    Tool(
        name="今日油价",
        func=oil_price_tool.run,
        description="获取指定省份的今日油价，输入应为省份名称"
    )
]

# 定义 ReAct prompt
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

# 创建 agent
agent = create_react_agent(chat_model, tools, prompt)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

# 测试示例
if __name__ == "__main__":
    print("=== Agent Tool 1 - 多API工具集成 ===")
    print("欢迎使用多API工具集成系统")
    print("-----------------------------------")
    print("可用工具:")
    print("1. 今日老婆 - 获取二次元老婆图片")
    print("2. Steam喜加一 - 获取最新的Steam免费游戏")
    print("3. 今日油价 - 获取指定省份的油价")
    print("4. 智能问答 - 让AI自动选择合适的工具")
    print("0. 退出系统")
    print("-----------------------------------")
    
    while True:
        choice = input("请选择工具编号: ")
        
        if choice == "0":
            print("感谢使用，再见！")
            break
        elif choice == "1":
            print("=== 今日老婆 ===")
            id_input = input("请输入ID（可选，回车跳过）: ")
            if id_input:
                query = f"给我一张ID为{id_input}的今日老婆图片"
            else:
                query = "给我一张今日老婆图片"
            response = agent_executor.invoke({"input": query})
            print(response["output"])
        elif choice == "2":
            print("=== Steam喜加一 ===")
            query = "最新的Steam喜加一游戏是什么"
            response = agent_executor.invoke({"input": query})
            print(response["output"])
        elif choice == "3":
            print("=== 今日油价 ===")
            province = input("请输入省份名称: ")
            if province:
                query = f"{province}今天的油价是多少"
                response = agent_executor.invoke({"input": query})
                print(response["output"])
            else:
                print("请输入有效的省份名称")
        elif choice == "4":
            print("=== 智能问答 ===")
            query = input("请输入您的问题: ")
            if query:
                response = agent_executor.invoke({"input": query})
                print(response["output"])
            else:
                print("请输入有效的问题")
        else:
            print("无效的选择，请重新输入")
        
        print("-----------------------------------")
        print()
