
from fastapi import HTTPException, Depends
from fastapi_sqlalchemy import db
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from superagi.agents.aria_agents.aria_agent_factory import AriaAgentFactory
from superagi.agents.aria_agents.aria_workflow_handler import AriaWorkflowHandler
from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
from superagi.helper.auth import check_auth
from superagi.lib.logger import logger

class AriaWorkflowRequest(BaseModel):
    task: str
    capability: Optional[str] = None
    agent_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class AriaMultiWorkflowRequest(BaseModel):
    workflow_steps: List[Dict[str, Any]]

def execute_aria_workflow(agent_id: int, workflow_request: AriaWorkflowRequest, 
                         organisation=Depends(check_auth)):
    """
    Execute a single Aria agent workflow
    """
    try:
        handler = AriaWorkflowHandler(db.session, agent_id)
        result = handler.execute_workflow(workflow_request.dict())
        
        return {
            "success": True,
            "agent_id": agent_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing Aria workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def execute_aria_multi_workflow(agent_id: int, workflow_request: AriaMultiWorkflowRequest,
                               organisation=Depends(check_auth)):
    """
    Execute a multi-step Aria agent workflow
    """
    try:
        handler = AriaWorkflowHandler(db.session, agent_id)
        results = handler.execute_multi_agent_workflow(workflow_request.workflow_steps)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error executing Aria multi-workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_aria_agents_info(organisation=Depends(check_auth)):
    """
    Get information about available Aria agents
    """
    try:
        return {
            "available_agents": AriaAgentFactory.get_available_agent_types(),
            "available_capabilities": AriaAgentFactory.get_available_capabilities(),
            "registry_info": {
                "total_agents": len(AriaAgentRegistry.get_all_agents()),
                "total_capabilities": len(AriaAgentRegistry.get_all_capabilities())
            }
        }
    except Exception as e:
        logger.error(f"Error getting Aria agents info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
