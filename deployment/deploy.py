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
# limitations under the License.

import logging
import argparse
import sys
import vertexai
from chimei_gpt_agent.agent import root_agent
from chimei_gpt_agent.config import Config
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from google.api_core.exceptions import NotFound

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

configs = Config()

AGENT_WHL_FILE = "./chimei_gpt_agent-0.1.0-py3-none-any.whl"

vertexai.init(
    project=configs.GOOGLE_CLOUD_PROJECT,
    location=configs.GOOGLE_CLOUD_LOCATION,
    staging_bucket=f"gs://{configs.GOOGLE_CLOUD_STORAGE_BUCKET}",
)

parser = argparse.ArgumentParser(description="Short sample app")

parser.add_argument(
    "--delete",
    action="store_true",
    dest="delete",
    required=False,
    help="Delete deployed agent",
)
parser.add_argument(
    "--resource_id",
    required="--delete" in sys.argv,
    action="store",
    dest="resource_id",
    help="The resource id of the agent to be deleted in the format projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID",
)


args = parser.parse_args()

if args.delete:
    try:
        agent_engines.get(resource_name=args.resource_id)
        agent_engines.delete(resource_name=args.resource_id)
        print(f"Agent {args.resource_id} deleted successfully")
    except NotFound as e:
        print(e)
        print(f"Agent {args.resource_id} not found")

else:
    logger.info("deploying app...")
    
    logging.debug("deploying agent to agent engine:")
    remote_app = agent_engines.create(
        agent_engine=root_agent,
        display_name=root_agent.name,
        description=root_agent.description,
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]==1.94.0",
            "google-genai==1.16.1",
            "cloudpickle==3.1.1",
            "pydantic==2.11.5",
            "python-dotenv (>= 1.0.1)",
            "litellm==1.71.1"
            # "google-genai (>=1.9.0,<2.0.0)",
            # "cloudpickle==3.1.1",
            # "pydantic (>=2.10.6,<3.0.0)",
            # "litellm (>=1.69.0)"
        ],
        # env_vars = {
        #     # "AZURE_API_KEY": "618e2d3eb6674b23a60e185f772b6b33",
        #     # "AZURE_API_BASE": "https://gcp-ai-test.openai.azure.com",
        #     # "AZURE_API_VERSION": "2025-01-01-preview",
        #     # "GOOGLE_CLOUD_PROJECT": "cht-gcp-ai-rag-poc", # google.api_core.exceptions.FailedPrecondition: 400 Environment variable name 'GOOGLE_CLOUD_PROJECT' is reserved. Please rename the variable in `spec.deployment_spec.env`.
        #     # "GOOGLE_CLOUD_LOCATION": "us-central1",
        #     # "GOOGLE_CLOUD_STORAGE_BUCKET": "cht-gcp-ai-rag-poc-agent-engine-test",
        #     # "GOOGLE_GENAI_USE_VERTEXAI": "1"
        # },
        extra_packages=["chimei_gpt_agent"],
    )

    app = AdkApp(agent=root_agent, enable_tracing=True)

    logging.debug("testing deployment:")
    session = remote_app.create_session(user_id="123")
    for event in remote_app.stream_query(
        user_id="123",
        session_id=session["id"],
        message="hello!",
    ):
        if event.get("content", None):
            logger.info(event['content']['parts'][0]['text'])