import os, logging, warnings, json
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from pydantic import BaseModel, Field
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .api import ubike_api, google_map_api as map


# llm = 'gpt-4o-mini'
llm = 'gemini-2.0-flash-001'
print(f'LLM: {llm}')


warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


youbike_station_info_tool = FunctionTool(func=ubike_api.get_youbike_info)
youbike_location_search_tool = FunctionTool(func=ubike_api.get_youbike_locations_in_taipei_city)
google_map_tool = FunctionTool(func=map.build_map_place_html)
restaurant_map_tool = FunctionTool(func=map.build_restaurant_search_map_html)

print(f"env variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

def init_youbike_agent():
    # llm = 'gemini-2.0-flash-001'
    llm = 'gemini-2.5-flash-preview-05-20'
    generate_content_config=types.GenerateContentConfig(
        temperature=0.8,
        top_p=0.8,
    )
    location_search_agent = Agent(
        name='youbike_location_search_agent',
        model=llm,
        description='''回覆使用者詢問的問題，負責轉換使用者詢問Youbike車站地點至確切的名稱''',
        instruction='''你是一個Youbike車站名稱查詢專員，負責轉換使用者詢問Youbike車站地點至確切的名稱，

        **使用者問題情境:**
        1. **詢問 Youbike 站點資訊:**
        1.1. tools 會回傳所有可供查詢的真實Youbike站點名稱，每個站點名稱被逗號分隔
        1.2. 轉換使用者所提到的Youbike站點成最近似的真實Youbike站點名稱，e.g, 信義杭州=>信義杭州路口
        1.3. 如果使用者所提到的地點有多個Youbike站點，請全部加到原始的提問中
        1.3. 回傳完整的使用者問題，只置換Youbike站點至真實名稱，*不要*添加或減少其他不相關內容
        2. **詢問其他訊息:**
        2.1 直接回傳原本的問題，*不要*做任何修改
        ''',
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        tools=[youbike_location_search_tool],
        output_key="adjusted_query"
    )

    state_agent = Agent(
        name='youbike_info_agent',
        model=llm,
        description='''Youbike車站查詢專員，根據使用者提問回覆Youbike車站的詳細狀況''',
        instruction='''你是一個Youbike車站查詢專員，根據使用者提問回覆Youbike車站的詳細狀況。
        
        **使用者提問情境:**
        * **詢問Youbike站點資訊:**
        ** 如果使用者詢問的地點不明確，請根據 'youbike_location_search_tool' 回應使用者至多*5個*附近Youbike車站供選擇 ('youbike_location_search_tool' 所回傳的車站清單需由","作為分隔符號進行切割)，並且利用 'google_map_tool' 查詢使用者詢問的地點，產生可供鑲嵌的 google map HTML
        * **其他對話內容**
        ** 簡單的閒聊回應，但不要偏離Youbike的主題
        ''',
        generate_content_config=generate_content_config,
        # tools=[AgentTool(agent=location_search_agent), youbike_station_info_tool, youbike_location_search_tool, google_map_tool],
        tools=[youbike_station_info_tool, youbike_location_search_tool, google_map_tool],
        output_key="youbike_info"
    )

    ubike_pipeline_agent = SequentialAgent(
        name="YoubikeInquiryPipelineAgent",
        sub_agents=[state_agent],
        description="Executes a sequence of youbike station location mapping & replacing, youbike station information answering.",
    )
    return ubike_pipeline_agent


def init_restaurant_search_agent():
    llm = 'gemini-2.5-flash-preview-05-20'
    generate_content_config=types.GenerateContentConfig(
        temperature=1,
    )
    restaurant_critic = Agent(
        name='restaurant_critic',
        model=llm,
        description='查詢特定地點附近的餐廳，並產生Google Embed Map HTML',
        instruction='''你是一個餐廳搜尋及分析專家，根據使用者提供的地點及要求，回應適合的餐廳，並詳細描述餐廳的 google map 評價、價格、餐點、地點、環境等饕客會注意的項目
        - 使用 'google_search' 搜尋地點附近餐廳資訊
        - 預設搜尋範圍會是台灣的台北市區域，實際請根據使用者提供的地點搜尋
        - 條列餐廳及其相關資訊
        - 盡可能地明確描述餐廳的價位範圍
        - 如果可能請判斷 google map 評價是不是灌水或洗的
        ''',
        generate_content_config=generate_content_config,
        tools=[google_search],
        output_key="restaurants_info"
    )
    restaurant_summary_agent = Agent(
        name='restaurant_summary_agent',
        model=llm,
        description='查詢特定地點附近的餐廳，並產生Google Embed Map HTML',
        instruction='''你是一個餐廳搜尋及分析專家，根據使用者提供的地點及要求，回應適合的餐廳，並詳細描述餐廳的 google map 評價、價格、餐點、地點、環境等饕客會注意的項目，並回應使用餐廳地點的map HTML
        - 使用 'restaurant_critic' 搜尋地點附近的餐廳及相關資訊
        - 務必使用 'restaurant_search_tool' 將餐廳地圖HTML回應給使用者
        - 請根據使用者實際提供的地點搜尋，如果不夠明確，預設搜尋範圍會是台灣的台北市區域
        - 如果使用者不知道要吃甚麼，請提供 2~3 個選項個選項進行快速決策
        ''',
        generate_content_config=generate_content_config,
        tools=[AgentTool(agent=restaurant_critic), restaurant_map_tool],
        output_key="restaurant_summary"
    )

    restaurant_search_agent = SequentialAgent(
        name="RestaurantSearchAgent",
        sub_agents=[restaurant_summary_agent],
        description="Search for restaurants near the queried location.",
    )
    return restaurant_search_agent


def init_agent(llm):
    global_instruction = GLOBAL_INSTRUCTION
    instruction = INSTRUCTION
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.8,
    )

    match llm:
        case 'gpt-4o-mini':
            root_agent = Agent(
                name="aoai_agent",
                model=LiteLlm(model="azure/gpt-4o-mini"),
                instruction=instruction,
                description='A GPT model agent'
            )
        case 'gemini-2.0-flash-001':
            root_agent = Agent(
                name=configs.agent_settings.name,
                model=configs.agent_settings.model,
                global_instruction=global_instruction,
                instruction=instruction,
                description='a Gemini model agent',
                generate_content_config=generate_content_config,
            )
        case _:
            root_agent = Agent(
                name=configs.agent_settings.name,
                model=configs.agent_settings.model,
                global_instruction=global_instruction,
                instruction=instruction,
                description='a Gemini model agent',
                generate_content_config=generate_content_config,
            )
    return root_agent

# root_agent = init_agent(llm)
# root_agent = init_youbike_agent()
root_agent = init_restaurant_search_agent()