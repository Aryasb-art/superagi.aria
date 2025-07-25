# FastAPI Authentication System

## Overview

This is a FastAPI-based authentication system that provides secure user registration and login functionality using JWT tokens and PostgreSQL. The system implements industry-standard security practices including password hashing, token-based authentication, and CORS configuration.

## System Architecture

The application follows a clean, modular architecture with clear separation of concerns:

- **API Layer**: FastAPI framework handling HTTP requests and responses
- **Authentication Layer**: JWT-based token authentication with refresh token support
- **Data Layer**: SQLAlchemy ORM with PostgreSQL database
- **Security Layer**: BCrypt password hashing and token validation
- **Configuration Layer**: Environment-based configuration management

## Key Components

### 1. Authentication System (`auth.py`)
- **Purpose**: Handles password hashing, token creation, and user verification
- **Key Features**:
  - BCrypt password hashing with configurable rounds
  - JWT access token generation (30-minute expiry)
  - JWT refresh token generation (7-day expiry)
  - Password verification utilities
  - HTTP Bearer token scheme implementation

### 2. Database Layer (`database.py`, `models.py`)
- **Purpose**: Manages database connections and data models
- **Architecture**: SQLAlchemy ORM with PostgreSQL backend
- **User Model**: Includes email, password, names, activity status, and timestamps
- **Connection Management**: Connection pooling with pre-ping and recycling

### 3. API Schemas (`schemas.py`)
- **Purpose**: Defines request/response data structures using Pydantic
- **Validation**: Strong password requirements (8+ chars, mixed case, digits)
- **Models**: User creation, login, response, and token schemas

### 4. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Environment Variables**: Database URL, JWT secrets, token expiry times
- **CORS Settings**: Configurable allowed origins for frontend integration

### 5. Main Application (`main.py`)
- **Purpose**: FastAPI application setup and endpoint definitions
- **Middleware**: CORS middleware for cross-origin requests
- **Database**: Automatic table creation on startup
- **Agent Integration**: Added endpoints for AI agent communication

### 6. AI Agents System (`agents/`)
- **BaseAgent**: Abstract base class providing core agent functionality
  - Message handling with receive/respond pattern
  - Logging system with structured message history
  - Status tracking and agent lifecycle management
  - Short-term memory system using deque (10 messages per agent)
  - Memory functions: remember(), recall(), clear_memory()
- **MasterAgent**: Central coordinator for multi-agent communication
  - Message routing based on keywords and context
  - Sub-agent registration and management
  - Broadcasting capabilities for system-wide messages
  - Persian language response support
  - Independent memory system per agent instance
  - Auto-initialization of all agents on startup
- **UtilityAgent**: OpenAI GPT-powered text processing agent
  - Text summarization with Persian output
  - Multi-language translation (Persian ↔ English)
  - Text improvement and error correction
  - General text processing using GPT-4o model
  - Keyword-based routing integration with MasterAgent
  - Error handling for API quota limits
- **ToolAgent**: Advanced task processing agent with comprehensive capabilities
  - Intelligent task type detection with confidence scoring
  - Multi-task support: summarization, translation, extraction, analysis, improvement, conversion, generation, sentiment analysis
  - Sentiment analysis using TextBlob library with Persian output labels
  - Detailed logging of input, output, errors, and task status
  - Processing time tracking and performance metrics
  - Support for both Persian and English responses
  - Auto-registration with MasterAgent routing system
- **SummaryAgent**: Specialized text summarization agent with database storage
  - OpenAI GPT-4o powered summarization with structured output
  - PostgreSQL database integration for summary storage
  - Automatic summaries table creation and management
  - Compression ratio calculation and processing time tracking
  - Support for long-form text summarization (50+ characters minimum)
  - Detailed summary statistics and metadata storage
  - Auto-registration with MasterAgent routing system
- **Integration**: RESTful endpoints for agent interaction in main FastAPI app
- **Memory Testing**: Dedicated `/agent/memory` endpoint for testing memory functionality
- **Utility Endpoints**: `/agent/utility` (authenticated) and `/agent/utility/public` (public) for direct UtilityAgent access
- **Tool Endpoints**: `/agent/tool` (authenticated) and `/agent/tool/public` (public) for direct ToolAgent access with comprehensive task processing
- **Summary Endpoints**: `/agent/summary` (authenticated) and `/agent/summary/public` (public) for direct SummaryAgent access with database storage
- **LongTermMemoryAgent**: Advanced memory management agent with PostgreSQL integration
  - Persistent memory storage with user categorization and tagging system
  - Support for 8 memory categories: هدف، تجربه، درس، یادآوری، احساس، یادداشت، ایده، برنامه
  - Advanced search and retrieval capabilities with text matching
  - Memory endpoints: POST `/agent/longterm/save` and GET `/agent/longterm/fetch`
  - Auto-registration with MasterAgent for combined analysis
