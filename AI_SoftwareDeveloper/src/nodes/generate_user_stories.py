from src.state.state import State, UserStories,POReview, DecisionPOReview
from langchain_core.messages import HumanMessage, SystemMessage


class User_Stories:
    """
    node to generate user stories given some code request.
    """
    def __init__(self,model):
        self.llm = model

    def user_story_planner(self, state: State)-> dict:
        """Orchestrator that generates user stories for the code based on the requirement"""

        # Augment the LLM with schema for structured output
        planner = self.llm.with_structured_output(UserStories)
        
        # Generate user stories
        if state.get('decision_po_review')=='Rejected':
            project_user_stories = planner.invoke(
                [
                    SystemMessage( content="Generate the user stories plan for the project but aditional from requirement take into account the product owner feedback.\n"
                    "to improve the user stories take into account the initial user stories, the initial requirement and the product owner feedback and and human-in-the-loop review"),
                    HumanMessage(content=f"Here is initial user stories {state['user_stories']} the initial requirement: {state['requirement']}, product owner feedback: {state['po_review']} and human-in-the-loop review {state['human_po_review']}"),
                ]
            )                    
        elif state.get('decision_po_review','Initial')=='Initial':
            project_user_stories = planner.invoke(
                    [
                        SystemMessage(content="Generate the user stories plan for the project"),
                        HumanMessage(content=f"Here is the requirement: {state['requirement']}"),
                    ]
                )    
        return {"user_stories": project_user_stories}     

class ProductOwnerReview:
    """
    Node to review generated user stories before approval.
    """
    def __init__(self, model):
        self.llm = model

    def review_user_stories(self, state: State) -> dict:
        """AI-assisted review of user stories by the product owner."""
        reviewer = self.llm.with_structured_output(POReview)

        review_feedback = reviewer.invoke([
            SystemMessage(content="You are a critical product owner reviewing user stories. \n"
            "Your goal is to analyze the user stories, identify missing elements, \n"
            "suggest improvements, and ensure completeness, clarity, and feasibility."),
            HumanMessage(content=f"Here are the generated user stories: {state['user_stories']}. "
                             "Identify any missing requirements, problems with feasibility, clarify vague descriptions, and suggest improvements."),
        ])
        
        # print("\n=== Product Owner Review Feedback ===")
        # print(f"Product Owner Review Feedback: {review_feedback}")
        # print(f"state: {state}")
        return {"po_review": review_feedback}

class HumanLoopProductOwnerReview:
    """
    Human-in-the-loop product owner review process.
    """
    @staticmethod
    def get_human_feedback(state: State) -> dict:
        """Collects human feedback on the Product Owner review."""
        
        print("\n=== Human Review Required ===")
        print("A Product Owner has suggested changes to the user stories.")
        print(f"Here are the original user stories:\n{state['user_stories']}\n")
        print(f"Here is the Product Owner's review feedback:\n{state['po_review']}\n")
        
        # Simulate human feedback collection (replace with actual input UI in production)
        human_review = input("Please enter any modification for user stories or type 'Accepted' if no changes are needed:\n")
        
        # print("\n=== Human Review Feedback ===")
        # print(f"human_po_review {human_review.strip()}")
        # print(f"state: {state}")
        return {"human_po_review": human_review}
   
class DecisionProductOwnerReview:
    """
    Node to generate approve or reject decision based on review feedback.
    """
    def __init__(self, model):
        self.llm = model

    def decision_review(self, state: State) -> dict:
        """Checks if review feedback was met and decides to approve or reject the user stories."""

        evaluator = self.llm.with_structured_output(DecisionPOReview)
        print("\n=== Input State in DecisionProductOwnerReview ===")
        print(f"State: {state}")


        decision_product_owner_review = evaluator.invoke([
            SystemMessage(content=(
                "You are an AI responsible for making the final decision on user stories. "
                "Your task is to determine whether the suggested improvements from the product owner review "
                "and human-in-the-loop review have been incorporated properly."
            )),
            HumanMessage(content=(
                f"Here is the latest product owner review feedback:\n{state['po_review']}\n\n"
                f"Here is the latest human review feedback:\n{state['human_po_review']}\n\n"
                f"Here are the user stories:\n{state['user_stories']}\n\n"
                "Evaluate the product owner review feedback, human review feedback with the user stories and\n"
                "decide if all necessary changes are incorporated or user stories needs to be updated."
            )),
        ])
        print("\n=== Decision Review Feedback ===")
        print(f"decision_po_review: {decision_product_owner_review.decision_po_review}")
        if str(decision_product_owner_review.decision_po_review)=='Rejected':
        times_reject_po += 1
        return {"decision_po_review": str(decision_product_owner_review.decision_po_review)}
    
def route_product_owner_review(state: State) -> dict:
    """Checks if user stories are approved and passes them to the next stage."""
    # print("\n=== Route Product Owner Review ===")
    # print(f"decision_po_review: {state['decision_po_review']}")
    if state["decision_po_review"] == "Accepted":
        return "Accepted"
    elif state["decision_po_review"] == "Rejected":
        return "Rejected + Feedback"