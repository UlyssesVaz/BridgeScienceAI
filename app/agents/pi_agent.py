# app/agents/pi_agent.py (REFINED - Correct Stub)
# going to be using langgraph?

from typing import Dict, List, Any, Optional
from .base import BaseAgent, VirtualLabState
from app.schemas.project import ConversationMessage, TaskItem
from datetime import datetime, timezone
import uuid
import logging
logger = logging.getLogger(__name__)

class PIAgent(BaseAgent):
    """
    Planning & Intake Agent
    Responsible for parsing documents and creating initial task list.
    """
    
    async def execute(
        self,
        state: VirtualLabState,
        original_research_goal: str,
        user_metadata: Dict[str, Any],
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
        user_role = user_metadata.get('profession', 'Scientist')

        logger.debug(
            "PI Agent execution started with user context.", 
            extra={
                "user_id": user_metadata.get('user_id'),
                "profession": user_role,
                "input_goal_len": len(original_research_goal),
            }
        )
        
        # Log initial action (Audit Log Entry #2)
        state.add_audit_entry(
            agent="pi_agent",
            action="planning_initiated",
            details={
                "user_profession": user_role,
                "original_research_goal": original_research_goal,
                "num_context_files": len(context_files) if context_files else 0
            }
        )
        
        # 1. Simulate AI Refinement (Boilerplate)
        # The AI now uses the profession to set the tone!
        refined_goal = (
            f"Validated Goal for {user_role}: Determine protein function given reaction pathways and contextual documents "
            f"provided by {user_metadata.get('institution', 'the user')}. (Tone adjusted for {user_role}.)"
        )

        # CRITICAL: Store the refined goal in the SCRATCHPAD
        state.scratchpad['refined_research_goal'] = refined_goal


        # 2. Log initiation (Note: The user's initial message and intake audit are added in the Service)
        state.add_audit_entry(
            agent="pi_agent",
            action="planning_initiated",
            details={
                "original_research_goal": original_research_goal, # or should it be redfined_goal?
                "num_context_files": len(context_files) if context_files else 0
            }
        )
        
        # 2. Simulate AI Processing and Response
        
        # Add Assistant Message (The AI's response)
        
        # Add Assistant Message (The AI's public response)
        state.messages.append(
            ConversationMessage(
                role="assistant",
                # Show the refined goal to the user to prove understanding
                content=f"Based on your domain {user_role}. I have refined your objective into the following question: '{refined_goal}'. I have drafted an initial analysis plan based on your request."
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
                "refined_research_goal": refined_goal,
                "tasks_created": len(state.task_list),
                "next_agent": state.next_agent
            }
        )
        
        return state