- **ConceptualMemoryAgent**: AI-powered conceptual sentence and event analysis agent
  - OpenAI GPT-4o integration for intelligent concept extraction and sentiment analysis
  - Keyword detection fallback when OpenAI API unavailable
  - Support for 8 concept categories: هدف، ارزش، تجربه، اولویت، ترس، انگیزه، نگرانی، الهام‌بخش
  - Sentiment analysis: مثبت، منفی، خنثی with emoji visualization
  - PostgreSQL storage in conceptual_memories table with fields: id, user_id, raw_text, concept, category, sentiment, created_at
  - Conceptual endpoints: POST `/agent/conceptual/save` and GET `/agent/conceptual/latest`
  - Auto-registration with MasterAgent for intelligent routing
- **RepetitiveLearningAgent**: Pattern detection agent that learns from repeated concepts and phrases over time
  - Advanced pattern detection in short-term and long-term memory analysis
  - PostgreSQL storage in repetitive_patterns table with fields: id, user_id, phrase, count, category, last_occurred_at, created_at
  - Configurable thresholds: min_repetition (3), warning (5), critical (10) levels
  - Support for 5 pattern categories: هدف، نگرانی، علاقه، عادت، تکرار
  - Cross-memory analysis including longterm_memories and conceptual_memories tables
  - Warning system with emoji-enhanced levels: 🚨 بحرانی، ⚠️ هشدار، 📝 قابل توجه، ℹ️ عادی، 🆕 جدید
  - Pattern endpoints: POST `/agent/repetitive/observe` and GET `/agent/repetitive/frequent`
  - Auto-registration with MasterAgent for automatic pattern monitoring
- **KnowledgeGraphAgent**: Advanced concept extraction and knowledge graph construction agent
  - OpenAI GPT-4o integration for intelligent concept extraction and relationship mapping
  - Rule-based fallback method when OpenAI API unavailable using NLP patterns
  - Support for 7 relationship types: علت_معلول، شامل، مرتبط، مشابه، متضاد، زمانی، مکانی
  - Support for 8 concept types: شخص، مکان، شیء، ایده، فرآیند، هدف، مشکل، راه‌حل
  - PostgreSQL storage in knowledge_graph table with fields: id, user_id, source_text, concepts, relationships, graph_data, created_at, updated_at
  - Graph structure building for visualization with nodes, edges, and metadata
  - Advanced search and retrieval capabilities across existing knowledge graphs
  - Knowledge graph endpoints: POST `/agent/knowledge-graph/build` and GET `/agent/knowledge-graph/list`
  - Auto-registration with MasterAgent for intelligent routing using graph-related keywords
- **AutoSuggesterAgent**: Intelligent suggestion and contextual guidance agent
  - OpenAI GPT-4o integration for smart text completion and contextual recommendations
  - Rule-based fallback system for suggestion generation when OpenAI unavailable
  - Support for 8 suggestion types: ادامه متن، اقدام بعدی، هشدار، مطالب مرتبط، بهبود، سوال راهنما، هدف پیشنهادی، یادآوری
  - Memory context analysis including short-term, long-term, and conceptual memories
  - Context categorization: goal, problem, completion, learning, general with urgency assessment
  - Theme extraction and pattern recognition from user input and memory
  - PostgreSQL storage in auto_suggestions table with fields: id, user_id, input_text, suggestion, suggestion_type, confidence, context_data, created_at
  - Confidence scoring system (0-1) for all suggestions with visual indicators
  - Auto suggester endpoints: POST `/agent/suggester/complete` and GET `/agent/suggester/hints`
  - Auto-registration with MasterAgent for intelligent routing using suggestion-related keywords
- **GoalInferenceAgent**: Advanced goal and intent detection agent with hybrid analysis
  - Hybrid detection system combining pattern recognition and OpenAI GPT-4o analysis
  - Support for 11 intent categories: action/initiation, decision/choice, concern/worry, motivation/energy, confusion/help, planning/organization, learning/knowledge, health/wellness, relationship/social, career/work, general/other
  - Pattern-based analysis with keyword and phrase matching for high-confidence detection
  - GPT-powered analysis for complex cases with contextual reasoning
  - Memory context integration for better understanding of user patterns and themes
  - Structured JSON output with goal, intent_category, confidence level, and detection method
  - PostgreSQL storage in goal_inferences table with fields: id, user_id, input_text, goal, intent_category, confidence, detected_by, context_data, analysis_details, created_at
  - Confidence levels: high, medium, low with visual indicators
  - Goal inference endpoint: POST `/agent/goal-inference/analyze`
  - Auto-registration with MasterAgent for intelligent routing using goal and intent-related keywords
