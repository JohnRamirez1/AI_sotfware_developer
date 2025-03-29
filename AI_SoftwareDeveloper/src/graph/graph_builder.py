from langgraph.graph import StateGraph, START,END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from src.state.state import State
from src.nodes.generate_user_stories import User_Stories, ProductOwnerReview, HumanLoopProductOwnerReview, DecisionProductOwnerReview, route_product_owner_review
from src.nodes.create_desing_docs import DocumentsDesigner, UserStoriesReview, DesignDocumentReview, HumanLoopDesingDocumentReview, DecisionDesigDocumentReview, route_document_review

class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)
    
    def test_code_builder(self):
        """
        Builds an advanced code developer graph with tool integration.
        This method creates a code developer graph that includes both user_stories_node, 
        doc_developer_node and code_developer_node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        # user stories nodes
        self.user_story_node = User_Stories(self.llm)
        self.po_review_node = ProductOwnerReview(self.llm)
        self.humanloop_po_review_node = HumanLoopProductOwnerReview()
        self.decision_po_review_node = DecisionProductOwnerReview(self.llm)
        self.graph_builder.add_node("generate_user_stories", self.user_story_node.user_story_planner)
        self.graph_builder.add_node("product_owner_review", self.po_review_node.review_user_stories)
        self.graph_builder.add_node("human_loop_product_owner_review", self.humanloop_po_review_node.get_human_feedback)
        self.graph_builder.add_node("decision_product_owner_review", self.decision_po_review_node.decision_review)
        
        # documents nodes
        self.document_desing_node = DocumentsDesigner(self.llm)
        self.us_review_node = UserStoriesReview(self.llm)
        self.dd_review_node = DesignDocumentReview(self.llm)
        self.humanloop_dd_review_node = HumanLoopDesingDocumentReview()
        self.decision_dd_review_node = DecisionDesigDocumentReview(self.llm)
        self.graph_builder.add_node("create_design_docs", self.document_desing_node.design_document_planner)
        self.graph_builder.add_node("revise_user_stories", self.us_review_node.user_stories_reviewer)
        self.graph_builder.add_node("desing_review", self.dd_review_node.design_document_reviewer)
        self.graph_builder.add_node("human_loop_design_review", self.humanloop_dd_review_node.get_human_feedback)
        self.graph_builder.add_node("decision_design_review", self.decision_dd_review_node.decision_review)

        # graph
        self.graph_builder.add_edge(START,"generate_user_stories")
        self.graph_builder.add_edge("generate_user_stories","product_owner_review")
        self.graph_builder.add_edge("product_owner_review","human_loop_product_owner_review")
        self.graph_builder.add_edge("human_loop_product_owner_review","decision_product_owner_review")
        self.graph_builder.add_conditional_edges(
            "decision_product_owner_review",
            route_product_owner_review,
            {
            "Accepted": "create_design_docs",
            "Rejected + Feedback": "generate_user_stories",
            },
        )
        self.graph_builder.add_edge("create_design_docs","revise_user_stories")
        self.graph_builder.add_edge("revise_user_stories","desing_review")
        self.graph_builder.add_edge("desing_review","human_loop_design_review")
        self.graph_builder.add_edge("human_loop_design_review","decision_design_review")
        self.graph_builder.add_conditional_edges(
            "decision_design_review",
            route_document_review,
            {
            "Accepted": END,
            "Rejected + Feedback": "revise_user_stories",
            },
        )

        return self.graph_builder
