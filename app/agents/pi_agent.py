# app/agents/pi_agent.py (REFINED - Correct Stub)
# going to be using langgraph?

from typing import Dict, List, Any, Optional
from .base import BaseAgent, VirtualLabState
from app.schemas.project import ConversationMessage, TaskItem
from datetime import datetime, timezone
import uuid

class PIAgent(BaseAgent):
    """
    Planning & Intake Agent
    Responsible for parsing documents and creating initial task list.
    """
    
    async def execute(
        self,
        state: VirtualLabState,
        research_goal: str,
        context_files: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> VirtualLabState:
        """
        Analyzes research goal and creates a refined research question + initial task plan.
        
        Args:
            state: The initial state workbench.
            research_goal: The user's goal.
            context_files: List of file metadata.
        """
        
        
        # 1. Simulate AI Refinement (Boilerplate)
        refined_goal = f"Validated Goal: Determine protein function given reaction pathways using {len(context_files) if context_files else 0} documents."


        # 2. Log initiation (Note: The user's initial message and intake audit are added in the Service)
        state.add_audit_entry(
            agent="pi_agent",
            action="planning_initiated",
            details={
                "research_goal": research_goal, # or should it be redfined_goal?
                "num_context_files": len(context_files) if context_files else 0
            }
        )
        
        # 2. Simulate AI Processing and Response
        
        # Add Assistant Message (The AI's response)
        state.messages.append(
            ConversationMessage(
                role="assistant",
                content=f"Understood. Your goal is: '{research_goal}'. I've drafted an analysis plan based on the {len(context_files) if context_files else 0} documents provided."
            )
        )
        
        # Create the Initial Task List
        state.task_list = [
            TaskItem(id="t1", description="Search PubMed for latest KP.3 variants literature.", status="pending"),
            TaskItem(id="t2", description="Analyze spike protein mutations.", status="pending"),
        ]

        # 3. CRITICAL: Store the refined goal in the SCRATCHPAD
        state.scratchpad['refined_research_goal'] = refined_goal

        # 3. Transition State and Log Completion
        state.current_phase = "planning_complete"
        state.next_agent = "user_approval"
        
        state.add_audit_entry(
            agent="pi_agent",
            action="planning_complete",
            details={
                "tasks_created": len(state.task_list),
                "next_agent": state.next_agent
            }
        )
        
        return state