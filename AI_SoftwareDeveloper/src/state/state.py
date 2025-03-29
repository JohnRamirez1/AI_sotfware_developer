from typing_extensions import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field

class UserStory(TypedDict, total=False):
    name: str = Field( description="Name for this user story.",)
    description: str = Field( description="Description for this user story",)
 
class UserStories(BaseModel):
    user_stories: List[UserStory] = Field(
        description=" User Stories of the project",
    )

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
    parent_folder: Literal["backend", "frontend", "dependencies", "config"] = Field(
        ..., description="Category where the file belongs (e.g., backend, frontend, dependencies, config)"
    )
    file_name: str = Field(..., description="File name with extension (e.g., 'app.py')")
    generated_code: str = Field(..., description="Generated code content to be stored in the file")

class GeneratedProject(BaseModel):
    project_name: str = Field(..., description="Name of the generated project")
    code_files: List[GeneratedCode] = Field(default=[], description="List of generated code files")


# class DesignDoc(TypedDict, total=False):
#     name: str = Field(description="Name for this desing document.",)
#     description: str = Field(description="Content of this desing document.",)
#     doc_type: Literal["Functional", "Technical", "API Spec"]
#     link: Optional[str]  # URL or path to the document
#     status: Literal["Draft", "Approved", "In Review"]
#     user_story_ids: List[int]  # Ensures doc aligns with User Stories

# class TestResult(TypedDict, total=False):
#     test_name: str
#     status: Literal["Passed", "Failed", "Skipped"]
#     log: Optional[str]  # Error details (if failed)
#     related_file: Optional[str]  # Links test to a specific file (if applicable)
#     related_code_id: Optional[int]  # Links test to a specific CodeFile
#     user_story_id: Optional[int]  # Ensures tests validate user needs

# class CodeFile(TypedDict, total=False):
#     id: int
#     filename: str
#     language: str
#     document_link: str  # URL or file path
#     status: Literal["Generated", "Pending Review", "Reviewed", "Approved", "Refactored", "Tested", "Deployed", "Deprecated"]
#     test_results: Optional[List[TestResult]]
#     version: Optional[int]
#     user_story_id: Optional[int]  # Links code to a User Story
#     design_doc_id: Optional[int]  # Ensures code is based on design

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

    # implementation_scripts:Optional[list[]]
    # design_docs: Optional[List[DesignDoc]]
    # code: Optional[List[CodeFile]]
    # global_test_results: Optional[List[TestResult]]  
    # deployment_status: Optional[Literal["Not Deployed", "In Progress", "Passed", "Failed", "Rolled Back"]]