- **EmotionRegulationAgent**: Advanced emotion detection and regulation agent with therapeutic suggestions
  - Hybrid emotion detection system combining pattern recognition and OpenAI GPT-4o analysis
  - Support for 13 emotion types: خشم، استیصال، اضطراب، هیجان، بی‌انگیزگی، رضایت، خوشحالی، غم، سردرگمی، استرس، ترس، امید، خنثی
  - Three-level intensity detection: mild (خفیف), moderate (متوسط), intense (شدید)
  - Personalized regulation suggestions based on emotion type, intensity, and memory context
  - Emotional pattern detection for escalating negativity and repeated frustration
  - Memory context integration for understanding emotional themes and triggers
  - Structured JSON output with emotion, intensity, regulation_suggestion, and confidence
  - PostgreSQL storage in emotional_states table with fields: id, user_id, input_text, emotion_type, intensity, suggestion, confidence, context_data, created_at
  - Therapeutic suggestions including breathing techniques, activity changes, and warning systems
  - Emotion regulation endpoint: POST `/agent/emotion-regulation/analyze`
  - Auto-registration with MasterAgent for intelligent routing using emotion-related keywords
- **DecisionSupportAgent**: Comprehensive multi-dimensional decision analysis agent
  - Multi-dimensional analysis framework integrating goal, emotion, memory, and risk assessment
  - Goal alignment analysis through GoalInferenceAgent integration with pattern-based fallback
  - Emotional state analysis through EmotionRegulationAgent integration with emotion detection
  - Memory context analysis using short-term memory patterns and decision history
  - Advanced risk assessment system with pattern-based and GPT-4o powered analysis
  - Risk categorization: low (green), medium (yellow), high (red) with visual color coding
  - Confidence scoring system (0-1) based on analysis quality and data availability
  - Comprehensive recommendation engine: proceed, caution, stop with emoji-enhanced output
  - PostgreSQL storage in decision_support table with fields: id, user_id, decision_text, goal_alignment, emotional_state, risk_level, confidence_score, recommendation, analysis_data, created_at
  - Inter-agent communication system for comprehensive analysis using existing specialized agents
  - Structured JSON output with goal_alignment, emotion, risk_level, suggestion for API integration
  - Decision support endpoints: POST `/agent/decision-support/analyze` and GET `/agent/decision-support/list`
  - Auto-registration with MasterAgent for intelligent routing using decision-related keywords
- **SelfAwarenessAgent**: Advanced self-awareness and mental state analysis agent
  - Hybrid analysis system combining OpenAI GPT-4o integration with pattern-based fallback
  - Mental state analysis including self-reflection, metacognitive patterns, and behavioral insights
  - Support for 3 status levels: ok (green), warning (yellow), alert (red) with visual indicators
  - Memory context analysis across short-term, long-term, and conceptual memory systems
  - Self-awareness indicators detection: introspection phrases, emotional labels, growth mindset markers
  - Theme extraction and pattern recognition for consistency and authenticity assessment
  - Message categorization: self-reflection, planning, emotional, learning, general with urgency scoring
  - Confidence scoring system (0-1) based on analysis quality and self-awareness indicators
  - PostgreSQL storage in self_awareness_logs table with fields: id, user_id, input_text, status, alert, confidence, related_memory, analysis_data, created_at
  - Therapeutic recommendations and growth suggestions based on mental state patterns
  - Self-awareness endpoints: POST `/agent/self-awareness/analyze` and GET `/agent/self-awareness/logs`
  - Auto-registration with MasterAgent for intelligent routing using self-awareness keywords
- **InteractiveSecurityCheckAgent**: Advanced cognitive/emotional security threat detection and risk assessment agent
  - Hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent threat detection
  - Support for 8 threat types: burnout, emotional_overload, impulsivity, cognitive_fatigue, stress_overload, decision_paralysis, anxiety_spiral, none
  - Three-level alert system: green (safe), yellow (caution), red (danger) with visual color coding and emoji indicators
  - Risk scoring system (0.0-1.0) with visual progress bars and percentage display for threat assessment
  - Confidence scoring system (0.0-1.0) based on pattern matching quality and GPT analysis reliability
  - Pattern-based threat detection with keyword and phrase matching for high-confidence identification
  - GPT-powered analysis for complex cases requiring contextual reasoning and nuanced threat assessment
  - PostgreSQL storage in security_checks table with fields: id, input_text, detected_threat_type, alert_level, risk_score, recommendation, analysis_data, created_at
  - Personalized security recommendations with actionable advice based on detected threat type and severity
  - Comprehensive analysis output with JSON-structured data and formatted Persian-language reports
  - Security check endpoints: POST `/agent/security-check/analyze` and GET `/agent/security-check/list`
  - Auto-registration with MasterAgent for intelligent routing using security and threat-related keywords
