from src.state.state import State, CodReview, DecisionCodReview, GeneratedProject
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

class CodeGenerator:
    """
    Node to generate user stories given some code request.
    """
    def __init__(self,model):
        self.llm = model

    def code_developer(self, state: State)-> dict:
        """Orchestrator that generates code content based on functional and technical document"""

        # Augment the LLM with schema for structured output
        planner = self.llm.with_structured_output(GeneratedProject)
        
        # Convert design_documents list into a readable string
        design_docs_list = state.get("design_documents", [])
        
        # if not design_docs_list:
        #     design_documents_str = "No design documents provided."
        # else:
        #     design_documents_str = "\n\n".join(
        #         [f"### {doc['name']}\n{doc['description']}" for doc in design_docs_list]
        #     )

        prompt_template = PromptTemplate(
            input_variables=["requirement", "design_documents", "code_review_feedback", "human_code_review"],
            template="""
            You are an expert AI Software Engineer specializing in full-stack development. Your task is to generate fully functional, end-to-end project code based on the provided **Functional Design Document (FDD)** and **Technical Design Document (TDD)**. The generated code must:

            1. **Follow Best Practices** - Ensure modularity, scalability, maintainability, and security.
            2. **Be Complete & Functional** - Each part of the code should integrate seamlessly, forming a fully operational project.
            3. **Match the Provided Architecture** - The system should align with the documented backend, frontend, database, and API structure.
            4. **Include Dependencies & Configuration** - Generate appropriate package dependencies (`package.json`, `requirements.txt`, `Dockerfile`, `config.yaml`, `.env`, etc.).
            5. **Ensure Code Readability & Documentation** - Provide inline comments and relevant README instructions.
            6. **Implement Security Measures** - Follow secure coding practices, including authentication, authorization, and encryption where necessary.
            7. **Follow CI/CD and Deployment Guidelines** - If applicable, generate scripts for testing, building, and deploying the application.

            ### Provided Inputs:
            - **Project Requirements:** {requirement}
            - **Functional & Technical Design Documents:** {design_documents}
            - **Code Review Feedback:** {code_review_feedback}
            - **Human Review Feedback:** {human_code_review}

            ### Expected Output:
            - **Project Structure** (e.g., backend, frontend, config, dependencies, API, services).
            - **Fully Implemented Source Code** for backend and frontend.
            - **API Endpoints & Database Models** matching the design.
            - **Configuration & Setup Files** for easy deployment.

            Ensure that the generated code is **ready for execution** with minimal modifications.
            """
        )

        # Generate user stories
        print("\n=== Input Documents code developer===")
        print(f"{state.get('design_documents',[])}")
        generated_project = planner.invoke(
            [
                SystemMessage(content=prompt_template.format(
                    requirement=state.get('requirement'),
                    design_documents=state.get('design_documents',[]),
                    code_review_feedback=state.get('code_review_fedback', "None"),
                    human_code_review=state.get('human_code_review', "None")
                )),
            ]
        )   
        return {"generated_project": generated_project}    
    
class CodeReview:
    """
    Node to review generated code before approval.
    """
    def __init__(self, model):
        self.llm = model

    def ai_code_reviewer(self, state: State) -> dict:
        """AI-assisted review code project."""
        reviewer = self.llm.with_structured_output(CodReview)

        review_feedback = reviewer.invoke([
            SystemMessage(content="""
            You are an AI **Full-Stack Software Engineer & Code Reviewer**. Your role is to **critically analyze** the generated project code **end-to-end**
            and provide **detailed, actionable feedback** to ensure that the software is **functional, maintainable, scalable, and secure**.
            
            ## 🔍 Your Review Focus:
            1. **Completeness** - Ensure all required features, modules, and integrations are implemented.
            2. **Code Quality** - Evaluate maintainability, modularity, and adherence to best practices.
            3. **Functionality** - Verify that the code achieves its intended purpose and is executable.
            4. **Security & Performance** - Identify vulnerabilities and potential performance bottlenecks.
            5. **Architectural Consistency** - Ensure adherence to the proposed design documents and technology stack.
            6. **API & Database Design** - Validate endpoints, request-response formats, and database schema.
            7. **Scalability & Deployment Readiness** - Suggest improvements for handling high loads and CI/CD readiness.
            
            **Instructions:**
            - Provide **specific** observations and examples where the code needs improvement.
            - Suggest **refinements** and optimizations with precise recommendations.
            - Highlight **potential risks** and how to mitigate them.
            - Ensure that all components **align with the functional and technical design documents**.
            """),
            HumanMessage(content=f"""
            **Generated Project Code:** {state['generated_project']}
            **Functional and Technical Design Documents:** {state['design_documents']}
            
            Review the code based on the above focus areas and provide structured feedback with actionable recommendations.
            """),
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
        print("An AI Full-Stack Software Engineer & Code Reviewer has suggested changes to the code project.")
        print(f"Here are the code project:\n{state['generated_project']}\n")
        print(f"Here is the code review feedback feedback:\n{state['code_review_feedback']}\n")
        
        # Simulate human feedback collection (replace with actual input UI in production)
        human_review = input("Please enter any modification required for code project or type 'Accepted' if no changes are needed:\n")
        
        # print("\n=== Human Review Feedback ===")
        # print(f"human_po_review {human_review.strip()}")
        # print(f"state: {state}")
        return {"human_code_review": human_review}
   
class DecisionCodeReview:
    """
    Node to generate approve or reject decision based on review feedback.
    """
    def __init__(self, model):
        self.llm = model

    def ai_decision_reviewer(self, state: State) -> dict:
        """Checks if review feedback was met and decides to approve or reject the project code."""

        evaluator = self.llm.with_structured_output(DecisionCodReview)
        print("\n=== Input State in DecisionProductOwnerReview ===")
        print(f"State: {state}")


        code_reviewer = evaluator.invoke([
            SystemMessage(content=(
                "You are an AI responsible for making the final decision on user stories. "
                "Your task is to determine whether the suggested improvements from the product owner review "
                "and human-in-the-loop review have been incorporated properly."
            )),
            HumanMessage(content=(
                f"Here is the latest code review feedback:\n{state['code_review_feedback']}\n\n"
                f"Here is the latest human review feedback:\n{state['human_code_review']}\n\n"
                f"Here are the code:\n{state['generated_project']}\n\n"
                "Evaluate the review feedback, human review feedback with the generated_project and\n"
                "decide if all necessary changes are incorporated or generated_project needs to be updated."
            )),
        ])
        print("\n=== Decision Code Review Feedback ===")
        print(f"decision_code_review_fedback: {code_reviewer.decision_code_review}")

        if "times_reject_code" not in state:
            state["times_reject_code"] = 0  
            print(f"init times_reject_code: {state['times_reject_code']}")
        else:
            state["times_reject_code"] += 1
            print(f"update times_reject_code: {state['times_reject_code']}")
    
        return { "decision_code_review_feedback": str(code_reviewer.decision_code_review), "times_reject_code": state["times_reject_code"]}
    
def route_code_review(state: State) -> dict:
    """Checks if code are approved and passes them to the next stage."""
       
    if state["decision_code_review_feedback"] == "Accepted" or state["times_reject_code"]>=4:
        return "Accepted"
    
    elif state["decision_code_review_feedback"] == "Rejected":
        return "Rejected + Feedback"
        