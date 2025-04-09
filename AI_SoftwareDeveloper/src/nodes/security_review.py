from src.state.state import State, GeneratedProject, TestCasesCodes,DecisionTestCases
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
import json

class SecurityReviewer:
    """
    Class to perform security review and improve code security.
    """
    def __init__(self,model):
        self.llm = model
    

    def make_security_review(self, state: State) -> dict:
        """Evaluate the code project to find security vulnerabilities."""
        
        prompt_template = PromptTemplate(
            input_variables=["generated_project"],
            template="""
            Perform a comprehensive security audit of the given codebase. Identify vulnerabilities such as:
            - Injection attacks (SQL, NoSQL, Command, LDAP)
            - Cross-Site Scripting (XSS), CSRF
            - Broken Authentication & Weak Access Controls
            - Security Misconfiguration
            - Insufficient Logging & Monitoring
            - Server-Side Request Forgery (SSRF)
            - Hardcoded secrets and insufficient encryption
            Follow OWASP guidelines and industry best practices. Provide a structured report with:
            - Identified vulnerabilities
            - Risk levels (Critical, High, Medium, Low)
            - Suggested fixes with example code
            """
        )

        review_feedback = self.llm.invoke([
            SystemMessage(content=prompt_template.format(
                generated_project=state.get('generated_project')
            )),
        ])   
        return {"security_review_feedback": review_feedback}
    
    def improve_code_project(self, state: State)-> dict:
        """evaluate the code project in order to fix and ensure functionality and efficiency"""    
        
        code_developer = self.llm.with_structured_output(GeneratedProject)

        prompt_template = PromptTemplate(
            input_variables=["generated_project"],
            template="""
            Apply necessary funcionability fixes to enhance readability, maintainability, and efficiency\n
            while ensuring compliance with coding standards and best practices. \n
            Refactor and reduce complex or redundant code or scripts, improve documentation, and optimize \n
            performance where necessary. Address all identified issues while preserving \n
            the intended functionality.
            """
        )

        # Generate user stories
        review_generated_project = code_developer.invoke(
            [
                SystemMessage(content=prompt_template.format(
                    generated_project=state.get('generated_project')
                )),
            ]
        )   
        return {"generated_project": review_generated_project} 
    
    def improve_security(self, state: State)-> dict:
        """evaluate the code project in order to fix security vulnerabilities"""    
        
        code_developer = self.llm.with_structured_output(GeneratedProject)

        prompt_template = PromptTemplate(
            input_variables=["generated_project"],
            template="""
            Apply necessary security fixes to address vulnerabilities \n
            found in the security review while also improving readability, \n
            maintainability, and efficiency. Implement safeguards such as \n
            input validation, encryption, and secure API calls while \n
            ensuring the code adheres to industry best practices. \n
            Refactor any unclear or inefficient portions of the code \n
            to enhance overall quality before proceeding to deployment.
            """
        )

        # Generate user stories
        review_generated_project = code_developer.invoke(
            [
                SystemMessage(content=prompt_template.format(
                    generated_project=state.get('generated_project')
                )),
            ]
        )   
        return {"generated_project": review_generated_project} 
    
    def write_test_cases(self, state: State)-> dict:
        """Generate test cases for the given project to ensure correctness and security compliance.""" 
        
        code_developer = self.llm.with_structured_output(TestCasesCodes)

        prompt_template = PromptTemplate(
            input_variables=["generated_project"],
            template="""
            *"Given the following code, generate comprehensive test cases \n
            to ensure its correctness, reliability, and edge case handling. Follow these guidelines:\n
            Use unit testing best practices (e.g., pytest, JUnit, unittest, etc., based on the language).\n
            Cover both typical and edge cases.\n
            Ensure tests validate functionality, performance, and error handling.\n
            Maintain readability, maintainability, and efficiency in test structure.\n
            Take into account the name of the input files of generated_project to create the test cases.
            """
        )

        # Generate user stories
        create_test_cases_code = code_developer.invoke(
            [
                SystemMessage(content=prompt_template.format(
                    generated_project=state.get('generated_project')
                )),
            ]
        )   
        return {"test_cases_codes": create_test_cases_code.test_cases_codes}
    
    def test_cases_review(self, state: State) -> dict:
        """Review test cases to ensure adherence to best practices and completeness."""    

        test_cases_codes = state.get('test_cases_codes')

        if not test_cases_codes:
            return {"test_cases_feedback": "No test cases provided for review."}

        test_cases_text = "\n\n".join(f"File: {tc.file_name}\n{tc.generated_code}" for tc in test_cases_codes)

        prompt_template = PromptTemplate(
            input_variables=["test_cases_codes"],
            template="""
            Given the following generated test cases, perform a detailed review to ensure they meet the following criteria:
            - Adherence to unit testing best practices (e.g., pytest, JUnit, unittest, etc.).
            - Comprehensive coverage of typical and edge cases.
            - Proper validation of functionality, performance, and error handling.
            - Readability, maintainability, and efficiency of test structures.

            Identify any missing cases, incorrect assertions, or areas for improvement.
            Provide a structured review with suggested corrections or enhancements.

            Test Cases:
            {test_cases_codes}
            """
        )

        # Generate test cases review
        test_cases_feedback = self.llm.invoke(
            [
                HumanMessage(content=prompt_template.format(test_cases_codes=test_cases_text))
            ]
        )

        return {"test_cases_feedback": test_cases_feedback}
    
    def human_loop_test_cases_review(self, state: State) -> dict:
        """Collects human feedback on the Code Project."""
        
        print("\n=== Human Review Required ===")
        print(" Please review the following test cases and provide feedback based on your expertise. Consider the following aspects:"
        "- Do the tests cover all necessary scenarios, including edge cases?"
        "- Are they correctly structured, readable, and maintainable?"
        "- Do they ensure functionality, performance, and error handling?")
        # print(f"Here are the code project:\n{state['generated_project']}\n")
        # print(f"Here is the test cases review feedback feedback:\n{state['test_cases_code']}\n")
        
        human_review = input("Please enter any modification required for code project or type 'Accepted' if no changes are needed:\n")
        
        # print("\n=== Human Review Feedback ===")
        # print(f"human_po_review {human_review.strip()}")
        # print(f"state: {state}")
        return {"human_test_cases_review": human_review}
    
    def decision_test_cases_review(self, state: State) -> dict:
        """Determines whether the test cases meet all quality criteria and approves or rejects them accordingly."""

        evaluator = self.llm.with_structured_output(DecisionTestCases)
        # print("\n=== Input State in test cases review ===")
        # print(f"State: {state}")


        decision_review = evaluator.invoke([
            SystemMessage(content=(
                "Based on the automated and human reviews of the test cases, make a final decision:"
                "- Approve the test cases if they meet all quality criteria."
                "- Request improvements if issues remain (specify the required changes"
            )),
            HumanMessage(content=(
                f"Here are the test cases feedback:\n{state['test_cases_feedback']}\n\n"
                f"Here are the human test cases review code:\n{state['human_test_cases_review']}\n\n"
                f"Here are the genearted project code:\n{state['generated_project']}\n\n"
                "Evaluate the test cases review feedback, human test cases review feedback and\n"
                "genearted project code to decide if test cases needs to be updated."
            )),
        ])
        
        # print("\n=== Document Review Feedback ===")
        # print(f"decision_test_cases_feedback: {decision_review.decision_test_cases_feedback}")
        if "times_reject_tc" not in state:
            state["times_reject_tc"] = 0  
            # print(f"init times_reject_tc: {state['times_reject_tc']}")
        else:
            state["times_reject_tc"] += 1
            # print(f"update times_reject_tc: {state['times_reject_tc']}")

        print("\n=== Decision Security Review Feedback ===")
        print(f"Decision: {decision_review.decision_test_cases_feedback}")
        print(f"Updated Rejection Count: {state['times_reject_tc']}")

        return {"decision_test_cases_feedback": str(decision_review.decision_test_cases_feedback), "times_reject_tc": state["times_reject_tc"]}

    def fix_test_cases(self, state: State)-> dict:
        """create the code project in order to fix security vulnerabilities"""    
        
        test_cases_reviewer = self.llm.with_structured_output(TestCasesCodes)

        prompt_template = PromptTemplate(
            input_variables=["test_cases_code"],
            template="""
            Revise and improve the following test cases based on the feedback provided in the review. Ensure:  
            - Coverage of all required scenarios, including edge cases.  
            - Proper validation of functionality, performance, and error handling.  
            - Readability, maintainability, and efficiency in test structure.  

            Provide an updated version of the test cases incorporating the necessary fixes."""
            )

        # Generate user stories
        test_cases_feedback = test_cases_reviewer.invoke(
            [
                SystemMessage(content=prompt_template.format(
                    generated_project=state.get('test_cases_code')
                )),
            ]
        )
        # Save final state to JSON
        state['test_cases_code'] = test_cases_feedback
        with open("final_output_state.json", "w") as f:
            json.dump(state, f, indent=2,default=str)
        
        # generated_project = state['generated_project']
        # project_dicts = [item.to_dict() for item in generated_project]
        # with open("generated_project.json", "w") as f:
        #     json.dump(project_dicts, f, indent=2, default=str)

        print("✅ Final state saved to final_output_state.json")   
        return {"test_cases_code": test_cases_feedback}

def route_test_cases_review(state: State) -> dict:
    """Checks if test cases are approved and passes them to the next stage."""
       
    if state["decision_test_cases_feedback"] == "Accepted" or state["times_reject_tc"]>=1:
        return "Accepted"
    
    elif state["decision_test_cases_feedback"] == "Rejected":
        return "Rejected + Feedback"