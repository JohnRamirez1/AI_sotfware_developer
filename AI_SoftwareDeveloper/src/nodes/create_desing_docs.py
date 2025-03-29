from src.state.state import State, DesignDocuments, DDReview, DecisionDDReview
from langchain_core.messages import HumanMessage, SystemMessage


class DocumentsDesigner:
    """
    node to generate user stories given some code request.
    """
    def __init__(self,model):
        self.llm = model

    def design_document_planner(self, state: State)-> dict:
        """Orchestrator that generates design documents based on input user stories"""

        # Augment the LLM with schema for structured output
        planner = self.llm.with_structured_output(DesignDocuments)
        
        project_design_documents = planner.invoke(
            [
                SystemMessage( content="You are an AI expert designing functional and technical documents to develop sofware projects.\n"
                "Based on the following user stories, generate a\n"
                "comprehensive design documents. The document should include functional and\n"
                "technical details, key components, and system interactions. Ensure clarity in architecture, data flow, and dependencies."),
                HumanMessage(content=f"Here is the user stories: {state['user_stories']} "),
            ]
            )                    
        return {"design_documents": project_design_documents}  
    
class UserStoriesReview:
    """
    node to generate user stories given some code request.
    """
    def __init__(self,model):
        self.llm = model

    def user_stories_reviewer(self, state: State)-> dict:
        """Orchestrator that generates design documents based on input user stories"""

        # Augment the LLM with schema for structured output
        planner = self.llm.with_structured_output(DesignDocuments)
        
        # Generate user stories
        if state.get('decision_dd_review')=='Rejected':
            project_design_documents = planner.invoke(
                [
                    SystemMessage( content="You are an AI expert designing functional and technical documents to develop sofware projects.\n"
                    "Based on the following user stories, generate a comprehensive design documents. The document should include functional and\n"
                    "technical details, key components, and system interactions. Ensure clarity in architecture, data flow, and dependencies. \n"
                    "to improve the initial design documents, the user stories, the product owner feedback and human-in-the-loop review"),
                    HumanMessage(content=f"Here is the initial design documents {state['design_documents']} the user stories: {state['user_stories']}, product owner feedback: {state['dd_review']} and human-in-the-loop review {state['human_dd_review']}"),
                ]
            )                    
        elif state.get('decision_dd_review','Initial')=='Initial':
            project_design_documents = planner.invoke(
                    [
                        SystemMessage(content="You are an AI expert designing functional and technical documents to develop sofware projects.\n"
                    "Based on the following user stories, generate a comprehensive design documents. The document should include functional and\n"
                    "technical details, key components, and system interactions. Ensure clarity in architecture, data flow, and dependencies.\n"
                    "to generate the design functional and technical documents take into account the user stories"
                    ),
                        HumanMessage(content=f"Here is the user stories: {state['user_stories']}"),
                    ]
                )    
        return {"design_documents": project_design_documents}

class DesignDocumentReview:
    """
    Node to review generated user stories before approval.
    """
    def __init__(self, model):
        self.llm = model

    def design_document_reviewer(self, state: State) -> dict:
        """AI-assisted review of user stories by the product owner."""
        doc_reviewer = self.llm.with_structured_output(DDReview)

        review_feedback = doc_reviewer.invoke([
            SystemMessage(content="You are an AI expert in functional and technical document reviewer developed based on user stories. \n"
            "Your goal is to Evaluate the design documents for completeness, correctness, and feasibility. \n"
            "Identify potential issues related to scalability, security, and maintainability. Provide constructive feedback and suggest improvements."),
            HumanMessage(content=f"Here are the generated documents: {state['design_documents']}. "
                             "Design review report with identified issues and suggestions."),
        ])
        
        # print("\n=== Product Owner Review Feedback ===")
        # print(f"Product Owner Review Feedback: {review_feedback}")
        # print(f"state: {state}")
        return {"dd_review": review_feedback}

class HumanLoopDesingDocumentReview:
    """
    Human-in-the-loop product owner review process.
    """
    @staticmethod
    def get_human_feedback(state: State) -> dict:
        """Collects human feedback on the Product Owner review."""
        
        print("\n=== Human Review Required for Desing Document===")
        print("An AI has suggested changes to the Design Documents.")
        print(f"Here are the original design documents:\n{state['design_documents']}\n")
        print(f"Here is the Design Document review feedback:\n{state['dd_review']}\n")
        
        # Simulate human feedback collection (replace with actual input UI in production)
        human_review = input("Please enter any modifications for desing documents or type 'Accepted' if no changes are needed:\n")
        
        # print("\n=== Human Review Feedback ===")
        # print(f"human_po_review {human_review.strip()}")
        # print(f"state: {state}")
        return {"human_dd_review": human_review}
   
class DecisionDesigDocumentReview:
    """
    Node to generate approve or reject decision based on review feedback.
    """
    def __init__(self, model):
        self.llm = model

    def decision_review(self, state: State) -> dict:
        """Checks if review feedback was met and decides to approve or reject the user stories."""

        evaluator = self.llm.with_structured_output(DecisionDDReview)
        print("\n=== Input State in DecisionProductOwnerReview ===")
        print(f"State: {state}")


        decision_review = evaluator.invoke([
            SystemMessage(content=(
                "You are an AI responsible for making the final decision on functional and technical desing documents. "
                "Your task is to determine whether the suggested improvements from the design document review "
                "and human-in-the-loop review have been incorporated properly."
            )),
            HumanMessage(content=(
                f"Here is the latest desing document review feedback:\n{state['dd_review']}\n\n"
                f"Here is the latest human review feedback:\n{state['human_dd_review']}\n\n"
                f"Here are the user stories:\n{state['user_stories']}\n\n"
                f"Here are the design documents:\n{state['design_documents']}\n\n"
                "Evaluate the desing document review feedback, human review feedback with the user stories and\n"
                "document review to decide if all necessary changes was incorporated or user documents needs to be updated."
            )),
        ])
        print("\n=== Document Review Feedback ===")
        print(f"decision_dd_review: {decision_review.decision_dd_review}")
        return {"decision_dd_review": str(decision_review.decision_dd_review)}
    
def route_document_review(state: State) -> dict:
    """Checks if documents was approved and passes them to the next stage."""
    print("\n=== Route Design Document Review ===")
    print(f"decision_dd_review: {state['decision_po_review']}")
    if state["decision_dd_review"] == "Accepted":
        return "Accepted"
    elif state["decision_dd_review"] == "Rejected":
        return "Rejected + Feedback"
    