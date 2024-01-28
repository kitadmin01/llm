import os
from dotenv import load_dotenv 
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.agents import create_sql_agent, load_tools, initialize_agent, react, Tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents.react.base import DocstoreExplorer, Tool
from langchain_community.docstore import Wikipedia
from langchain.serpapi import SerpAPIWrapper
from sqlalchemy import MetaData, Column, Integer, String, Table, Date, Float, create_engine
from datetime import datetime
from sqlalchemy import insert



class AgentCreator:
    def __init__(self):
        self.load_env_vars()
        self.setup_llm()
        self.setup_database()
        self.insert_observations()
        self.setup_agent()
        self.setup_conversational_agent()

    def load_env_vars(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    def setup_llm(self):
        self.llm = OpenAI(
            openai_api_key=self.OPENAI_API_KEY,
            temperature=0
        )

    def setup_database(self):
        self.metadata_obj = MetaData()
        self.stocks = Table(
            "stocks",
            self.metadata_obj,
            Column("obs_id", Integer, primary_key=True),
            Column("stock_ticker", String(4), nullable=False),
            Column("price", Float, nullable=False),
            Column("date", Date, nullable=False),
        )
        self.engine = create_engine("sqlite:///:memory:")
        self.metadata_obj.create_all(self.engine)

    def insert_observations(self):
        observations = [
            [1, 'ABC', 200, datetime(2023, 1, 1)],
            [2, 'ABC', 208, datetime(2023, 1, 2)],
            [3, 'ABC', 232, datetime(2023, 1, 3)],
            [4, 'ABC', 225, datetime(2023, 1, 4)],
            [5, 'ABC', 226, datetime(2023, 1, 5)],
            [6, 'XYZ', 810, datetime(2023, 1, 1)],
            [7, 'XYZ', 803, datetime(2023, 1, 2)],
            [8, 'XYZ', 798, datetime(2023, 1, 3)],
            [9, 'XYZ', 795, datetime(2023, 1, 4)],
            [10, 'XYZ', 791, datetime(2023, 1, 5)],
        ]

        for obs in observations:
            self.insert_obs(obs)

    def insert_obs(self, obs):
        stmt = insert(self.stocks).values(
            obs_id=obs[0],
            stock_ticker=obs[1],
            price=obs[2],
            date=obs[3]
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def setup_agent(self):
        db = SQLDatabase(self.engine)
        self.sql_chain = SQLDatabaseChain(llm=self.llm, database=db, verbose=True)
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=SQLDatabaseToolkit(db=db, llm=self.llm),
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            max_iterations=3
        )

    def setup_conversational_agent(self):
        self.tools = load_tools(
            ["llm-math"],
            llm=self.llm
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.conversational_agent = initialize_agent(
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            max_iterations=3,
            memory=self.memory,
        )

    def setup_docstore_agent(self):
        docstore = DocstoreExplorer(Wikipedia())
        tools = [
            Tool(
                name="Search",
                func=docstore.search,
                description='search wikipedia'
            ),
            Tool(
                name="Lookup",
                func=docstore.lookup,
                description='lookup a term in wikipedia'
            )
        ]

        self.docstore_agent = initialize_agent(
            tools,
            self.llm,
            agent="react-docstore",
            verbose=True,
            max_iterations=3
        )

    def setup_self_ask_with_search_agent(self):
        search = SerpAPIWrapper(serpapi_api_key='api_key')  # Replace 'api_key' with your actual API key
        tools = [
            Tool(
                name="Intermediate Answer",
                func=search.run,
                description='google search'
            )
        ]

        self.self_ask_with_search_agent = initialize_agent(
            tools, 
            self.llm, 
            agent="self-ask-with-search", 
            verbose=True
        )

    def run_and_count_tokens(self, agent, query):
            """
            Executes the given agent with the specified query and counts the tokens used.

            Args:
            agent: The agent to be executed.
            query: The query string for the agent.

            Returns:
            The result of the agent's execution.
            """
            with get_openai_callback() as cb:
                result = agent(query)
                print(f'Spent a total of {cb.total_tokens} tokens')
            print("token count=", result)
            return result

# Test the agents
    
# Create an instance of AgentCreator
agent_creator = AgentCreator()

# Execute the SQL agent
result = agent_creator.run_and_count_tokens(
    agent_creator.agent_executor,
    "What is the multiplication of the ratio between stock " +
    "prices for 'ABC' and 'XYZ' in January 3rd and the ratio " +
    "between the same stock prices in January the 4th?"
)

# Execute the conversational agent
result = agent_creator.run_and_count_tokens(
    agent_creator.conversational_agent,
    "What's the result of an investment of $10,000 growing at 8% annually for 5 years with compound interest?"
)

# Set up the Docstore agent
agent_creator.setup_docstore_agent()
# Execute the Docstore agent
result = agent_creator.run_and_count_tokens(
    agent_creator.docstore_agent,
    "What were Archimedes' last words?"
)

# Set up the Self Ask with Search agent
agent_creator.setup_self_ask_with_search_agent()

# Example of executing the Self Ask with Search agent
# result = agent_creator.run_and_count_tokens(
#     agent_creator.self_ask_with_search_agent,
#     "What is the tallest building in the world?"
# )