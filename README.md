# Shark Tank Pitch Simulator

A web application that simulates a Shark Tank pitch experience using AI-powered judges. This project was migrated from Jupyter notebooks to a full-stack web application with FastAPI backend and React frontend.

## Project Structure

```
shark-tank-app/
├── backend/
│   ├── main.py              # FastAPI server with all endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Your actual environment variables
│   
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Application styles
│   │   ├── main.jsx        # React entry point
│   │   ├── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── vite.config.js      # Vite configuration
│   ├── package.json        # Node dependencies
│   └── .env                # Your actual frontend env vars
│   
└── README.md               # This file
```

## Features

- **Complete Business Pitch Setup**: Define your business idea with all key details
- **Multiple Judge Agents**: Add and configure multiple AI judges with different personalities
- **Real-time Chat Interface**: Interactive conversation with judges
- **Iterative Feedback**: Continue the conversation and respond to judge concerns
- **Example Templates**: Load example business ideas to get started quickly
- **Conversation History**: Track the full pitch conversation

## Migration from Notebooks

### What was preserved:
- ✅ All agent creation logic (Entrepreneur and Judge agents)
- ✅ Business idea structure and validation
- ✅ Task creation and crew execution
- ✅ Conversation history tracking
- ✅ API connection testing
- ✅ Support for both OpenAI and Azure OpenAI
- ✅ Ability to respond multiple times to judge feedback

### What changed:
- 🔄 Ngrok tunnel → Direct FastAPI server (no longer needed for web app)
- 🔄 Manual cell execution → Automatic web UI interactions
- 🔄 Two separate notebooks → Single integrated web application
- 🔄 Hardcoded variables → Environment variables (.env file)
- 🔄 Print statements → React UI components
- 🔄 Threading for server → Standard FastAPI deployment

## Installation

### Prerequisites

- Python 3.12 (same as Google Colab environment)
- Node.js 18+ and npm
- OpenAI API key OR Azure OpenAI access

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Edit `.env` and add your API keys:
```env
# For Azure OpenAI (recommended, as used in notebooks)
API_TYPE=azure
AZURE_API_KEY=your_azure_api_key_here
AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYMENT=gpt-4o-mini
AZURE_API_VERSION=2024-02-01

# OR for OpenAI
API_TYPE=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Edit `.env` if needed (default should work):
```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend (Terminal 1):

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

The backend will start on `http://localhost:8000`

### Start Frontend (Terminal 2):

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### Access the Application:

Open your browser and navigate to `http://localhost:3000`

## Usage Guide

### 1. Setup Your Pitch

- **Business Idea**: Fill in all the fields for your business
  - Name, Description, Target Market, Revenue Model, etc.
  - Or click "Load Example" to see a sample business
  
- **Judges Configuration**: 
  - At least one judge is required (Mark Cuban is pre-configured)
  - Click "+ Add Another Judge" to add more judges
  - Customize each judge's name and backstory

### 2. Start the Pitch

- Click "Start Pitch" button
- The system will generate your initial pitch automatically
- The judge(s) will respond with questions or feedback

### 3. Continue the Conversation

- Read the judge's response
- Type your answer in the input field
- Click "Send" or press Enter
- Continue the conversation until the judge makes a final decision

### 4. Start Over

- Click "Start Over" to reset and pitch a new business idea

## Example Business Ideas

The application includes an example business (EcoTrack) that you can load. Here are more examples from the notebooks:

### Tech SaaS Example:
```
Name: DataSense AI
Description: An AI-powered data analysis platform for small and medium businesses
Target Market: SMBs without dedicated data science teams
Revenue Model: Tiered SaaS subscription based on data volume and features
Current Traction: 50 paying customers, $15,000 MRR, 15% month-over-month growth
Investment Needed: $500,000 for 15% equity
Use of Funds: Expanding engineering team, enhancing AI capabilities, sales and marketing
```

### Consumer Product Example:
```
Name: GreenPlate
Description: Biodegradable, plant-based food containers that replace single-use plastics
Target Market: Eco-conscious restaurants, food delivery services, and consumers
Revenue Model: Direct B2B sales to restaurants and wholesale to retailers
Current Traction: Partnerships with 10 local restaurants, LOIs from 2 regional chains
Investment Needed: $250,000 for 20% equity
Use of Funds: Scaling production, certifications, and expanding distribution channels
```

## API Endpoints

The backend provides the following endpoints:

- `GET /` - Health check
- `POST /api/test-connection` - Test AI API connection
- `POST /api/start-pitch` - Initialize new pitch session
- `POST /api/send-message` - Send message in conversation
- `GET /api/conversation-history` - Get conversation history
- `POST /api/reset` - Reset conversation

### API CURL Examples

