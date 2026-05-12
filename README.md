# Nexora Scholar

Nexora Scholar is an Azure Foundry multi-agent planning assistant designed to help busy professionals create realistic weekly plans across work, fitness, meals, recovery, hobbies, and personal wellbeing.

The tool reads a user’s uploaded Google Calendar export, identifies available time blocks, and generates a Monday-to-Sunday plan that respects existing calendar commitments. It uses specialised Azure Foundry agents for scheduling, training, and meal planning, then presents the result through a modern dashboard with charts, weekly reports, daily views, and a copilot chat interface.

## How to Run the App

### 1. Install dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Create a .env file

Create a .env file in the root directory of the project and add your Azure Foundry project endpoint and agent IDs.

```
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT

Scholar_AGENT_ID=asst_your_Scholar_agent_id
TRAINER_AGENT_ID=asst_your_trainer_agent_id
DIETICIAN_AGENT_ID=asst_your_dietician_agent_id
```

Replace the placeholder values with your own Azure Foundry details:

- FOUNDRY_PROJECT_ENDPOINT — your Azure Foundry project endpoint
- Scholar_AGENT_ID — the agent ID for the Scholar/orchestrator agent
- TRAINER_AGENT_ID — the agent ID for the personal trainer agent
- DIETICIAN_AGENT_ID — the agent ID for the dietician/meal planning agent

### 3. Login to Azure

This app uses Azure Foundry Agents, so you need to authenticate with your Azure account before running it.

Make sure Azure CLI is installed, then run:

```bash
az login
```

After logging in, select the Azure subscription that contains your Azure Foundry project and agents.

### 4. Run the Streamlit app

Start the application with:

```bash
streamlit run app.py
```

---

## What Nexora Scholar Does

Nexora Scholar helps users plan a week ahead by combining:

- Existing calendar commitments
- Deep work blocks
- Weekly work and life tasks
- Fitness goals
- Training history
- Meal planning
- Recovery routines
- Sleep protection
- Self-care and hobbies
- ADHD-friendly planning preferences

The goal is not just to create a to-do list, but to generate a realistic and balanced weekly schedule that fits into the user’s actual available time.

---

## Key Features

### 1. Calendar-Aware Weekly Planning

Users upload a Google Calendar `.ics` file. Nexora Scholar parses the events, converts them to GMT+8, and identifies available time blocks for the upcoming Monday-to-Sunday week.

The system preserves existing calendar events and only schedules new activities inside available free blocks.

### 2. Azure Foundry Multi-Agent Architecture

Nexora Scholar uses multiple Azure Foundry agents, each responsible for a different planning layer:

- **Scholar Agent**  
  Creates the final weekly schedule while respecting calendar constraints.

- **Trainer Agent**  
  Designs a weekly training plan based on yearly fitness goals, training history, stress level, and available workout windows.

- **Dietician Agent**  
  Creates a meal plan based on calorie targets, dietary preferences, cuisine preferences, meal prep time, and the training load for the week.

This separation allows the system to behave more like a coordinated planning team rather than a single generic chatbot.

### 3. Fitness and Training Support

The assistant can support goals such as:

- HYROX-style training
- Marathon progression
- Long-run building
- Strength and hybrid training
- Pilates
- Yoga
- HIIT
- Swimming
- Active recovery
- Sauna / ice bath / mobility suggestions

It also keeps previous training recommendations in local history so future weekly plans can consider what was suggested before.

### 4. Meal Planning

The Dietician Agent generates meal suggestions that consider:

- Calorie target
- Number of meals per day
- Dietary preferences
- Cuisine preferences
- Meal prep time
- Training load
- Busy calendar days

The output includes meal options and macro estimates for protein, carbohydrates, and fats.

### 5. ADHD-Friendly Planning Mode

Nexora Scholar includes an ADHD-friendly planning option. When enabled, the schedule aims to:

- Reduce overwhelm
- Limit must-do tasks per day
- Break work into smaller steps
- Include breaks
- Avoid excessive task switching
- Make the weekly plan easier to scan and follow

### 6. Modern Dashboard

The app displays the generated plan using a modern dashboard-style interface, including:

- Weekly motivation banner
- Summary KPI cards
- Time distribution donut chart
- Macro distribution donut chart
- Weekly schedule cards
- Daily view
- Weekly report layout
- Raw agent output viewer

### 7. Copilot Chat

After a plan is generated, users can interact with Nexora Scholar through a chat interface.

Example follow-up requests:

- “Move my run to Thursday.”
- “Make Wednesday lighter.”
- “Reduce cooking time.”
- “Add more protein.”
- “Shift deep work to the morning.”
- “Add more recovery because I feel tired.”

The chat updates the schedule while preserving calendar constraints.

### 8. PDF Export

Users can download the weekly report as a PDF for offline use or sharing.

---

## System Architecture

```text
Google Calendar Export (.ics)
        ↓
Calendar Parser + Free Block Generator
        ↓
Trainer Agent
        ↓
Dietician Agent
        ↓
Scholar Agent
        ↓
Dashboard + Weekly Report + Daily View + Copilot Chat
        ↓
PDF Export + Local History