- **RewardAgent**: Advanced positive progress detection and motivational feedback agent
  - Hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent reward detection
  - Support for 6 trigger types: emotional_recovery, goal_alignment, security_improvement, stress_reduction, positive_mindset, breakthrough, consistency
  - Pattern-based detection with keyword and phrase matching for 6 reward categories with Persian and English support
  - GPT-powered analysis for complex cases requiring contextual understanding and personalized motivation
  - Confidence scoring system (0.0-1.0) with visual progress bars and automatic reward triggering when thresholds met
  - Context analysis integration with EmotionRegulationAgent, GoalInferenceAgent, and InteractiveSecurityCheckAgent outputs
  - PostgreSQL storage in reward_logs table with fields: id, timestamp, trigger_type, reward_message, emoji, confidence
  - Motivational message generation with emoji visualization and personalized encouragement quotes
  - Comprehensive reward output with JSON-structured data and formatted Persian-language celebration messages
  - Reward endpoints: POST `/agent/reward/analyze` and GET `/agent/reward/logs`
  - Auto-registration with MasterAgent for intelligent routing using reward and progress-related keywords
- **BiasDetectionAgent**: Advanced cognitive bias detection and reflection agent
  - Hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent bias detection
  - Support for 7 cognitive bias types: Confirmation Bias, Availability Bias, Overconfidence, Anchoring, Sunk Cost Fallacy, Negativity Bias, Framing Effect
  - Pattern-based detection with keyword and phrase matching for cognitive bias identification in Persian and English
  - GPT-powered analysis for complex cases requiring contextual understanding and nuanced bias assessment
  - Severity scoring system (0.0-1.0) with visual progress bars and comprehensive bias analysis reporting
  - Confidence scoring system (0.0-1.0) based on pattern matching quality and GPT analysis reliability
  - PostgreSQL storage in bias_logs table with fields: id, timestamp, input_text, bias_type (array), severity_score, suggestion
  - Reflective suggestion generation with personalized advice based on detected bias type and severity
  - Comprehensive bias output with JSON-structured data and formatted Persian-language reflection messages
  - Bias endpoints: POST `/agent/bias/analyze`, GET `/agent/bias/logs`, and public endpoints for testing
  - Auto-registration with MasterAgent for intelligent routing using bias and cognitive-related keywords
- **SimulatedConsensusAgent**: Collaborative decision-making simulation agent
  - Hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent consensus building
  - Support for 5 virtual agent perspectives with different cognitive approaches: analytical, creative, practical, ethical, balanced
  - Virtual agent personas with distinct characteristics: Conservative Analyst, Creative Thinker, Practical Problem Solver, Ethical Evaluator, Balanced Mediator
  - Weighted consensus response generation with individual argument logging and confidence scoring
  - Context categorization for decision complexity assessment: simple, complex, ethical, strategic, personal
  - PostgreSQL storage in consensus_logs table with fields: id, timestamp, input_text, virtual_agents, consensus_result, final_decision, confidence_score, primary_contributor, decision_data
  - Comprehensive decision summary with individual agent perspectives and final consensus recommendation
  - Consensus endpoints: POST `/agent/consensus/simulate`, GET `/agent/consensus/logs`, and public endpoints for testing
  - Auto-registration with MasterAgent for intelligent routing using consensus and decision-related keywords
- **AdvancedMemoryManagerAgent**: Centralized memory management system with intelligent classification and cross-agent communication
  - Hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent memory classification
  - Support for 4 memory types: short_term, long_term, mission_specific, reflective with automatic type detection
  - Intelligent importance scoring system (1-10 scale) with context-aware calculation and priority-based retrieval
  - PostgreSQL storage in memory_entries table with fields: id, user_id, agent_name, memory_type, mission_id, content, metadata, importance_score, access_count, created_at, updated_at, expires_at, is_active
  - Memory summaries table with automatic summarization using OpenAI GPT-4o for efficient retrieval and analysis
  - Advanced memory operations: analyze_and_store, retrieve, summarize, purge with comprehensive error handling
  - Memory clustering and context-aware retrieval with performance monitoring and optimization
  - Retention policies and automatic purging with configurable thresholds and dry-run capabilities
  - Memory endpoints: POST `/agent/memory/analyze`, GET `/agent/memory/retrieve/{memory_type}`, GET `/agent/memory/summarize/{memory_type}`, DELETE `/agent/memory/purge/{memory_type}`, GET `/agent/memory/statistics`, and public endpoints for testing
  - Auto-registration with MasterAgent for intelligent routing using memory and storage-related keywords
  - Persian UI integration with comprehensive memory management interface: analyze & store, retrieve, summarize, statistics with tabbed interface

