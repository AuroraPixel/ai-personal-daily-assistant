# AI-Powered Personal Daily Assistant: Technical Interview Project

## Project Overview

Build an intelligent personal assistant that helps users manage their daily activities through natural conversation. The assistant should use multiple specialized AI agents working together to provide comprehensive support for everyday tasks like checking weather, finding recipes, getting news updates, and managing personal information.

This project demonstrates your ability to build sophisticated multi-agent AI systems using modern technologies including the OpenAI Agents SDK, Model Context Protocol (MCP), and Retrieval-Augmented Generation (RAG).

## Core Requirements

### Technology Stack

**Required Technologies:**
- **OpenAI Agents SDK**: For multi-agent system implementation
- **Model Context Protocol (MCP)**: For API integration architecture  
- **RAG System**: For knowledge-enhanced responses
- **Frontend**: React with TypeScript
- **Backend**: FAST API
- **Database**: MySQL for development (if needed) 

**Provided Resources:**
- OpenAI API key will be provided
- All other APIs are free and require no setup

### Multi-Agent System Design

Implement a collaborative system with **specialized agents**:

1. **Coordinator Agent**: Main conversation handler, intent analyzer, task router
2. **Weather Agent**: Weather information and forecasts
3. **Recipe Agent**: Food recommendations and cooking assistance  
4. **News Agent**: Current events and news summaries
5. **Personal Assistant Agent**: Notes, reminders, and personal data management

Feel free to re-architect or redesign the agentic workflows.

**Agent Collaboration Requirements:**
- Agents must use proper collaboration (such as handoff) mechanisms
- Implement conversation context preservation across agents
- Support complex multi-step workflows requiring multiple agents
- Include error handling and graceful fallbacks

### User Intent Analysis

Build a system that can understand and classify user requests:

- **Intent Classification**: Categorize user requests (weather, recipes, news, personal tasks, general chat)
- **Entity Extraction**: Extract relevant information (locations, dates, food preferences, etc.)
- **Context Management**: Maintain conversation history and user preferences
- **Confidence Scoring**: Handle ambiguous requests appropriately

### MCP Server Implementation

Create **MCP servers** for external API integration, for exmpale:

1. **Weather MCP Server**: Integration with Open-Meteo API (no key required)
2. **Content MCP Server**: Integration with TheMealDB and News APIs  
3. **Data MCP Server**: User data management and preferences

**MCP Requirements:**
- Proper protocol compliance
- Error handling and retry logic
- Resource and tool definitions
- Authentication handling where needed

### RAG Implementation

Build a knowledge base system that enhances agent responses:

- **Knowledge Base**: Create curated content about daily life topics, tips, and best practices
- **Vector Database**: Implement semantic search for relevant information retrieval
- **Integration**: Seamlessly integrate retrieved knowledge into agent responses
- **Content Types**: Include lifestyle tips, cooking advice, weather interpretation, news context

### Core Features

**Chat Interface:**
- Real-time conversation with the assistant
- Support for text input and responses
- Conversation history and context preservation
- Agent handoff indicators and status updates

**Weather Services:**
- Current weather for any location
- Multi-day forecasts
- Weather alerts and recommendations
- Location-based suggestions

**Recipe and Food Assistance:**
- Recipe search by ingredients or cuisine
- Cooking instructions and tips
- Dietary restriction handling
- Meal planning suggestions

**News and Information:**
- Current news summaries
- Topic-specific news filtering
- News source diversity
- Fact-checking and context

**Personal Data Management:**
- Note-taking and reminders
- User preferences and settings
- Conversation history
- Personal context for better assistance

## Free APIs to Use

### Weather API
**Open-Meteo** (https://open-meteo.com/)
- No API key required
- Global weather data
- Current conditions and forecasts
- Example: `https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true`

### Recipe API  
**TheMealDB** (https://www.themealdb.com/api.php)
- Free recipe database
- Search by ingredient, category, or name
- Detailed cooking instructions
- Example: `https://www.themealdb.com/api/json/v1/1/search.php?s=chicken`

### News API
**The News API** (https://www.thenewsapi.com/)
- Free news aggregation
- Multiple sources and categories
- No API key required for basic usage
- Example: `https://api.thenewsapi.com/v1/news/top?locale=us`

### Development/Testing APIs
**JSONPlaceholder** (https://jsonplaceholder.typicode.com/)
- Fake REST API for testing
- User data, posts, comments
- Perfect for development and demos
- Example: `https://jsonplaceholder.typicode.com/users`

## Technical Specifications

### Backend Architecture
- FastAPI application with RESTful API design
- WebSocket support for real-time chat
- MySQL database for development
- Proper error handling and logging
- Environment-based configuration

### Frontend Architecture  
- React with TypeScript for type safety
- Real-time chat interface with WebSocket
- Responsive design for desktop and mobile
- State management for conversation history
- Component-based architecture

### Agent System Architecture
- OpenAI Agents SDK for agent implementation
- Clear agent specialization and responsibilities
- Robust handoff mechanisms between agents
- Context preservation across agent interactions
- Error handling and recovery strategies

### MCP Architecture
- Separate MCP servers for different API categories
- Proper protocol message handling
- Resource and tool definitions
- Authentication and rate limiting
- Comprehensive error handling

### RAG Architecture
- Vector database for semantic search
- Efficient embedding and retrieval strategies
- Knowledge base organization and curation
- Integration with agent reasoning processes
- Performance optimization for real-time use

## Evaluation Criteria

Your implementation will be evaluated on:

**Technical Implementation**
- Proper use of OpenAI Agents SDK
- MCP protocol compliance and server quality
- RAG system effectiveness
- Code quality and architecture

**System Integration**
- Agent collaboration and handoffs
- API integration reliability
- Database design and data management
- Error handling and edge cases

**User Experience**
- Chat interface usability
- Response quality and relevance
- Real-time performance
- Mobile responsiveness

**Code Quality**
- Code organization and documentation
- Testing coverage and quality
- Security best practices
- Deployment readiness

## Resources

- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **Open-Meteo Weather API**: https://open-meteo.com/
- **TheMealDB Recipe API**: https://www.themealdb.com/api.php
- **The News API**: https://www.thenewsapi.com/
- **JSONPlaceholder**: https://jsonplaceholder.typicode.com/


Good luck! This project is designed to showcase your skills in building sophisticated AI applications while working with practical, everyday use cases.

