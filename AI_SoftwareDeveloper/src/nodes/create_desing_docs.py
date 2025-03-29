from src.state.state import State, DesignDocuments, DDReview, DecisionDDReview
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

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
        
        prompt_template = PromptTemplate(
            input_variables=["user_stories", "design_documents", "dd_review", "human_dd_review"],
            template="""
            You are an expert software architect. Your task is to generate a **Functional Design Document (FDD)** and a **Technical Design Document (TDD)**
            for an application based on the given user stories. The output must be formatted in **Markdown**
            
            ---
            **User Stories:** {user_stories}
            **Existing Design Documents (if any):** {design_documents}
            **Product Owner Feedback:** {dd_review}
            **Human-in-the-Loop Review:** {human_dd_review}
            ---
            
            **📄 Functional Design Document (FDD)**
            - **Objective:** Describe the purpose of the application.
            - **User Roles & Permissions:** Define all types of users and their capabilities.
            - **Features & Functional Modules:** List all major system modules and their functions.
            - **Workflows & User Interactions:** Outline key workflows and user actions.
            - **System Integrations:** Identify external APIs or databases required.
            - **Non-Functional Requirements:** Define performance, security, and compliance standards.
            - **Acceptance Criteria:** Set clear validation conditions for feature completion.
            
            **📄 Technical Design Document (TDD)**
            - **System Architecture:** Describe the system architecture (e.g., microservices, monolith, event-driven).
            - **Technology Stack:** Recommend programming languages, frameworks, and databases.
            - **Module Breakdown:** Provide details on each module’s structure and logic.
            - **APIs & Contracts:** Define key API endpoints, input/output formats, and integration logic.
            - **Data Models & Storage:** Outline database schema, data relationships, and storage considerations.
            - **Security & Authentication:** Detail access control, encryption, and data protection measures.
            - **Deployment & CI/CD:** Describe the deployment pipeline, testing, and automation strategies.
            - **Scalability & Fault Tolerance:** Recommend caching, load balancing, and failure recovery strategies.

            Ensure the generated documents are **modular, scalable, and follow best practices**.
            """
        )

        # Generate user stories
        if state.get('decision_dd_review') == 'Rejected':
            project_design_documents = planner.invoke(
                [
                    SystemMessage(content=prompt_template.format(
                        user_stories=state['user_stories'],
                        design_documents=state['design_documents'],
                        dd_review=state['dd_review'],
                        human_dd_review=state['human_dd_review']
                    )),
                ]
            )
        elif state.get('decision_dd_review', 'Initial') == 'Initial':
            project_design_documents = planner.invoke(
                [
                    SystemMessage(content=prompt_template.format(
                        user_stories=state['user_stories'],
                        design_documents="None",
                        dd_review="None",
                        human_dd_review="None"
                    )),
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
        if "times_reject_dd" not in state:
            state["times_reject_dd"] = 0  
            print(f"init times_reject_dd: {state['times_reject_dd']}")
        else:
            state["times_reject_dd"] += 1
            print(f"update times_reject_dd: {state['times_reject_dd']}")

        return {"decision_dd_review": str(decision_review.decision_dd_review), "times_reject_dd": state["times_reject_dd"]}
    
def route_document_review(state: State) -> dict:
    """Checks if documents was approved and passes them to the next stage."""
    print("\n=== Route Design Document Review ===")
    print(f"decision_dd_review: {state['decision_po_review']}")
    if state["decision_dd_review"] == "Accepted" or state["times_reject_dd"]>=1:
        return "Accepted"
    elif state["decision_dd_review"] == "Rejected":
        return "Rejected + Feedback"
    