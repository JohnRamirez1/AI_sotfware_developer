from src.state.state import State, CodReview, DecisionCodReview, GeneratedProject
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

class CodeGenerator:
    """
    Node to generate code based on functional and technical documents.
    """
    SYSTEM_PROMPT = (
        "You are an expert AI Software Engineer specializing in full-stack development. Your task is to generate fully functional, end-to-end project code based on the provided **Functional Design Document (FDD)** and **Technical Design Document (TDD)**. The generated code must:\n"
        "1. **Follow Best Practices** - Ensure modularity, scalability, maintainability, and security.\n"
        "2. **Be Complete & Functional** - Each part of the code should integrate seamlessly, forming a fully operational project.\n"
        "3. **Match the Provided Architecture** - The system should align with the documented backend, frontend, database, and API structure.\n"
        "4. **Include Dependencies & Configuration** - Generate appropriate package dependencies (`package.json`, `requirements.txt`, `Dockerfile`, `config.yaml`, `.env`, etc.).\n"
        "5. **Ensure Code Readability & Documentation** - Provide inline comments and relevant README instructions.\n"
        "6. **Implement Security Measures** - Follow secure coding practices, including authentication, authorization, and encryption where necessary.\n"
        "7. **Follow CI/CD and Deployment Guidelines** - If applicable, generate scripts for testing, building, and deploying the application.\n\n"
        "### Provided Inputs:\n"
        "- **Project Requirements:** {requirement}\n"
        "- **Functional & Technical Design Documents:** {design_documents}\n"
        "- **Code Review Feedback:** {code_review_feedback}\n"
        "- **Human Review Feedback:** {human_code_review}\n\n"
        "### Expected Output:\n"
        "- **Project Structure** (e.g., backend, frontend, config, dependencies, API, services).\n"
        "- **Fully Implemented Source Code** for backend and frontend.\n"
        "- **API Endpoints & Database Models** matching the design.\n"
        "- **Configuration & Setup Files** for easy deployment.\n"
        "Ensure that the generated code is **ready for execution** with minimal modifications."
    )

    def __init__(self, model):
        self.llm = model

    def code_developer(self, state: State) -> dict:
        """Orchestrates the generation of code based on functional and technical documents."""
        planner = self.llm.with_structured_output(GeneratedProject)

        # Safely retrieve design documents and other inputs from state
        design_docs = state.get("design_documents", [])
        requirement = state.get("requirement", "No requirements provided.")
        code_review_feedback = state.get("code_review_fedback", "None")
        human_code_review = state.get("human_code_review", "None")

        # Create the prompt
        prompt = self.SYSTEM_PROMPT.format(
            requirement=requirement,
            design_documents=design_docs,
            code_review_feedback=code_review_feedback,
            human_code_review=human_code_review
        )

        # Generate the code
        generated_project = planner.invoke([SystemMessage(content=prompt)])

        return {"generated_project": generated_project}   
    
class CodeReview:
    """
    Node to review generated code before approval.
    """
    REVIEW_PROMPT = (
        "You are an AI **Full-Stack Software Engineer & Code Reviewer**. Your role is to **critically analyze** the generated project code **end-to-end** "
        "and provide **detailed, actionable feedback** to ensure that the software is **functional, maintainable, scalable, and secure**.\n\n"
        "## 🔍 Your Review Focus:\n"
        "1. **Completeness** - Ensure all required features, modules, and integrations are implemented.\n"
        "2. **Code Quality** - Evaluate maintainability, modularity, and adherence to best practices.\n"
        "3. **Functionality** - Verify that the code achieves its intended purpose and is executable.\n"
        "4. **Security & Performance** - Identify vulnerabilities and potential performance bottlenecks.\n"
        "5. **Architectural Consistency** - Ensure adherence to the proposed design documents and technology stack.\n"
        "6. **API & Database Design** - Validate endpoints, request-response formats, and database schema.\n"
        "7. **Scalability & Deployment Readiness** - Suggest improvements for handling high loads and CI/CD readiness.\n\n"
        "**Instructions:**\n"
        "Provide **specific** observations and examples where the code needs improvement.\n"
        "Suggest **refinements** and optimizations with precise recommendations.\n"
        "Highlight **potential risks** and how to mitigate them.\n"
        "Ensure that all components **align with the functional and technical design documents**."
    )

    def __init__(self, model):
        self.llm = model

    def ai_code_reviewer(self, state: State) -> dict:
        """AI-assisted review of generated project code."""
        reviewer = self.llm.with_structured_output(CodReview)

        # Safely retrieve relevant inputs from state
        generated_project = state.get("generated_project", "No generated project found.")
        design_documents = state.get("design_documents", "No design documents provided.")

        review_feedback = reviewer.invoke([
            SystemMessage(content=self.REVIEW_PROMPT),
            HumanMessage(content=f"**Generated Project Code:** {generated_project}\n**Functional and Technical Design Documents:** {design_documents}\nReview the code based on the above focus areas and provide structured feedback with actionable recommendations.")
        ])

        return {"code_review_feedback": review_feedback}

class HumanCodeOwnerReview:
    """
    Human-in-the-loop code review process.
    """
    @staticmethod
    def get_human_feedback(state: State) -> dict:
        """Collects human feedback on the Code Project."""
        print("\n=== Human Review Required ===")
        print(f"Here is the code project:\n{state.get('generated_project', 'No generated project found.')}")
        print(f"Here is the code review feedback:\n{state.get('code_review_feedback', 'No feedback provided.')}")
        
        human_review = input("Please enter any modification required for code project or type 'Accepted' if no changes are needed:\n")

        return {"human_code_review": human_review}
   
class DecisionCodeReview:
    """
    Node to generate approve or reject decision based on review feedback.
    """
    def __init__(self, model):
        self.llm = model

    def ai_decision_reviewer(self, state: State) -> dict:
        """Decides whether to approve or reject the project code based on review feedback."""
        evaluator = self.llm.with_structured_output(DecisionCodReview)

        # Safely retrieve relevant inputs from state
        code_review_feedback = state.get("code_review_feedback", "No review feedback available.")
        human_code_review = state.get("human_code_review", "No human review available.")
        generated_project = state.get("generated_project", "No generated project found.")

        # Evaluation prompt
        decision_review = evaluator.invoke([
            SystemMessage(content="You are an AI responsible for making the final decision on user stories. Your task is to determine whether the suggested improvements from the product owner review and human-in-the-loop review have been incorporated properly."),
            HumanMessage(content=(
                f"Here is the latest code review feedback:\n{code_review_feedback}\n\n"
                f"Here is the latest human review feedback:\n{human_code_review}\n\n"
                f"Here are the code:\n{generated_project}\n\n"
                "Evaluate the review feedback, human review feedback with the generated_project and decide if all necessary changes are incorporated or generated_project needs to be updated."
            ))
        ])

        decision = getattr(decision_review, "decision_code_review", "Rejected").strip()

        # Track rejection count
        state["times_reject_code"] = state.get("times_reject_code", 0) + (1 if decision == "Rejected" else 0)
        
        print("\n=== Decision Code Review Feedback ===")
        print(f"Decision: {decision}")
        print(f"Updated Rejection Count: {state['times_reject_code']}")

        return {"decision_code_review_feedback": decision, "times_reject_code": state["times_reject_code"]}

    
def route_code_review(state: State) -> dict:
    """Route code for approval or rejection."""
    if state.get("decision_code_review_feedback", "") == "Accepted" or state.get("times_reject_code", 0) >= 4:
        return "Accepted"
    elif state.get("decision_code_review_feedback", "") == "Rejected":
        return "Rejected + Feedback"
        