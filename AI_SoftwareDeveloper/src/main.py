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
for event in graph.stream(initial_input, thread, stream_mode="updates"):
    print(f"\n=== run {n} ===")
    print(event)
    n+=1

# # Run graph with updated state
# initial_input = {"requirement": HumanMessage(content="Create code for snake game")}
# thread = {"configurable": {"thread_id": "1"}}

# event = {}
# flag_initial = True
# n = 0
# while 'document_code' not in event:
#     if flag_initial:
#         #stream first time
#         for event in graph.stream(initial_input, thread, stream_mode="updates"):
#             if "decision_po_review" in event:
#                 print(f"\n=== run {n} ===")
#                 # print(event)
#         flag_initial = False
#     else:
#         # Run execution with new state
#         print(f"\n=== next step to execute {n} ===")
#         for event in graph.stream(None, thread, stream_mode="updates"):
#             print(f"\n=== run {n} ===")
        
#     state=graph.get_state(thread)
#     print(f"current state: {state}")
#     # Verify if we are in Product_Owner_Review nodes and modify state
#     if "decision_po_review" in state.values:
#         # humman in the loop to Update the status 
#         new_decision = input("Decision About User Stories: Please confirm decision about user stories 'Rejected' or 'Accepted' if no changes are needed:\n")
#         if new_decision in ('Rejected', 'Accepted'):
#             # state["decision_po_review"] = new_decision
#             state.values["decision_po_review"] = new_decision
#             if "writes" in state.metadata:
#                 state.metadata["writes"]["decision_product_owner_review"] = {"decision_po_review": new_decision}
#             thread["configurable"]["state"] = state  
#             # memory.save_state(thread["configurable"]["thread_id"], state)
#             # memory.restore(thread["configurable"]["thread_id"], state)
#             # event["decision_po_review"] = new_decision
#             # thread["configurable"]["state"] = event  #save the status into thread
#             # print(f"Updated state to input and continuing execution...")
#             # print("\n=== updated decision about user stories ===")
#             # print(event['decision_po_review'])

#     elif "decision_dd_review" in state.values:
#     # elif "decision_dd_review" in event:
#         # humman in the loop to Update the status 
#         new_decision = input("Decision Desing Documents: Please confirm decision about Desing Documents 'Rejected' or 'Accepted' if no changes are needed:\n")
#         if new_decision in ('Rejected', 'Accepted'):
#             state.values["decision_dd_review"] = new_decision
#             if "writes" in state.metadata:
#                 state.metadata["writes"]["decision_design_review"] = {"decision_dd_review": new_decision}
#             # event["decision_dd_review"] = new_decision
#             # # Run the graph with updated state
#             # thread["configurable"]["state"] = event  #save the status into thread
#             # print(f"Updated state to input and continuing execution...")
#             # print("\n=== updated decision about desing document ===")
#             # print(event['decision_dd_review'])
#     n += 1

# print(state)