from src.state.state import State, UserStories,POReview, DecisionPOReview, DesignDocuments
from langchain_core.messages import HumanMessage, SystemMessage


class User_Stories:
    """
    node to generate code given some documents.
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