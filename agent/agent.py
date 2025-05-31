# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.§

"""Agent module for the customer service agent."""

import logging
import warnings
from google.adk.agents import Agent
from google.adk.tools import ToolContext, FunctionTool
from .config import Config
from .prompts import GLOBAL_INSTRUCTION
from .api import youbike_api as ubike, google_map_api as map

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


def get_youbike_info(preference: str, value: str, tool_context: ToolContext):
    """Updates a user-specific preference."""
    user_prefs_key = "user:preferences"
    # Get current preferences or initialize if none exist
    preferences = tool_context.state.get(user_prefs_key, {})
    preferences[preference] = value
    # Write the updated dictionary back to the state
    tool_context.state[user_prefs_key] = preferences
    print(f"Tool: Updated user preference '{preference}' to '{value}'")
    return {"status": "success", "updated_preference": preference}

youbike_station_info_tool = FunctionTool(func=ubike.get_youbike_info)
youbike_station_list_tool = FunctionTool(func=ubike.get_youbike_locations_in_taipei_city)
google_map_tool = FunctionTool(func=map.build_map_html)


instruction = '''你是個Youbike服務專員，提供使用者有用的站點資訊。
- 如果使用者詢問的特定youbike車站資訊，使用 'youbike_station_list_tool' 回應車站的剩餘車輛及存在的車輛數目
- 如果使用者詢問的地點不夠明確，使用 'youbike_station_list_tool' 給予最接近的youbike車站作為提示，'youbike_station_list_tool' 所回傳的車站清單會由 "," 分隔
- 如果查詢到youbike車站資訊結果，利用 'google_map_tool' 產生地圖HTML供使用者參考。
'''

root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=instruction,
    name=configs.agent_settings.name,
    tools=[youbike_station_info_tool,youbike_station_list_tool,google_map_tool]
)