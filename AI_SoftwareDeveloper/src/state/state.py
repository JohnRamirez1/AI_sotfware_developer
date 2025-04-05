from typing_extensions import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field

class UserStory(TypedDict, total=False):
    name: str = Field( description="Name for this user story.",)
    description: str = Field( description="Description for this user story",)
 
class UserStories(BaseModel):
    user_stories: List[UserStory] = Field( description=" User Stories of the project",)

class POReview(BaseModel):
    po_review: str = Field(description="As Product Owner provide feedback about user stories.")

class DecisionPOReview(BaseModel):
    decision_po_review: Literal["Accepted", "Rejected"] = Field(description="Decide if the use case is Accepted or not.",)

class DesignDocument(TypedDict, total=False):
    name: str = Field( description="Name for this desing document.",)
    description: str = Field( description="Description for this document",)

class DesignDocuments(BaseModel):
    design_documents: List[DesignDocument] = Field(
        description=" Design Documents of the project",
    )

class DDReview(BaseModel):
    dd_review: str = Field(description="As Technical and Functional Document Reviewer provide feedback about desing documents.")

class DecisionDDReview(BaseModel):
    decision_dd_review: Literal["Accepted", "Rejected"] = Field(description="Decide if the documents are Accepted or not.",)

class GeneratedCode(BaseModel):
    parent_folder: Literal["backend", "frontend", "config", "dependencies", "API", "services"] = Field(
        ..., description="Category where the file belongs (e.g., backend, frontend, dependencies, config")
    file_name: str = Field(..., description="File name with extension (e.g., 'app.py')")
    generated_code: str = Field(..., description="Generated code content to be stored in the file")

class TestCaseCode(BaseModel):
    file_name: str = Field(..., description="File name with extension (e.g., 'app.py')")
    generated_code: str = Field(..., description="Generated test cases code to evaluate the project")

class TestCasesCodes(BaseModel):
    test_cases_codes: List[TestCaseCode] = Field( 
        description=" Test cases of the code project",
        )

class GeneratedProject(BaseModel):
    generated_project: List[GeneratedCode] = Field(description="List of dictionaries with generated code files")

class CodReview(BaseModel):
    code_review_fedback: str = Field(description="As Sofware Developer expert you need to provide feedback about desing documents.")

class DecisionCodReview(BaseModel):
    decision_code_review: Literal["Accepted", "Rejected"] = Field(description="Decide if the codes are accepted or not.",)

class DecisionTestCases(BaseModel):
    decision_test_cases_feedback: Literal["Accepted", "Rejected"] = Field(description="Decide if the test cases are accepted or not.",)

class State(TypedDict, total=False):
    requirement: str # project requirement
    user_stories: Optional[List[UserStory]]
    po_review: Optional[str]
    human_po_review: Optional[str]
    decision_po_review: Optional[str]
    times_reject_po: Optional[int]
    design_documents: Optional[List[DesignDocument]]
    dd_review: Optional[str]
    human_dd_review: Optional[str]
    decision_dd_review: Optional[str]
    times_reject_dd: Optional[int]
    generated_project: Optional[List[GeneratedCode]]
    code_review_feedback: Optional[str]
    human_code_review: Optional[str]
    decision_code_review_feedback: Optional[str]
    times_reject_code: Optional[int]
    security_review_feedback: Optional[str]
    test_cases_codes: Optional[List[TestCaseCode]]
    test_cases_feedback: Optional[str]
    human_test_cases_review: Optional[str]
    decision_test_cases_feedback: Optional[str]
    times_reject_tc: Optional[int]
