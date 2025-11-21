"""
FastAPI Backend for Shark Tank Chat Application
Migrated from Jupyter notebooks to web application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Shark Tank Chat API")

# CORS middleware - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== STEP 1: Configuration from notebooks (migrated to .env) =====
# Original: API_TYPE, OPENAI_API_KEY, AZURE_API_KEY, etc.
# New: All loaded from .env file

API_TYPE = os.getenv("API_TYPE", "azure").lower()

if API_TYPE == "openai":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    model_string = OPENAI_MODEL
    logger.info(f"Using OpenAI API with model: {OPENAI_MODEL}")
elif API_TYPE == "azure":
    AZURE_API_KEY = os.getenv("AZURE_API_KEY")
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT", "gpt-4o-mini")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-02-01")
    
    os.environ['AZURE_API_KEY'] = AZURE_API_KEY
    os.environ["AZURE_API_BASE"] = AZURE_ENDPOINT
    os.environ["AZURE_API_VERSION"] = AZURE_API_VERSION
    
    model_string = f"azure/{AZURE_DEPLOYMENT}"
    logger.info(f"Using Azure OpenAI API with deployment: {AZURE_DEPLOYMENT}")
else:
    raise ValueError("API_TYPE must be either 'openai' or 'azure'")

# ===== STEP 2: Data Models =====

class Message(BaseModel):
    content: str
    sender: str  # Entrepreneur

class BusinessIdea(BaseModel):
    name: str
    description: str
    target_market: str
    revenue_model: str
    current_traction: str
    investment_needed: str
    use_of_funds: str

class ChatRequest(BaseModel):
    business_idea: BusinessIdea
    entrepreneur_name: Optional[str] = "Entrepreneur"

class ChatResponse(BaseModel):
    response: str
    sender: str
    conversation_history: List[Dict[str, str]]
    judge_responses: Optional[List[Dict[str, str]]] = None

# ===== STEP 3: Global State =====

conversation_history: List[Dict[str, str]] = []
current_business_idea: Optional[BusinessIdea] = None
judge_agents: List[Agent] = []
current_judges_config: List[Dict[str, str]] = []
entrepreneur_name: str = ""
judge_collaboration_history: List[Dict[str, str]] = []  # Track judge-to-judge communication

# ===== STEP 4: Agent Creation Functions =====
# Migrated from Step 7 (judge notebook) and Step 7 (entrepreneur notebook)

def create_default_judge_agents() -> List[Agent]:
    """
    Create 3 default Shark Tank judge agents:
    - Market Judge 
    - Finance Judge
    - Technology Judge
    """

    default_judges = [
        {
            "name": "Sophia",
            "role": "Market Judge",
            "goal": """
            Evaluate the startup strictly from a market perspective:
            • Customer segmentation
            • Market demand strength
            • Pain point validation
            • Competitive landscape
            • Product differentiation
            • CAC vs LTV feasibility
            • Pricing and distribution strategy
            • Real evidence of market validation

            You can collaborate with other judges by considering their perspectives.

            You must ask a MAXIMUM of 3 market-related questions.

            Rules:
            1. Only ONE question per turn.
            2. Only market-focused questions (no finance, no tech).
            3. Never repeat a question.
            4. After asking 3 total questions → you MUST give a final decision:
               - "I will invest because..."
               - "I'm out because..."
            """,
            "backstory": """
            You are a Shark Tank Market Judge.
            You are analytical, data-driven, and skeptical about exaggerated claims.
            Your expertise includes:
            • market analysis
            • competitive research
            • customer psychology
            • go-to-market strategy
            • growth patterns and validation signals

            Your style:
            • Direct but professional
            • Always challenging assumptions
            • Demand evidence, not buzzwords
            • Drill into gaps in logic or weak positioning
            • You collaborate with other judges and consider their perspectives

            Behavioral Rules:
            • Ask 1 question per message.
            • Only market questions.
            • No repetitive questions.
            • Stop after 3 questions and deliver a final verdict.
            """
        },
        {
            "name": "Marcus",
            "role": "Finance Judge",
            "goal": """
            Evaluate the business from a financial and economic feasibility perspective:
            • Revenue model clarity
            • Unit economics (CAC, LTV, margins)
            • Cash flow sustainability
            • Pricing logic
            • Break-even point
            • Burn rate realism
            • Scalability of the economics
            • Opportunity cost of investment

            You can collaborate with other judges by considering their perspectives.

            Rules:
            1. Ask ONLY financial questions.
            2. One question per turn.
            3. Be extremely strict with numbers and assumptions.
            4. After 3–4 questions → MUST make a final investment decision.
            """,
            "backstory": """
            You are Marcus, a former Wall Street private equity analyst and fractional CFO.
            You excel at tearing down unrealistic financial projections and exposing hidden risks.
            You speak with surgical financial precision, challenge every number, and tolerate no fluff.
            You collaborate with other judges and consider their perspectives when making decisions.
            """
        },
        {
            "name": "Elena",
            "role": "Technology Judge",
            "goal": """
            Evaluate the startup from a technology feasibility and scalability viewpoint:

            Focus areas:
            • Architecture design
            • Codebase scalability
            • Security risks and vulnerabilities
            • Algorithmic logic and complexity
            • Tech stack suitability
            • Data handling and compliance
            • Infrastructure costs vs growth
            • Real innovation vs buzzwords

            You can collaborate with other judges by considering their perspectives.

            Rules:
            1. Ask ONE technical question per message.
            2. No general business or financial questions.
            3. Push the entrepreneur to explain architecture clearly, no vague claims.
            4. After 3-4 total questions → mandatory technical verdict (IN or OUT).
            """,
            "backstory": """
            You are Elena, a senior CTO with 20 years designing scalable distributed systems.
            You are highly technical, allergic to vague buzzwords, and hyper-focused on clarity.
            You quickly spot unrealistic architecture, weak engineering planning, or security flaws.
            You collaborate with other judges and consider their perspectives when making decisions.
            """
        }
    ]

    agents = []

    for judge in default_judges:
        agent = Agent(
            role=judge["role"],
            goal=judge["goal"],
            backstory=judge["backstory"],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model=model_string)
        )

        agents.append(agent)
        logger.info(f"Created judge agent: {judge['name']}")

    return agents

def create_entrepreneur_agent() -> Agent:
    """
    Create the entrepreneur agent (user's proxy in the system)
    Original: entrepreneur_agent from entrepreneur notebook Step 7
    """

    agent = Agent(
        role="Entrepreneur",
        goal="""
Pitch your startup clearly, defend your business model, and answer judge questions 
with persuasive, logical, and data-backed reasoning. Your mission is to secure investment.
""",
        backstory="""
You are an articulate, ambitious, well-prepared founder presenting your startup 
in a Shark Tank environment. You deeply understand your:
• Market  
• Customer  
• Product  
• Traction  
• Competition  
• Revenue strategy  
• Long-term vision  

You communicate with confidence, clarity, and structure.
You NEVER ramble, NEVER contradict yourself, and ALWAYS support claims with logic/data.
If a judge challenges you, respond professionally, strategically, and convincingly.
""",
        verbose=False,
        allow_delegation=False,
        llm=LLM(model=model_string)
    )
    return agent

# ===== STEP 5: Core Logic Functions =====
# Migrated from notebooks' task creation and crew execution

def generate_initial_pitch(business_idea: BusinessIdea, entrepreneur_name: str) -> str:
    """
    Generate initial pitch for the business idea
    Original: initiate_pitch() from entrepreneur notebook Step 10
    """
    entrepreneur_agent = create_entrepreneur_agent()
    
    task = Task(
        description=f"""Create a compelling initial pitch for your business idea.

        Your name is {entrepreneur_name}.

        Your business idea:
        Name: {business_idea.name}
        Description: {business_idea.description}
        Target Market: {business_idea.target_market}
        Revenue Model: {business_idea.revenue_model}
        Current Traction: {business_idea.current_traction}
        Investment Needed: {business_idea.investment_needed}
        Use of Funds: {business_idea.use_of_funds}

        Start your pitch by greeting the judges: "Hello Sharks, I'm {entrepreneur_name}..."
        
        Be enthusiastic and concise. Highlight the problem you're solving, your solution,
        market opportunity, and why your team is uniquely positioned to succeed.
        End with a clear ask for the investment amount and equity offer.""",
        expected_output="A compelling business pitch for Shark Tank",
        agent=entrepreneur_agent,
    )

    crew = Crew(
        agents=[entrepreneur_agent],
        tasks=[task],
    )

    result = crew.kickoff()
    return result.raw

async def generate_judge_responses_with_collaboration(
    business_idea: BusinessIdea, 
    conversation: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Generate judge responses with inter-judge collaboration
    Judges can see each other's responses
    Returns: List of judge response dictionaries with collaboration context
    """
    if not judge_agents:
        raise HTTPException(status_code=400, detail="No judges configured")
    
    responses = []
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
    
    # Build collaboration context from previous judge responses
    collaboration_context = ""
    if judge_collaboration_history:
        collaboration_context = "\n\nOther Judges' Recent Perspectives:\n"
        for judge_msg in judge_collaboration_history[-6:]:  # Last 6 judge messages
            judge_name = judge_msg.get("judge_name", "Unknown")
            content = judge_msg.get("content", "")[:200]
            collaboration_context += f"- {judge_name}: {content}...\n"

    # Generate response from EACH judge with collaboration context
    for idx, judge_agent in enumerate(judge_agents):
        judge_name = current_judges_config[idx]['name'] if idx < len(current_judges_config) else f"Judge {idx + 1}"
        judge_role = current_judges_config[idx]['role'] if idx < len(current_judges_config) else judge_agent.role
        
        task = Task(
            description=f"""You are {judge_name}, the {judge_role}. Evaluate the entrepreneur's pitch and respond appropriately.

            Business being evaluated:
            Name: {business_idea.name}
            Description: {business_idea.description}
            Target Market: {business_idea.target_market}
            Revenue Model: {business_idea.revenue_model}
            Current Traction: {business_idea.current_traction}
            Investment Needed: {business_idea.investment_needed}
            Use of Funds: {business_idea.use_of_funds}

            Conversation history:
            {context}
            
            {collaboration_context}

            IMPORTANT COLLABORATION INSTRUCTIONS:
            - Consider the perspectives of other judges mentioned above
            - You can reference or build upon their questions/concerns
            - If another judge has raised a valid point, you can acknowledge it
            - However, maintain your own unique perspective and expertise

            Respond with your thoughts, questions or investment decision. Be critical but constructive.
            If you need more information, ask specific questions. If you have enough information,
            make your final investment decision.
            
            IMPORTANT: Start your response with "{judge_name}: " to identify yourself clearly.""",
            expected_output="Evaluation and feedback on the entrepreneur's pitch with consideration of other judges' perspectives",
            agent=judge_agent,
        )

        crew = Crew(
            agents=[judge_agent],
            tasks=[task],
        )

        result = crew.kickoff()
        
        response_dict = {
            "judge_name": judge_name,
            "judge_role": judge_role,
            "content": result.raw
        }
        
        responses.append(response_dict)
        
        # Add to collaboration history for next round
        judge_collaboration_history.append({
            "judge_name": judge_name,
            "content": result.raw
        })
    
    return responses

def generate_entrepreneur_response(business_idea: BusinessIdea, conversation: List[Dict[str, str]], user_message: str) -> str:
    """
    Generate entrepreneur's response to judge feedback
    Original: respond_to_feedback() from entrepreneur notebook Step 12
    Modified: Takes user message as input instead of generating automatically
    """
    entrepreneur_agent = create_entrepreneur_agent()
    
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])

    task = Task(
        description=f"""Respond to the Shark Tank judge's feedback or questions.

        Your business idea:
        Name: {business_idea.name}
        Description: {business_idea.description}
        Target Market: {business_idea.target_market}
        Revenue Model: {business_idea.revenue_model}
        Current Traction: {business_idea.current_traction}
        Investment Needed: {business_idea.investment_needed}
        Use of Funds: {business_idea.use_of_funds}

        Conversation history:
        {context}

        User's input: {user_message}

        Respond to the judge's feedback or questions thoughtfully.
        Address any concerns they raise, provide additional details about your business when needed,
        and try to convince them of the value of your idea. Be confident but not arrogant.""",
        expected_output="A thoughtful response to the judge's feedback",
        agent=entrepreneur_agent,
    )

    crew = Crew(
        agents=[entrepreneur_agent],
        tasks=[task],
    )

    result = crew.kickoff()
    return result.raw

