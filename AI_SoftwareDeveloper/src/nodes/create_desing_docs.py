from src.state.state import State, DesignDocuments, DDReview, DecisionDDReview
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
# import json


class DocumentsDesigner:
    """
    Node to generate Functional and Technical Design Documents based on user stories.
    """
    SYSTEM_PROMPT = (
        "You are an AI expert specializing in software architecture and design documentation. "
        "Your role is to generate **Functional Design Documents (FDD)** and **Technical Design Documents (TDD)** "
        "based on the provided user stories. Ensure clarity, completeness, and adherence to industry best practices.\n\n"
        "**Guidelines:**\n"
        "- The Functional Design Document (FDD) should focus on user workflows, system interactions, and feature descriptions.\n"
        "- The Technical Design Document (TDD) should cover system architecture, data structures, APIs, and security considerations.\n"
        "- Follow standard documentation formats and use clear, structured Markdown output.\n\n"
        "Now, generate the design documents using the following user stories."
    )

    def __init__(self, model):
        self.llm = model

    def design_document_planner(self, state: State) -> dict:
        """Orchestrates the generation of design documents based on user stories."""
        planner = self.llm.with_structured_output(DesignDocuments)
        
        user_stories = state.get("user_stories", "No user stories provided.")
        
        project_design_documents = planner.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"User Stories:\n{user_stories}")
        ])
        
        return {"design_documents": project_design_documents.design_documents}
    
# class UserStoriesReview:
    """
    Node to generate design documents based on user stories.
    """
    def __init__(self, model):
        self.llm = model

    def user_stories_reviewer(self, state: State) -> dict:
        """Generates Functional and Technical Design Documents based on user stories."""

        # Augment the LLM with a structured output schema
        planner = self.llm.with_structured_output(DesignDocuments)

        # Extract state variables with default values
        user_stories = state.get("user_stories", "No user stories provided.")
        existing_documents = state.get("design_documents", "None")
        dd_review_feedback = state.get("dd_review", "None")
        human_review_feedback = state.get("human_dd_review", "None")

        # Define the prompt template
        prompt_template = """
        You are an expert software architect. Your task is to generate a **Functional Design Document (FDD)** 
        and a **Technical Design Document (TDD)** based on the given user stories. Format the output in **Markdown**.

        ---
        **📌 User Stories:** {user_stories}
        **📄 Existing Design Documents:** {design_documents}
        **📌 Product Owner Feedback:** {dd_review}
        **📌 Human Review Feedback:** {human_dd_review}
        ---

        ## 📄 Functional Design Document (FDD)
        - **Objective**: Describe the purpose of the application.
        - **User Roles & Permissions**: Define user types and their capabilities.
        - **Features & Functional Modules**: List major system modules and functions.
        - **Workflows & User Interactions**: Outline key workflows and user actions.
        - **System Integrations**: Identify external APIs or databases needed.
        - **Non-Functional Requirements**: Define performance, security, and compliance standards.
        - **Acceptance Criteria**: Set clear validation conditions.

        ## 📄 Technical Design Document (TDD)
        - **System Architecture**: Describe the system structure (e.g., microservices, monolith).
        - **Technology Stack**: Recommend programming languages, frameworks, and databases.
        - **Module Breakdown**: Provide details on each module’s logic.
        - **APIs & Contracts**: Define API endpoints, input/output formats, and integration details.
        - **Data Models & Storage**: Outline the database schema and relationships.
        - **Security & Authentication**: Detail access control, encryption, and data protection.
        - **Deployment & CI/CD**: Describe deployment pipelines, testing, and automation strategies.
        - **Scalability & Fault Tolerance**: Recommend caching, load balancing, and failure recovery.

        Ensure the documents are **modular, scalable, and follow best practices**.
        """

        # Generate prompt with available data
        updated_prompt = prompt_template.format(
            user_stories=user_stories,
            design_documents=existing_documents,
            dd_review=dd_review_feedback,
            human_dd_review=human_review_feedback
        )

        # Generate the design documents using the LLM
        project_design_documents = planner.invoke([SystemMessage(content=updated_prompt)])

        return {"design_documents": project_design_documents}

