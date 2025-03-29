import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class GroqLLM:
    def __init__(self,user_controls_input):
        self.user_controls_input=user_controls_input

    def get_llm_model(self):
        try:
            api_key=self.user_controls_input['api_key']
            selected_model=self.user_controls_input['selected_model']
            if api_key=='' and selected_model =='':
                st.error("Please Enter the Groq API KEY")
            os.environ["GROQ_API_KEY"] = api_key
            llm = ChatGroq(model=selected_model)

        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
    
class OpenAILLM:
    def __init__(self,user_controls_input):
        self.user_controls_input=user_controls_input

    def get_llm_model(self):
        try:
            api_key=self.user_controls_input['api_key']
            selected_model=self.user_controls_input['selected_model']
            if api_key=='' and selected_model =='':
                st.error("Please Enter the api key and model")
            os.environ["OPENAI_API_KEY"] = api_key
            llm = ChatOpenAI(model=selected_model)
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
    