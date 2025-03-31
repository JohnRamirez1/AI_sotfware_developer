from src.LLMS.llm import GroqLLM, OpenAILLM
from src.graph.graph_builder import GraphBuilder
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

import os
from dotenv import load_dotenv
load_dotenv()

# Configurar el modelo
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

selected_model = 'openai'

if selected_model == 'groq':
    user_input = {
        'api_key': os.getenv("GROQ_API_KEY"),
        'selected_model': "qwen-2.5-32b"
    }
    obj_llm_config = GroqLLM(user_controls_input=user_input)
    model = obj_llm_config.get_llm_model()

elif selected_model == 'openai':
    user_input = {
        'api_key': os.getenv("OPENAI_API_KEY"),
        'selected_model': "gpt-4o"
    }
    obj_llm_config = OpenAILLM(user_controls_input=user_input)
    model = obj_llm_config.get_llm_model()

# Build and Compile the graph
code_developer = GraphBuilder(model)
graph_builder = code_developer.test_code_builder()  
memory = MemorySaver()
# graph = graph_builder.compile(interrupt_after=["decision_product_owner_review","decision_design_review"], checkpointer=memory)
# save graph as PNG
graph = graph_builder.compile(checkpointer=memory)
graph.get_graph().draw_mermaid_png(output_file_path='agentic_code_builder.png')
# state = graph.invoke({"requirement": "Create code for snake game"})

initial_input = {"requirement": HumanMessage(content="Create code for snake game")}
thread = {"configurable": {"thread_id": "1"}}
n = 0
# graph.config(recursion_limit=100)  


for event in graph.stream(initial_input, config={"recursion_limit": 100, "thread_id": "my_thread_1"}):
# for event in graph.stream(initial_input, thread):
    print(f"\n=== run {n} ===")
    print(event)
    n+=1
