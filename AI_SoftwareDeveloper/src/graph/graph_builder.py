from langgraph.graph import StateGraph, START,END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from src.state.state import State
from src.nodes.generate_user_stories import User_Stories, ProductOwnerReview, HumanLoopProductOwnerReview, DecisionProductOwnerReview, route_product_owner_review
from src.nodes.create_desing_docs import DocumentsDesigner, UserStoriesReview, DesignDocumentReview, HumanLoopDesingDocumentReview, DecisionDesigDocumentReview, route_document_review
from src.nodes.generate_code import CodeGenerator, CodeReview, HumanCodeOwnerReview, DecisionCodeReview, route_code_review
from src.nodes.security_review import SecurityReviewer

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

        # code project
        self.generate_code_node = CodeGenerator(self.llm)
        self.code_review_node = CodeReview(self.llm)
        self.humanloop_code_review_node = HumanCodeOwnerReview()
        self.decision_code_review_node = DecisionCodeReview(self.llm)
        self.graph_builder.add_node("generate_code", self.generate_code_node.code_developer)
        self.graph_builder.add_node("code_review", self.code_review_node.ai_code_reviewer)
        self.graph_builder.add_node("human_loop_code_review", self.humanloop_code_review_node.get_human_feedback)
        self.graph_builder.add_node("decision_code_review", self.decision_code_review_node.ai_decision_reviewer)

        # fix security code
        self.security_review_node = SecurityReviewer(self.llm)
        self.graph_builder.add_node("security_review", self.security_review_node.make_security_review)
        self.graph_builder.add_node("fix_code_after_code_review", self.security_review_node.improve_code_project)
        self.graph_builder.add_node("fix_code_after_security", self.security_review_node.improve_security)
        self.graph_builder.add_node("write_test_cases", self.security_review_node.write_test_cases)


        # graph user stories part
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
        # graph functional and thecnical documents part
        self.graph_builder.add_edge("create_design_docs","revise_user_stories")
        self.graph_builder.add_edge("revise_user_stories","desing_review")
        self.graph_builder.add_edge("desing_review","human_loop_design_review")
        self.graph_builder.add_edge("human_loop_design_review","decision_design_review")
        self.graph_builder.add_conditional_edges(
            "decision_design_review",
            route_document_review,
            {
            "Accepted": 'generate_code',
            "Rejected + Feedback": "revise_user_stories",
            },
        )
        # graph code part
        self.graph_builder.add_edge("generate_code","code_review")
        self.graph_builder.add_edge("code_review","human_loop_code_review")
        self.graph_builder.add_edge("human_loop_code_review","decision_code_review")
        self.graph_builder.add_conditional_edges(
            "decision_code_review",
            route_code_review,
            {
            "Accepted": "security_review",
            "Rejected + Feedback": "generate_code",
            },
        )
        #security code part
        self.graph_builder.add_edge("security_review","fix_code_after_code_review")
        self.graph_builder.add_edge("fix_code_after_code_review","fix_code_after_security")
        self.graph_builder.add_edge("fix_code_after_security","write_test_cases")
        self.graph_builder.add_edge("write_test_cases",END)

        return self.graph_builder