### 7. Frontend UI (`frontend/`)
- **Framework**: Pure HTML/CSS/JavaScript with Tailwind CSS styling
- **Features**: 
  - Real-time messaging with AI agents
  - Short-term memory management interface (show/clear memory)
  - Sentiment analysis tool with TextBlob integration
  - Text summarization with OpenAI GPT-4o and database storage
  - Long-term memory management with categorization and tagging
  - Conceptual memory analysis with OpenAI GPT integration and color-coded display
  - Repetitive pattern analysis with automatic detection and warning system
  - Knowledge graph construction with concept extraction and relationship mapping
  - Auto suggestions with text completion, contextual hints, and smart recommendations
  - Goal and intent detection with hybrid pattern+GPT analysis and structured JSON output
  - Emotion detection and regulation with intensity levels and therapeutic suggestions
  - Multi-dimensional decision support with goal, emotion, memory, and risk analysis
  - Interactive security check with cognitive/emotional threat detection and risk assessment
  - Reward system with positive progress detection and motivational feedback
  - Cognitive bias detection with 7 bias types and reflective suggestions
  - Simulated consensus decision-making with 5 virtual agent perspectives
  - System status monitoring
  - Persian/RTL language support
  - Responsive design with modern UI components
- **API Integration**: Fetch-based communication with FastAPI backend
- **Deployment**: Static files served via FastAPI StaticFiles at `/ui` endpoint

## Data Flow

1. **User Registration**: Email/password → validation → password hashing → database storage
2. **User Login**: Email/password → authentication → JWT token generation → token response
3. **Authenticated Requests**: JWT token → token validation → user identification → protected resource access
4. **Token Refresh**: Refresh token → validation → new access token generation

## External Dependencies

### Core Framework
- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running the application

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib**: Password hashing with BCrypt
- **bcrypt**: Cryptographic hashing algorithm

### Database
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database (via psycopg2 driver)

### Data Validation
- **Pydantic**: Data validation and serialization
- **email-validator**: Email format validation

## Deployment Strategy

The application is designed for containerized deployment:

- **Database**: PostgreSQL instance (local or cloud-hosted)
- **Environment Variables**: Configuration via environment variables
- **CORS**: Pre-configured for common frontend ports (3000, 5000, 8080)
- **Connection Pooling**: Optimized for production workloads
- **Security**: Configurable JWT secrets and password hashing rounds

## Changelog