class DesignDocumentReview:
    """
    Node to review design documents for completeness and quality.
    """
    REVIEW_PROMPT = (
        "You are an expert software architect reviewing Functional and Technical Design Documents. "
        "Your goal is to evaluate the documents for completeness, accuracy, and feasibility based on the given user stories. \n\n"
        "**Review Criteria:**\n"
        "1. **Completeness**: Are all required features and components documented?\n"
        "2. **Clarity**: Is the document structured logically and easy to understand?\n"
        "3. **Technical Feasibility**: Do the proposed solutions align with best practices and technology constraints?\n"
        "4. **Scalability & Security**: Are performance, security, and maintainability properly addressed?\n"
        "5. **Consistency**: Do the documents align with the user stories and acceptance criteria?\n\n"
        "Provide a structured review identifying gaps, inconsistencies, or improvements needed."
    )

    def __init__(self, model):
        self.llm = model

    def design_document_reviewer(self, state: State) -> dict:
        """AI-assisted review of design documents."""
        doc_reviewer = self.llm.with_structured_output(DDReview)

        review_feedback = doc_reviewer.invoke([
            SystemMessage(content=self.REVIEW_PROMPT),
            HumanMessage(content=f"Here are the generated design documents:\n{state.get('design_documents', 'No design documents available.')}")
        ])

        return {"dd_review": review_feedback.dd_review}

class HumanLoopDesignDocumentReview:
    """
    Human-in-the-loop product owner review process.
    """
    @staticmethod
    def get_human_feedback(state: State) -> dict:
        """Collects human feedback on the Product Owner review."""
        
        print("\n=== Human Review Required for Design Document ===")
        print("An AI has suggested changes to the Design Documents.")
        print(f"\n🔹 Original Design Documents:\n{state['design_documents']}\n")
        print(f"\n📌 AI Review Feedback:\n{state['dd_review']}\n")
        
        # Collect human feedback with a clearer message
        human_review = input(
            "Please enter any modifications for the Design Documents, or type 'Accepted' if no changes are needed:\n"
        ).strip()
        
        # Validate input
        if not human_review:
            print("⚠️ No input provided. Defaulting to 'Pending Review'.")
            human_review = "Pending Review"
        
        return {"human_dd_review": human_review}
   
class DecisionDesignDocumentReview:
    """
    Node to approve or reject functional and technical design documents based on review feedback.
    """
    def __init__(self, model):
        self.llm = model

    def decision_review(self, state: State) -> dict:
        """Checks if review feedback was met and decides to approve or reject the design documents."""
        
        evaluator = self.llm.with_structured_output(DecisionDDReview)

        # print("\n=== Input State in Decision Review ===")
        # print(json.dumps(state, indent=4))  # Print state in readable JSON format

        # Invoke evaluator for the review decision
        decision_review = evaluator.invoke([
            SystemMessage(content=(
                "You are an AI responsible for making the final decision on functional and technical design documents. "
                "Your task is to determine whether the suggested improvements from the design document review "
                "and human-in-the-loop review have been properly incorporated."
            )),
            HumanMessage(content=(
                f"**Latest Design Document Review Feedback:**\n{state.get('dd_review', 'No review available')}\n\n"
                f"**Latest Human Review Feedback:**\n{state.get('human_dd_review', 'No human review available')}\n\n"
                f"**User Stories:**\n{state.get('user_stories', 'No user stories provided')}\n\n"
                f"**Design Documents:**\n{state.get('design_documents', 'No design documents available')}\n\n"
                "Based on the design document review feedback, human review feedback, and user stories, "
                "determine whether all necessary changes have been incorporated or if the design documents need further updates."
            )),
        ])

        # Extract the decision and handle potential errors
        decision = str(decision_review.decision_dd_review).strip() if hasattr(decision_review, "decision_dd_review") else "Rejected"
    
        # Initialize or update rejection count
        state.setdefault("times_reject_dd", 0)
        if decision == "Rejected":
            state["times_reject_dd"] += 1
        
        print("\n=== Decision Document Review Feedback ===")
        print(f"Decision: {decision}")
        print(f"Updated Rejection Count: {state['times_reject_dd']}")

        return {
            "decision_dd_review": decision,
            "times_reject_dd": state["times_reject_dd"]
        }
    
def route_document_review(state: State) -> dict:
    """Checks if documents was approved and passes them to the next stage."""
    # print("\n=== Route Design Document Review ===")
    # print(f"decision_dd_review: {state['decision_po_review']}")
    if state["decision_dd_review"] == "Accepted" or state["times_reject_dd"]>=1:
        return "Accepted"
    elif state["decision_dd_review"] == "Rejected":
        return "Rejected + Feedback"
    