# ===== STEP 6: API Endpoints =====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Shark Tank Chat API is running"}

@app.post("/api/test-connection")
async def test_connection():
    """
    Test API connection
    Original: Step 4 test from both notebooks
    """
    try:
        test_llm = LLM(model=model_string)
        test_agent = Agent(
            role="Tester",
            goal="Test API connection",
            backstory="You are a simple agent created to test the API connection.",
            verbose=True,
            llm=test_llm
        )
        
        test_task = Task(
            description="Say 'Hello, the connection is working!' Please confirm which API you're using (OpenAI or Azure).",
            expected_output="A confirmation message",
            agent=test_agent
        )
        
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=1,
            tracing=0
        )
        
        result = test_crew.kickoff()
        return {
            "status": "success",
            "message": "Connection test successful",
            "api_type": API_TYPE.upper(),
            "response": result.raw
        }
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@app.post("/api/start-pitch")
async def start_pitch(request: ChatRequest):
    """
    Initialize a new pitch session
    Original: initiate_pitch() from entrepreneur notebook
    """
    global conversation_history, current_business_idea, judge_agents, current_judges_config, entrepreneur_name, judge_collaboration_history
    
    try:
        # Reset conversation
        conversation_history = []
        judge_collaboration_history = []
        current_business_idea = request.business_idea
        entrepreneur_name = request.entrepreneur_name or "Entrepreneur"
        
        # Create default judges
        judge_agents = create_default_judge_agents()

        # Store judge names for attribution
        current_judges_config = [
            {"name": "Sophia", "role": "Market Judge"},
            {"name": "Marcus", "role": "Finance Judge"},
            {"name": "Elena",  "role": "Technology Judge"},
        ]

        # Generate initial pitch
        initial_pitch = generate_initial_pitch(request.business_idea, entrepreneur_name)
        
        # Add to conversation history
        conversation_history.append({
            "role": "Entrepreneur",
            "content": initial_pitch,
            "sender_name": entrepreneur_name
        })
        
        # Generate responses from ALL judges with collaboration
        judge_responses = await generate_judge_responses_with_collaboration(
            request.business_idea, 
            conversation_history
        )
        
        # Add all judge responses to conversation history
        judge_response_list = []
        for judge_response in judge_responses:
            conversation_history.append({
                "role": "Judge",
                "content": judge_response["content"],
                "judge_name": judge_response["judge_name"],
                "judge_role": judge_response["judge_role"]
            })
            judge_response_list.append({
                "judge_name": judge_response["judge_name"],
                "judge_role": judge_response["judge_role"],
                "content": judge_response["content"]
            })
        
        return ChatResponse(
            response=f"Responses from {len(judge_responses)} judge(s)",
            sender="Judge",
            conversation_history=conversation_history,
            judge_responses=judge_response_list
        )
        
    except Exception as e:
        logger.error(f"Error starting pitch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting pitch: {str(e)}")