```
Changelog:
- July 06, 2025. Initial FastAPI authentication system setup
- July 07, 2025. Added AI agents system with MasterAgent and BaseAgent classes
- July 07, 2025. Implemented short-term memory system for agents using deque (last 10 messages)
- July 07, 2025. Created AriaRobot frontend UI with Tailwind CSS and JavaScript
- July 07, 2025. Added UtilityAgent with OpenAI GPT integration for text processing, summarization, and translation
- July 07, 2025. Added ToolAgent with advanced task processing, intelligent task detection, and comprehensive logging capabilities
- July 07, 2025. Added sentiment analysis capability to ToolAgent using TextBlob library with Persian language support
- July 07, 2025. Integrated ToolAgent with UI - added sentiment analysis section with input field, analyze button, and result display
- July 07, 2025. Created SummaryAgent with OpenAI GPT-4o integration for text summarization and PostgreSQL database storage
- July 07, 2025. Added summaries table to database with fields: id, original_text, summary, created_at
- July 07, 2025. Implemented /agent/summary and /agent/summary/public endpoints for SummaryAgent access
- July 07, 2025. Added text summarization UI section with textarea input, "خلاصه کن" button, and comprehensive result display
- July 08, 2025. Created LongTermMemoryAgent with PostgreSQL database integration for persistent memory storage
- July 08, 2025. Added longterm_memories table with fields: id, user_id, content, category, tags, created_at, updated_at
- July 08, 2025. Implemented memory categorization system with 8 categories: هدف، تجربه، درس، یادآوری، احساس، یادداشت، ایده، برنامه
- July 08, 2025. Added /agent/longterm/save and /agent/longterm/fetch endpoints for memory management
- July 08, 2025. Created comprehensive UI for long-term memory with textarea, category selection, tagging, and memory listing
- July 08, 2025. Built ConceptualMemoryAgent with OpenAI GPT-4o integration for intelligent concept extraction
- July 08, 2025. Added conceptual_memories table with fields: id, user_id, raw_text, concept, category, sentiment, created_at
- July 08, 2025. Implemented 8 concept categories and 3-level sentiment analysis with emoji visualization
- July 08, 2025. Added /agent/conceptual/save and /agent/conceptual/latest endpoints for conceptual analysis
- July 08, 2025. Created enhanced UI for conceptual analysis with color-coded category and sentiment display
- July 08, 2025. Built RepetitiveLearningAgent for detecting patterns from repeated concepts and phrases over time
- July 08, 2025. Added repetitive_patterns table with fields: id, user_id, phrase, count, category, last_occurred_at, created_at
- July 08, 2025. Implemented configurable thresholds and warning levels for pattern detection (3/5/10 repetitions)
- July 08, 2025. Added cross-memory analysis capability to detect patterns across all memory types
- July 08, 2025. Added /agent/repetitive/observe and /agent/repetitive/frequent endpoints for pattern management
- July 08, 2025. Created comprehensive UI for repetitive pattern analysis with warning level visualization
- July 08, 2025. Built KnowledgeGraphAgent for extracting concepts, identifying relationships, and building knowledge graphs
- July 08, 2025. Added knowledge_graph table with fields: id, user_id, source_text, concepts, relationships, graph_data, created_at, updated_at
- July 08, 2025. Implemented 7 relationship types and 8 concept types with OpenAI GPT-4o integration
- July 08, 2025. Added fallback concept extraction using rule-based NLP patterns when OpenAI unavailable
- July 08, 2025. Added /agent/knowledge-graph/build and /agent/knowledge-graph/list endpoints for graph management
- July 08, 2025. Created comprehensive UI for knowledge graph construction with textarea, build button, and result display
- July 08, 2025. Built AutoSuggesterAgent for intelligent suggestions and contextual guidance
- July 08, 2025. Added auto_suggestions table with fields: id, user_id, input_text, suggestion, suggestion_type, confidence, context_data, created_at
- July 08, 2025. Implemented 8 suggestion types with OpenAI GPT-4o integration and rule-based fallback
- July 08, 2025. Added memory context analysis including short-term, themes, urgency, and categorization
- July 08, 2025. Added /agent/suggester/complete and /agent/suggester/hints endpoints for suggestion management
- July 08, 2025. Created comprehensive UI for auto suggestions with 3 modes: completion, hints, smart suggestions
- July 08, 2025. Built GoalInferenceAgent for advanced goal and intent detection with hybrid pattern+GPT analysis
- July 08, 2025. Added goal_inferences table with fields: id, user_id, input_text, goal, intent_category, confidence, detected_by, context_data, analysis_details, created_at
- July 08, 2025. Implemented 11 intent categories with pattern-based detection and GPT fallback analysis
- July 08, 2025. Added memory context integration for theme extraction and user pattern recognition
- July 08, 2025. Added structured JSON output format with confidence scoring and detection method tracking
- July 08, 2025. Added POST /agent/goal-inference/analyze endpoint for goal analysis
- July 08, 2025. Created comprehensive UI for goal inference with textarea, analyze button, and formatted JSON display
- July 08, 2025. Built EmotionRegulationAgent for advanced emotion detection and regulation with therapeutic suggestions
- July 08, 2025. Added emotional_states table with fields: id, user_id, input_text, emotion_type, intensity, suggestion, confidence, context_data, created_at
- July 08, 2025. Implemented 13 emotion types with 3-level intensity detection (mild/moderate/intense)
- July 08, 2025. Added personalized regulation suggestions based on emotion type, intensity, and memory context
- July 08, 2025. Added emotional pattern detection for escalating negativity and repeated frustration
- July 08, 2025. Added POST /agent/emotion-regulation/analyze endpoint for emotion analysis
- July 08, 2025. Created comprehensive UI for emotion regulation with textarea, analyze button, and therapeutic suggestion display
- July 08, 2025. Built DecisionSupportAgent for comprehensive multi-dimensional decision analysis
- July 08, 2025. Added decision_support table with fields: id, user_id, decision_text, goal_alignment, emotional_state, risk_level, confidence_score, recommendation, analysis_data, created_at
- July 08, 2025. Implemented multi-dimensional analysis framework integrating GoalInferenceAgent, EmotionRegulationAgent, and LongTermMemoryAgent
- July 08, 2025. Added advanced risk assessment system with pattern-based analysis and GPT-4o integration
- July 08, 2025. Added confidence scoring system and color-coded recommendation engine (green/yellow/red)
- July 08, 2025. Added POST /agent/decision-support/analyze and GET /agent/decision-support/list endpoints
- July 08, 2025. Created comprehensive UI for decision support with textarea, analyze button, decision list, and color-coded results
- July 08, 2025. Integrated DecisionSupportAgent with MasterAgent routing using decision-related keywords
- July 08, 2025. Built SelfAwarenessAgent for advanced self-awareness and mental state analysis
- July 08, 2025. Added self_awareness_logs table with fields: id, user_id, input_text, status, alert, confidence, related_memory, analysis_data, created_at
- July 08, 2025. Implemented hybrid analysis system combining OpenAI GPT-4o integration with pattern-based fallback
- July 08, 2025. Added mental state analysis including self-reflection, metacognitive patterns, and behavioral insights
- July 08, 2025. Added support for 3 status levels (ok/warning/alert) with visual indicators and therapeutic recommendations
- July 08, 2025. Added POST /agent/self-awareness/analyze and GET /agent/self-awareness/logs endpoints
- July 08, 2025. Created comprehensive UI for self-awareness analysis with textarea, analyze button, logs display, and status visualization
- July 08, 2025. Built InteractiveSecurityCheckAgent for advanced cognitive/emotional security threat detection and risk assessment
- July 08, 2025. Added security_checks table with fields: id, input_text, detected_threat_type, alert_level, risk_score, recommendation, analysis_data, created_at
- July 08, 2025. Implemented hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent threat detection
- July 08, 2025. Added support for 8 threat types (burnout, emotional_overload, impulsivity, cognitive_fatigue, stress_overload, decision_paralysis, anxiety_spiral, none)
- July 08, 2025. Added three-level alert system (green/yellow/red) with risk scoring (0.0-1.0) and confidence assessment
- July 08, 2025. Added POST /agent/security-check/analyze and GET /agent/security-check/list endpoints
- July 08, 2025. Created comprehensive UI for security check analysis with textarea, analyze button, previous reports list, and color-coded results
- July 08, 2025. Built RewardAgent for detecting positive progress and providing motivational feedback
- July 08, 2025. Added reward_logs table with fields: id, timestamp, trigger_type, reward_message, emoji, confidence
- July 08, 2025. Implemented hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent reward detection
- July 08, 2025. Added support for 6 trigger types (emotional_recovery, goal_alignment, security_improvement, stress_reduction, positive_mindset, breakthrough, consistency)
- July 08, 2025. Added motivational message generation with emoji visualization and personalized encouragement quotes
- July 08, 2025. Added POST /agent/reward/analyze and GET /agent/reward/logs endpoints
- July 08, 2025. Created comprehensive UI for reward system with textarea, analyze button, reward history list, and colorful reward display
- July 08, 2025. Successfully completed comprehensive 15-agent system with full MasterAgent integration and Persian UI support
- July 08, 2025. Built BiasDetectionAgent for advanced cognitive bias detection and reflection with 7 bias types
- July 08, 2025. Added bias_logs table with fields: id, timestamp, input_text, bias_type (array), severity_score, suggestion
- July 08, 2025. Implemented hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent bias detection
- July 08, 2025. Added support for 7 cognitive bias types: Confirmation Bias, Availability Bias, Overconfidence, Anchoring, Sunk Cost Fallacy, Negativity Bias, Framing Effect
- July 08, 2025. Added severity scoring (0.0-1.0) and confidence assessment with personalized reflective suggestions
- July 08, 2025. Added POST /agent/bias/analyze, GET /agent/bias/logs, and public endpoints for bias analysis
- July 08, 2025. Created comprehensive UI for bias detection analysis with "🧠 سوگیری" section, analyze button, and history display
- July 08, 2025. Successfully completed comprehensive 16-agent system with BiasDetectionAgent integration and Persian UI support
- July 09, 2025. Built SimulatedConsensusAgent for collaborative decision-making simulation with 5 virtual agent perspectives
- July 09, 2025. Added consensus_logs table with fields: id, timestamp, input_text, virtual_agents, consensus_result, final_decision, confidence_score, primary_contributor, decision_data
- July 09, 2025. Implemented hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent consensus building
- July 09, 2025. Added support for 5 virtual agent perspectives: Conservative Analyst, Creative Thinker, Practical Problem Solver, Ethical Evaluator, Balanced Mediator
- July 09, 2025. Added weighted consensus response generation with individual argument logging and confidence scoring
- July 09, 2025. Added POST /agent/consensus/simulate, GET /agent/consensus/logs, and public endpoints for consensus analysis
- July 09, 2025. Created comprehensive UI for consensus simulation with "🤝 تصمیم‌گیری گروهی" button and interface
- July 09, 2025. Successfully completed comprehensive 17-agent system with SimulatedConsensusAgent integration and Persian UI support
- July 09, 2025. Built AdvancedMemoryManagerAgent for centralized memory management across all agents with intelligent classification
- July 09, 2025. Added memory_entries table with fields: id, user_id, agent_name, memory_type, mission_id, content, metadata, importance_score, access_count, created_at, updated_at, expires_at, is_active
- July 09, 2025. Added memory_summaries table with automatic summarization using OpenAI GPT-4o for efficient retrieval and analysis
- July 09, 2025. Implemented hybrid analysis system combining pattern recognition with OpenAI GPT-4o integration for intelligent memory classification
- July 09, 2025. Added support for 4 memory types: short_term, long_term, mission_specific, reflective with automatic type detection
- July 09, 2025. Added intelligent importance scoring system (1-10 scale) with context-aware calculation and priority-based retrieval
- July 09, 2025. Added memory clustering and context-aware retrieval with performance monitoring and optimization capabilities
- July 09, 2025. Added retention policies and automatic purging with configurable thresholds and dry-run capabilities
- July 09, 2025. Added POST /agent/memory/analyze, GET /agent/memory/retrieve/{memory_type}, GET /agent/memory/summarize/{memory_type}, DELETE /agent/memory/purge/{memory_type}, GET /agent/memory/statistics, and public endpoints
- July 09, 2025. Created comprehensive Persian UI for memory management with tabbed interface: analyze & store, retrieve, summarize, statistics with "🧠 مدیر حافظه" button
- July 09, 2025. Successfully completed comprehensive 18-agent system with AdvancedMemoryManagerAgent integration and Persian UI support
- July 13, 2025. **MAJOR ARCHITECTURAL TRANSFORMATION**: Converted entire monolithic agent system to modular SuperAGI architecture
- July 13, 2025. Created `superagi/agents/aria_agents/` directory structure with 20 modular agent folders
- July 13, 2025. Implemented base_agent.py template following SuperAGI standards with enhanced configuration support
- July 13, 2025. Created individual agent modules: AriaMasterAgent, AriaUtilityAgent, AriaToolAgent, AriaSummaryAgent, AriaMemoryAgent, AriaConceptualAgent, AriaRepetitiveAgent, AriaKnowledgeAgent, AriaSuggesterAgent, AriaGoalAgent, AriaEmotionAgent, AriaDecisionAgent, AriaAwarenessAgent, AriaSecurityAgent, AriaRewardAgent, AriaBiasAgent, AriaDistortionAgent, AriaEthicalAgent, AriaConsensusAgent, AriaAdvancedMemoryAgent
- July 13, 2025. Each agent now includes: __init__.py, agent_config.yaml with comprehensive metadata, and standalone agent class file
- July 13, 2025. Updated all agent configurations with: capabilities, routing keywords, dependencies, runtime settings, OpenAI configuration, database schema, logging, and integration settings
- July 13, 2025. Maintained backward compatibility while enabling modular deployment and independent scaling
- July 13, 2025. Enhanced error handling and fallback mechanisms across all agents
- July 13, 2025. Implemented YAML-based configuration system for all agents with validation and defaults
- July 13, 2025. Created centralized agent registration system with automatic discovery and initialization
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
Agent responses: Persian language preferred for AI agents.
Memory system: Short-term memory with deque, independent per agent.
```

## Architecture Decisions

### JWT vs Session-Based Authentication
- **Chosen**: JWT tokens with refresh token pattern
- **Rationale**: Stateless authentication, better scalability, mobile-friendly
- **Trade-offs**: Slightly more complex token management vs simpler session invalidation

### PostgreSQL Database Choice
- **Chosen**: PostgreSQL with SQLAlchemy ORM
- **Rationale**: ACID compliance, strong typing, excellent SQLAlchemy support
- **Alternatives**: MySQL, SQLite considered but PostgreSQL chosen for production readiness

### Password Security
- **Chosen**: BCrypt with 12 rounds
- **Rationale**: Industry standard, configurable work factor, resistance to rainbow table attacks
- **Security**: Strong password requirements enforced at validation layer

### Token Expiry Strategy
- **Chosen**: 30-minute access tokens, 7-day refresh tokens
- **Rationale**: Balance between security (short-lived access) and user experience (longer refresh)
- **Implementation**: Separate token types with different expiry times