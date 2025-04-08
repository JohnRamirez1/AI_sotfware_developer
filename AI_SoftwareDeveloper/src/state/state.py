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
    parent_folder: Literal["backend", "frontend", "config", "dependencies", "API", "services"]
    file_path: str = Field(..., description="Full path relative to parent folder, e.g., 'services/db/db.py'")
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
    requirement: str

    # User Stories
    user_stories: Optional[List[UserStory]] = None
    po_review: Optional[str] = None
    human_po_review: Optional[str] = None
    decision_po_review: Optional[Literal["Accepted", "Rejected"]] = None
    times_reject_po: int = 0

    # Design Docs
    design_documents: Optional[List[DesignDocument]] = None
    dd_review: Optional[str] = None
    human_dd_review: Optional[str] = None
    decision_dd_review: Optional[Literal["Accepted", "Rejected"]] = None
    times_reject_dd: int = 0

    # Code Generation
    generated_project: Optional[List[GeneratedCode]] = None
    code_review_feedback: Optional[str] = None
    human_code_review: Optional[str] = None
    decision_code_review_feedback: Optional[Literal["Accepted", "Rejected"]] = None
    times_reject_code: int = 0

    # Security Review
    security_review_feedback: Optional[str] = None

    # Test Cases
    test_cases_codes: Optional[List[TestCaseCode]] = None
    test_cases_feedback: Optional[str] = None
    human_test_cases_review: Optional[str] = None
    decision_test_cases_feedback: Optional[Literal["Accepted", "Rejected"]] = None
    times_reject_tc: int = 0