```bash
curl --location --request POST 'http://localhost:8000/'
```
```json
{
    "status": "Shark Tank Chat API is running"
}
```
```bash
curl --location --request POST 'http://localhost:8000/api/test-connection'
```
```json
{
    "status": "success",
    "message": "Connection test successful",
    "api_type": "AZURE",
    "response": "Hello, the connection is working! I am using the OpenAI API."
}
```
```bash
curl --location 'http://localhost:8000/api/start-pitch' \
--header 'Content-Type: application/json' \
--data '{
  "business_idea": {
    "name": "EcoTrack",
    "description": "A smart home energy management system that uses AI to optimize energy usage",
    "target_market": "Environmentally conscious homeowners and small businesses",
    "revenue_model": "Hardware sales + monthly subscription for premium features",
    "current_traction": "500 beta users, $50,000 in pre-orders",
    "investment_needed": "$300,000 for 10% equity",
    "use_of_funds": "Product refinement, marketing, and team expansion"
  },
  "judges": [
    {
      "name": "Mark Cuban",
      "role": "Shark Tank Judge",
      "goal": "Evaluate business pitches critically and decide whether to invest",
      "backstory": "You are a successful entrepreneur and investor on Shark Tank. You have a keen eye for promising businesses and can quickly identify flaws in business models. You are tough but fair, and you always ask penetrating questions about revenue, margins, customer acquisition costs, and scaling strategies. You'\''re not afraid to say '\''I'\''m out'\'' if the numbers don'\''t add up or if you don'\''t believe in the entrepreneur'\''s ability to execute."
    }
  ],
  "entrepreneur_name": "Alex Johnson"
}'
```
```json
{
    "response": "Responses from 1 judge(s)",
    "sender": "Judge",
    "conversation_history": [
        {
            "role": "Entrepreneur",
            "content": "Hello Sharks, I'm Alex Johnson, and today I'm excited to present to you EcoTrack, a revolutionary smart home energy management system that leverages the power of AI to optimize energy usage for environmentally conscious homeowners and small businesses.\n\nAs we all know, energy consumption is a leading contributor to climate change. Many homeowners and small businesses struggle to monitor and control their energy usage, leading to high costs and inefficiency. EcoTrack addresses this pressing issue by providing real-time energy monitoring, automated optimization suggestions, and AI-driven insights that empower users to reduce their carbon footprint and save money.\n\nOur target market is booming; with the rising awareness of sustainability, there are millions of environmentally conscious homeowners and small businesses looking for innovative solutions. We have already gained traction with 500 beta users and received $50,000 in pre-orders, validating our market demand and the effectiveness of our product.\n\nWhat sets EcoTrack apart is not just our cutting-edge technology but our team. Our diverse team combines years of expertise in AI, renewable energy, and consumer electronics. We are uniquely positioned to lead this market, offering a blend of technical innovation and user-friendly design that resonates with our target customers.\n\nToday, I'm seeking a $300,000 investment for 10% equity in EcoTrack. This funding will be instrumental in refining our product, ramping up marketing efforts, and expanding our team to meet growing demand. \n\nWith your investment, we can accelerate our growth, make a significant impact on energy consumption, and pave the way for a sustainable future. Thank you for considering EcoTrack as your next investment!",
            "sender_name": "Alex Johnson"
        },
        {
            "role": "Judge",
            "content": "Your final answer must include a thorough evaluation and critical questioning of the entrepreneur's pitch, focusing on the revenue model, customer acquisition costs, financial scalability, marketing differentiation, operational strategy, and potential challenges before making a final investment decision.",
            "judge_name": "Mark Cuban"
        }
    ]
}
```

## Troubleshooting

### LiteLLM Issues

The application uses **litellm==1.74.9** (exact version from the notebooks) to ensure compatibility. If you encounter LiteLLM errors:

1. Verify you're using the correct version:
```bash
pip show litellm
```

1. Ensure your API keys are correctly set in `.env`

2. Test the connection using the `/api/test-connection` endpoint

### Connection Issues

- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000
- Check that `.env` files are properly configured
- Verify no firewall is blocking the ports

### Agent Not Responding

- Check backend logs for errors
- Verify API keys are valid and have sufficient credits
- Ensure the API endpoint is correct for your provider (OpenAI vs Azure)

## Library Versions

The application uses the exact same library versions as the Google Colab notebooks to ensure compatibility:

- crewai==0.201.1
- litellm==1.74.9
- langchain==0.3.27
- langchain-openai==0.3.34
- openai==1.108.0

Full list in `backend/requirements.txt`

## Development

### Adding More Judges

The system supports multiple judges. To add a new default judge, modify the `judges` state in `App.jsx`:

```javascript
const [judges, setJudges] = useState([
  // existing judge...
  {
    name: 'Barbara Corcoran',
    role: 'Shark Tank Judge',
    goal: 'Evaluate retail and consumer businesses',
    backstory: 'You specialize in retail and consumer products...'
  }
]);
```

### Customizing Agent Behavior

Edit the agent creation functions in `backend/main.py`:

- `create_judge_agents()` - Customize judge behavior
- `create_entrepreneur_agent()` - Customize entrepreneur behavior

## Production Deployment

For production deployment:

1. Use a proper WSGI server for FastAPI (gunicorn + uvicorn workers)
2. Build the React frontend: `npm run build`
3. Serve the built frontend through a web server (nginx, Apache)
4. Use environment-specific `.env` files
5. Implement proper session management (Redis, database)
6. Add authentication and authorization
7. Set up proper CORS policies
8. Use HTTPS for all communications

## License

This project is based on the original Jupyter notebooks for educational purposes.

## Support

If you encounter issues:
1. Check the console logs (browser and backend)
2. Verify all environment variables are set correctly
3. Ensure you're using Python 3.12 and the exact library versions
4. Review the notebook comments for original functionality

---

**Note**: This application maintains all the functionality from the original Jupyter notebooks while providing a better user experience through a web interface.
