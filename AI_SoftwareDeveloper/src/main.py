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

code_developer = GraphBuilder(model)
graph_builder = code_developer.test_code_builder()  
memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)
graph.get_graph().draw_mermaid_png(output_file_path='agentic_code_builder.png')

# # Define input
# initial_input = {"requirement": HumanMessage(content="Create code for snake game")}

# # Run the graph and get final state
# final_state = graph.invoke(initial_input, config={"recursion_limit": 100, "thread_id": "my_thread_1"})

# # Save final state to JSON
# import json
# with open("final_output_state.json", "w") as f:
#     json.dump(final_state, f, indent=2, default=str)

# print("✅ Final state saved to final_output_state.json")

initial_input = {"requirement": HumanMessage(content="Create code for snake game")}
thread = {"configurable": {"thread_id": "1"}}
n = 0

for event in graph.stream(initial_input, config={"recursion_limit": 100, "thread_id": "my_thread_1"}):
    print(f"\n=== run {n} ===")
    print(event)
    n+=1
