from src.state.state import State, UserStories,POReview, DecisionPOReview
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

class UserStories:
    """
    Node to generate user stories based on project requirements.
    """
    def __init__(self, model):
        self.llm = model

    def user_story_planner(self, state: State) -> dict:
        """Generates user stories based on the provided requirements and feedback."""

        # Augment LLM with structured schema output
        planner = self.llm.with_structured_output(UserStories)

        prompt_template = PromptTemplate(
            input_variables=["requirement", "user_stories", "po_review", "human_po_review"],
            template="""
            You are an AI-driven **Agile Product Manager** responsible for writing clear, well-defined user stories.
            
            ---
            **Project Requirement:** {requirement}
            **Existing User Stories (if any):** {user_stories}
            **Product Owner Feedback:** {po_review}
            **Human-in-the-Loop Review Feedback:** {human_po_review}
            ---

            **📌 User Story Format:**
            - **Title:** A short, descriptive title.
            - **User Story:** "As a [role], I want to [action], so that [benefit]."
            - **Acceptance Criteria:** Clear, testable conditions for completion.
            - **Priority:** Must-have, should-have, or nice-to-have.
            - **Dependencies:** Any related stories or technical constraints.

            Ensure user stories are **concise, actionable, and adhere to Agile best practices**.
            """
        )

        # Generate user stories based on the review decision
        project_user_stories = planner.invoke([
            SystemMessage(content=prompt_template.format(
                requirement=state['requirement'],
                user_stories=state.get('user_stories', "None"),
                po_review=state.get('po_review', "None"),
                human_po_review=state.get('human_po_review', "None")
            ))
        ])

        return {"user_stories": project_user_stories}     

class ProductOwnerReview:
    """
    Node to review generated user stories before approval.
    """
    def __init__(self, model):
        self.llm = model

    def review_user_stories(self, state: State) -> dict:
        """Performs an AI-assisted product owner review of user stories."""

        reviewer = self.llm.with_structured_output(POReview)

        review_feedback = reviewer.invoke([
            SystemMessage(content=(
                "You are a critical product owner reviewing user stories. "
                "Analyze them for completeness, clarity, feasibility, and adherence to Agile principles. "
                "Identify missing elements, suggest improvements, and flag any inconsistencies."
            )),
            HumanMessage(content=(
                f"Here are the generated user stories:\n{state['user_stories']}\n\n"
                "Identify any missing requirements, feasibility issues, vague descriptions, or areas for improvement."
            )),
        ])

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
        print(f"Original User Stories:\n{state['user_stories']}\n")
        print(f"Product Owner's Review Feedback:\n{state['po_review']}\n")

        # Simulate human feedback collection (replace with actual UI input in production)
        human_review = input("Enter modifications or type 'Accepted' if no changes are needed:\n").strip()

        return {"human_po_review": human_review}
   
class DecisionProductOwnerReview:
    """
    Node to decide whether to approve or reject the user stories.
    """
    def __init__(self, model):
        self.llm = model

    def decision_review(self, state: State) -> dict:
        """Evaluates feedback and determines whether to approve or request changes to user stories."""

        evaluator = self.llm.with_structured_output(DecisionPOReview)

        decision_review_feedback = evaluator.invoke([
            SystemMessage(content=(
                "You are an AI responsible for the final decision on user stories. "
                "Your task is to ensure that the feedback from the product owner and human review has been properly implemented."
            )),
            HumanMessage(content=(
                f"Latest Product Owner Review Feedback:\n{state['po_review']}\n\n"
                f"Latest Human Review Feedback:\n{state['human_po_review']}\n\n"
                f"Updated User Stories:\n{state['user_stories']}\n\n"
                "Evaluate whether all necessary improvements have been incorporated."
                "If issues remain, request revisions. Otherwise, approve the user stories."
            )),
        ])

        # Track rejection count to avoid infinite loops
        state.setdefault("times_reject_po", 0)
        if decision_review_feedback.decision_po_review == "Rejected":
            state["times_reject_po"] += 1
        print("\n=== Decision User Stories Review Feedback ===")
        print(f"Decision: {decision_review_feedback.decision_po_review}")
        print(f"Updated Rejection Count: {state['times_reject_po']}")

        return {"decision_po_review": str(decision_review_feedback.decision_po_review), "times_reject_po": state["times_reject_po"]}

    
def route_product_owner_review(state: State) -> str:
    """Routes user stories based on approval or rejection feedback."""
    
    if state["decision_po_review"] == "Accepted" or state["times_reject_po"] >= 1:
        return "Accepted"
    return "Rejected + Feedback"