@app.post("/api/send-message")
async def send_message(message: Message):
    """
    Send a message in the ongoing conversation
    Original: submit_message and respond_to_feedback from both notebooks
    """
    global conversation_history, current_business_idea, entrepreneur_name
    
    if not current_business_idea:
        raise HTTPException(status_code=400, detail="No active pitch session. Please start a pitch first.")
    
    try:
        # Add user's message to history
        conversation_history.append({
            "role": message.sender,
            "content": message.content,
            "sender_name": entrepreneur_name
        })
        
        # Generate responses from ALL judges with collaboration
        judge_responses = await generate_judge_responses_with_collaboration(
            current_business_idea, 
            conversation_history
        )
        
        # Add all judge responses to conversation history
        judge_response_list = []
        for judge_response in judge_responses:
            conversation_history.append({
                "role": "Judge",
                "content": judge_response["content"],
                "judge_name": judge_response["judge_name"],
                "judge_role": judge_response["judge_role"]
            })
            judge_response_list.append({
                "judge_name": judge_response["judge_name"],
                "judge_role": judge_response["judge_role"],
                "content": judge_response["content"]
            })
        
        return ChatResponse(
            response=f"Responses from {len(judge_responses)} judge(s)",
            sender="Judge",
            conversation_history=conversation_history,
            judge_responses=judge_response_list
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.get("/api/conversation-history")
async def get_conversation_history():
    """
    Get the current conversation history
    """
    return {
        "conversation_history": conversation_history,
        "business_idea": current_business_idea.dict() if current_business_idea else None,
        "judge_collaboration_history": judge_collaboration_history
    }

@app.post("/api/reset")
async def reset_conversation():
    """Reset the conversation and start fresh"""
    global conversation_history, current_business_idea, judge_agents, current_judges_config, entrepreneur_name, judge_collaboration_history
    
    conversation_history = []
    judge_collaboration_history = []
    current_business_idea = None
    judge_agents = []
    current_judges_config = []
    entrepreneur_name = ""
    
    return {"status": "success", "message": "Conversation reset"}

@app.get("/api/judges")
async def get_judges():
    """Get information about active judges"""
    return {
        "judges": current_judges_config,
        "count": len(current_judges_config)
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("BACKEND_PORT", 8000)))
