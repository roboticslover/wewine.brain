import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WeWine.app Strategic AI Co-Founder",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENHANCED CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

    /* --- General Styles --- */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #722F37 0%, #B8860B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-subheader {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #B8860B;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* --- AI Response Box --- */
    .ai-response {
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #B8860B;
        border-radius: 15px;
        padding: 1.5rem 2rem;
        margin-top: 1.5rem;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        color: #EAEAEA;
        box-shadow: 0 4px 12px rgba(184, 134, 11, 0.3);
    }
    .ai-response h1, .ai-response h2, .ai-response h3 {
        font-family: 'Playfair Display', serif;
        color: #FFFFFF;
        border-bottom: 1px solid #B8860B;
        padding-bottom: 8px;
        margin-top: 1.5rem;
    }
    .ai-response strong {
        color: #DAA520;
    }

    /* --- Status Indicators --- */
    .status-connected {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .cost-tracker {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }

    /* --- Buttons --- */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid #B8860B;
        color: #B8860B;
        background-color: transparent;
        transition: all 0.3s ease-in-out;
        font-weight: 600;
    }
    .stButton>button:hover {
        border-color: #FFFFFF;
        color: #FFFFFF;
        background-color: #B8860B;
        transform: translateY(-2px);
    }

    /* --- Feature Cards --- */
    .feature-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid #B8860B;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(184, 134, 11, 0.3);
    }

    /* --- Agent Cards --- */
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #B8860B;
        color: #000000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'api_usage_cost' not in st.session_state:
    st.session_state.api_usage_cost = 0.0
if 'api_calls_count' not in st.session_state:
    st.session_state.api_calls_count = 0
if 'daily_reset' not in st.session_state:
    st.session_state.daily_reset = datetime.now().date()

# Reset daily usage
if st.session_state.daily_reset != datetime.now().date():
    st.session_state.api_usage_cost = 0.0
    st.session_state.api_calls_count = 0
    st.session_state.daily_reset = datetime.now().date()

# --- COST TRACKING ---
def estimate_cost(prompt_tokens, completion_tokens, model):
    """Estimate API cost based on token usage"""
    pricing = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'o1-preview': {'input': 0.015, 'output': 0.06},
        'o1-mini': {'input': 0.003, 'output': 0.012}
    }
    
    if model not in pricing:
        model = 'gpt-4'  # default
    
    input_cost = (prompt_tokens / 1000) * pricing[model]['input']
    output_cost = (completion_tokens / 1000) * pricing[model]['output']
    
    return input_cost + output_cost

def check_cost_limit():
    """Check if we're approaching cost limit"""
    return st.session_state.api_usage_cost < 1.0

# --- AI CEO CORE CLASS ---
class WeWineStrategicAICEO:
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.api_available = self.api_key is not None
        
        self.company_context = """
        COMPANY PROFILE: WeWine.app
        
        MISSION: To become the essential companion for the modern wine journey, blending AI technology, 
        community, and authentic experiences. We are not just an app; we are a cultural movement that 
        democratizes wine knowledge and creates joyful discovery experiences.
        
        CORE VALUE PROPOSITION: WeWine replaces wine anxiety with confident exploration. We empower users 
        to discover wines they love through AI-powered personalization, connect with a vibrant community, 
        and access unique wine experiences both online and offline.
        
        TARGET AUDIENCE:
        - Primary: "Curious Enthusiasts" (25-45) - Digitally native, value authenticity, eager to learn 
          but intimidated by traditional wine snobbery. They want guidance without judgment.
        - Secondary: Boutique Wineries & Local Wine Merchants - Need direct channels to reach engaged 
          consumers and tell their authentic stories.
        
        DIFFERENTIATORS (OUR MOAT):
        1. **Hyper-Personalized Journey AI:** Goes beyond taste profiles to understand context, mood, 
           occasions, and learning goals. Evolves with user's palate development.
        2. **Community-Powered Discovery:** Stories and experiences drive recommendations. Friend and 
           community trust beats algorithms alone.
        3. **Experience-First Model:** Seamless online-to-offline integration with tastings, vineyard 
           tours, educational sessions, and local events.
        4. **Lisbon-Born, Global-Minded:** Authentic European wine culture foundation with global scalability.
        
        CURRENT METRICS:
        - Monthly Users: 15,000 (growing 12% monthly)
        - Conversion Rate: 3.2% (target: 5%)
        - Customer LTV: $180
        - Customer CAC: $25.30
        - Monthly Revenue: $42,500
        - App Rating: 4.4/5
        - Markets: 5 countries
        """
        
        self.system_prompt = """
        You are "Aura," the Strategic AI Co-Founder of WeWine.app. Your persona blends:
        - Seasoned venture-backed CEO with exits
        - Master sommelier with deep wine knowledge  
        - Brilliant product strategist with user obsession
        - Growth expert with proven scaling experience
        
        GUIDING PRINCIPLES:
        1. **Founder's Mentality:** Think ROI, growth levers, user LTV, sustainable competitive advantage. 
           Every recommendation must be actionable with clear success metrics.
        2. **User-Obsessed:** Frame decisions around removing friction and creating "wow" moments for 
           "Curious Enthusiasts." Use behavioral psychology and UX best practices.
        3. **Framework-Driven:** Structure analysis using OKRs, RICE scoring, AARRR metrics, Jobs-to-be-Done, 
           and proven Go-To-Market strategies.
        4. **Brand Voice:** Sophisticated yet accessible. Expert authority with mentor warmth. Avoid jargon.
        5. **Strategic Depth:** Connect tactical recommendations to long-term strategic advantages and moat-building.
        
        OUTPUT FORMAT: Use clear Markdown with executive summaries, headers, bullet points. Start responses 
        with 2-3 sentence strategic overview, then detailed analysis with specific action items and success metrics.
        """

    def _call_openai_api(self, user_prompt: str, system_override: str = None) -> str:
        """Enhanced API call with cost tracking and error handling"""
        if not self.api_available:
            return self._generate_fallback_response(user_prompt)
        
        if not check_cost_limit():
            return "💰 **Daily cost limit reached ($1.00).** Using offline insights. Upgrade or wait for daily reset."
        
        try:
            system_content = system_override or self.system_prompt
            
            # Estimate tokens (rough approximation)
            prompt_length = len(system_content) + len(user_prompt) + len(self.company_context)
            estimated_prompt_tokens = prompt_length // 4  # rough estimate
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": f"{self.company_context}\n\nUSER PROMPT:\n{user_prompt}"}
                    ],
                    "max_tokens": 2500 if self.model.startswith('o1') else 3000,
                    "temperature": 0.7 if not self.model.startswith('o1') else None
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Track usage
            if 'usage' in result:
                usage = result['usage']
                cost = estimate_cost(usage['prompt_tokens'], usage['completion_tokens'], self.model)
                st.session_state.api_usage_cost += cost
                st.session_state.api_calls_count += 1
            
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as http_err:
            error_details = response.json().get('error', {}).get('message', 'No details provided.')
            return f"❌ **API Error:** {http_err}\n\n*Details:* {error_details}\n\nFalling back to offline analysis..."
        except Exception as e:
            return f"❌ **Connection Error:** {str(e)}\n\nUsing offline strategic framework..."

    def _generate_fallback_response(self, user_prompt: str) -> str:
        """Generate intelligent offline responses using business frameworks"""
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['market', 'competitor', 'competitive']):
            return self._market_analysis_framework()
        elif any(word in prompt_lower for word in ['growth', 'scaling', 'user']):
            return self._growth_strategy_framework()
        elif any(word in prompt_lower for word in ['product', 'feature', 'roadmap']):
            return self._product_strategy_framework()
        elif any(word in prompt_lower for word in ['gtm', 'go-to-market', 'launch']):
            return self._gtm_framework()
        else:
            return self._general_strategic_framework()

    def _market_analysis_framework(self) -> str:
        return """
## 🎯 **Strategic Market Analysis**

### **Executive Summary**
WeWine operates in a $350B+ global wine market with growing digital disruption. Key opportunity: 
Millennials represent 42% of wine consumption but are underserved by existing platforms.

### **Competitive Landscape Analysis**

**🏆 Market Leaders:**
- **Vivino**: 70M users, $224M funding - *Database approach, overwhelming for beginners*
- **Delectable**: 2M users, sommelier-focused - *Expert credibility but intimidating*
- **Firstleaf**: AI-driven, subscription model - *Limited flexibility, US-only*

**💡 WeWine's Strategic Positioning:**
*"The Anti-Vivino: Curated Discovery Over Information Overload"*

### **Key Strategic Moves**

1. **Blue Ocean Strategy**: Target the "Anxious Explorer" segment
   - Focus on confidence-building vs. expertise display
   - Simplicity over comprehensiveness

2. **Community-First Differentiation**:
   - Build trust through peer recommendations
   - Create "Wine Discovery Circles"

3. **Experience Integration**:
   - Online-to-offline event programming
   - Local wine bar partnerships

### **Success Metrics**
- User confidence score (NPS for wine anxiety reduction)
- Community engagement rate (>40% monthly active discussion)
- Experience participation rate (>15% attend events)

**Next Steps:** Focus Q1 on community features, Q2 on local partnerships.
        """

    def _growth_strategy_framework(self) -> str:
        return """
## 📈 **Growth Strategy Framework**

### **Executive Summary**
WeWine's path to 100K users requires a three-phase approach: Community-Led Growth → 
Viral Loops → Scaled Acquisition. Current metrics show strong product-market fit signals.

### **Phase 1: Community-Led Growth (0-25K users)**

**🎯 Core Strategy**: Turn early users into brand evangelists

**Key Initiatives:**
1. **Wine Discovery Challenges**
   - Monthly themed challenges (e.g., "Italian Adventure")
   - User-generated content with rewards
   - Community voting and curation

2. **Local Wine Ambassadors Program**
   - 10 power users per city become ambassadors
   - Exclusive events and early access
   - Referral rewards and recognition

3. **Strategic Partnerships**
   - Boutique wine shops for exclusive offerings
   - Local restaurants for pairing events
   - Wine education platforms for content

### **Phase 2: Viral Mechanics (25K-75K users)**

**🚀 Viral Loops:**
- **Social Sharing**: Beautiful wine journey visualizations
- **Gift Recommendations**: "Send a bottle" feature
- **Group Discoveries**: Friends can explore together

### **Phase 3: Scaled Acquisition (75K-100K users)**

**📊 Paid Channels:**
- Instagram/TikTok targeted at "wine curious" demographics
- Google Ads for high-intent searches
- Influencer partnerships with lifestyle creators

### **Success Metrics & Timeline**
- **Month 1-3**: 15K → 25K users (67% growth)
- **Month 4-6**: 25K → 50K users (viral coefficient 1.2)
- **Month 7-12**: 50K → 100K users (100% growth)

**Investment Required**: $150K for 12-month execution
        """

    def _product_strategy_framework(self) -> str:
        return """
## 🛠️ **Product Strategy Framework**

### **Executive Summary**
WeWine's product roadmap should focus on three pillars: AI Personalization Engine, 
Community Features, and Experience Integration. RICE framework guides prioritization.

### **Q1 2024: Foundation & Community (Theme: "Building Trust")**

| Feature | Description | Reach | Impact | Confidence | Effort | RICE Score |
|---------|-------------|-------|--------|------------|--------|------------|
| **Taste Journey AI** | Advanced preference learning | 9 | 9 | 85% | 2.0 | 34.5 |
| **Wine Discovery Feed** | Community-driven recommendations | 8 | 8 | 90% | 1.5 | 38.4 |
| **Local Availability** | Real-time inventory integration | 7 | 9 | 70% | 3.0 | 14.7 |
| **Social Sharing** | Beautiful wine story cards | 6 | 7 | 95% | 1.0 | 39.9 |

### **Q2 2024: Engagement & Retention (Theme: "Magical Moments")**

**Priority Features:**
1. **Wine Discovery Challenges** - Gamified learning experiences
2. **AR Label Scanner** - Instant wine information and reviews
3. **Personalized Events** - AI-recommended local tastings
4. **Gift Recommendations** - Occasion-based suggestions

### **Q3-Q4 2024: Scale & Monetization (Theme: "Sustainable Growth")**

**Advanced Features:**
- **Cellar Management** - Track personal wine collection
- **Advanced Analytics** - Taste evolution insights
- **Premium Subscriptions** - Expert access and exclusive content
- **Marketplace Integration** - Seamless purchasing experience

### **Success Metrics**
- **User Engagement**: 40% weekly active users
- **Feature Adoption**: >60% for core features within 30 days
- **Retention**: 35% monthly cohort retention by month 6
- **Revenue**: $2 ARPU monthly by Q4

**Technical Requirements**: React Native app, Node.js backend, ML pipeline for recommendations
        """

    def _gtm_framework(self) -> str:
        return """
## 🚀 **Go-To-Market Strategy Framework**

### **Executive Summary**
WeWine's GTM strategy leverages Lisbon as a beachhead market, then expands to select European 
cities using a community-first, experience-driven approach.

### **Phase 1: Lisbon Domination (Months 1-6)**

**🎯 Objective**: Become the #1 wine discovery app in Lisbon with 5,000 active users

**Core Tactics:**
1. **Hyper-Local Wine Tours**
   - Partner with 10 premium wine bars in Príncipe Real/Chiado
   - Weekly "WeWine Wednesday" events
   - Exclusive tastings for app users

2. **Sommelier Partnership Program**
   - Recruit 15 local wine experts as content creators
   - Monthly "Expert Picks" features
   - Live Q&A sessions in-app

3. **Tourist Integration**
   - Partner with premium hotels (Tivoli, Memmo Alfama)
   - "Lisbon Wine Guide" feature for visitors
   - Airport/tourism board partnerships

### **Phase 2: European Expansion (Months 7-18)**

**🌍 Target Cities**: Barcelona, Milan, Copenhagen, Amsterdam

**Expansion Playbook:**
- Hire local "Wine Community Managers"
- Replicate Lisbon partnership model
- Cross-market user acquisition campaigns

### **Phase 3: Global Platform (Months 19-36)**

**🚀 Scale Strategy:**
- API partnerships with wine retailers
- White-label solutions for wine regions
- Enterprise partnerships with hospitality

### **Success Metrics & Investment**

**Key KPIs:**
- **Market Penetration**: 2% of target demographic per city
- **Event Attendance**: 500+ monthly event participants
- **Partnership Revenue**: 30% of total revenue by month 18

**Investment Required:**
- **Phase 1**: €75K (events, partnerships, local team)
- **Phase 2**: €300K (expansion, marketing, tech)
- **Phase 3**: €1M+ (scaling, enterprise partnerships)

### **Risk Mitigation**
- Local competitor response → Strong community moats
- Economic downturn → Focus on free community features
- Partnership dependency → Diversified revenue streams
        """

    def _general_strategic_framework(self) -> str:
        return """
## 🎯 **Strategic Business Framework**

### **Executive Summary**
WeWine.app sits at the intersection of three growing trends: AI personalization, community commerce, 
and experience economy. Our strategic advantage lies in combining all three effectively.

### **Strategic Pillars**

#### **1. AI-Powered Personalization**
- Move beyond basic taste profiles to contextual recommendations
- Understand user's wine journey and goals
- Predict preferences based on mood, occasion, season

#### **2. Community-Driven Discovery**
- Trust-based recommendations over algorithmic ones
- Social proof and peer validation
- User-generated content and stories

#### **3. Experience Integration**
- Bridge online discovery with offline experiences
- Create memorable moments that build brand loyalty
- Generate multiple revenue streams

### **Business Model Innovation**

**Current**: Marketplace + commission model
**Evolution**: Platform + subscription + experiences + data

**Revenue Streams:**
1. **Transaction fees** (current): 10-15% commission
2. **Premium subscriptions**: $9.99/month for advanced features
3. **Experience bookings**: 20% commission on events
4. **Data insights**: B2B analytics for wineries

### **Competitive Moats**

1. **Data Network Effects**: More users = better recommendations
2. **Community Lock-in**: Social connections create switching costs
3. **Experience Infrastructure**: Physical partnerships hard to replicate
4. **Brand Trust**: Authentic, approachable wine discovery

### **Strategic Priorities**

**Near-term (0-6 months):**
- Strengthen core AI recommendation engine
- Build vibrant community features
- Establish local partnership network

**Medium-term (6-18 months):**
- Scale to 3-5 key markets
- Launch premium subscription tiers
- Develop experience marketplace

**Long-term (18+ months):**
- International expansion
- Enterprise partnerships
- Adjacent market opportunities

### **Success Framework**
- **Product-Market Fit**: NPS >50, retention >30%
- **Business Model**: Unit economics positive by month 18
- **Market Position**: Top 3 in each target market
        """

    # Enhanced Analysis Methods
    def generate_competitive_analysis(self, competitor: str = None):
        if competitor:
            prompt = f"""
            Conduct a comprehensive "David vs. Goliath" competitive analysis of WeWine.app against {competitor}.
            
            Focus on:
            1. Strategic positioning opportunities where we can win
            2. Specific product features that exploit their weaknesses
            3. Marketing strategies that turn their size into a disadvantage
            4. Partnership opportunities they're likely missing
            5. Actionable competitive moves for the next 90 days
            
            Provide concrete examples and specific tactics we can implement immediately.
            """
        else:
            prompt = """
            Analyze the entire competitive landscape for WeWine.app. Identify:
            1. Market gaps and white space opportunities
            2. Competitive threats and how to counter them
            3. Strategic partnerships we should pursue
            4. Positioning strategy that differentiates us
            5. Specific competitive advantages we can build
            
            Focus on actionable insights that drive growth and defend market position.
            """
        
        return self._call_openai_api(prompt)

    def generate_growth_strategy(self, focus_area: str = "user_acquisition"):
        prompt = f"""
        Develop a comprehensive growth strategy for WeWine.app focused on: {focus_area}
        
        Provide a detailed strategy including:
        1. Specific growth tactics and experiments to run
        2. 30-60-90 day milestone roadmap with measurable goals
        3. Resource requirements and budget allocation
        4. Success metrics and KPIs to track
        5. Risk assessment and contingency plans
        6. Competitive positioning during growth phase
        7. Implementation priorities and quick wins
        
        Make recommendations specific, measurable, and implementable with current resources.
        """
        
        return self._call_openai_api(prompt)

    def generate_product_roadmap(self, timeframe: str = "90_days"):
        prompt = f"""
        Create a prioritized {timeframe} product roadmap for WeWine.app using the RICE scoring framework.
        
        Requirements:
        1. Theme for the period with clear strategic focus
        2. 5-7 prioritized features with RICE scores (Reach, Impact, Confidence, Effort)
        3. Detailed feature descriptions with user value propositions
        4. Technical requirements and dependencies
        5. Success metrics for each feature
        6. Resource allocation and team assignments
        7. Risk mitigation for high-impact features
        
        Focus on features that maximize user engagement, retention, and business growth.
        """
        
        return self._call_openai_api(prompt)

    def multi_agent_analysis(self, query: str):
        system_role = """
        You are a team of specialized AI business experts for WeWine.app. Respond as multiple agents collaborating:
        
        🎯 **CEO Agent**: Strategic oversight, synthesis, final recommendations
        📊 **Market Research Agent**: Competitive analysis, market sizing, trends
        📈 **Growth Agent**: User acquisition, retention, viral strategies  
        🛠️ **Product Agent**: Feature prioritization, UX/UI, technical roadmap
        💰 **CFO Agent**: Financial modeling, unit economics, fundraising
        🎨 **Brand Agent**: Positioning, messaging, community building
        
        Each agent provides their specialized perspective, then CEO synthesizes into actionable strategy.
        """
        
        prompt = f"""
        Multi-agent strategic analysis for WeWine.app: {query}
        
        Each agent should provide their expertise perspective on this question, followed by a CEO synthesis 
        with specific action items, success metrics, and implementation timeline.
        """
        
        return self._call_openai_api(prompt, system_role)

# --- SIDEBAR CONFIGURATION ---
def setup_sidebar():
    with st.sidebar:
        st.markdown('<h2 style="color: #B8860B;">🍷 AI CEO Control Panel</h2>', unsafe_allow_html=True)
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        
        # Check for .env API key
        env_api_key = os.getenv('OPENAI_API_KEY')
        
        if env_api_key:
            st.success("✅ API Key loaded from .env")
            use_env_key = st.checkbox("Use .env API key", value=True)
            
            if use_env_key:
                api_key = env_api_key
                manual_key = None
            else:
                manual_key = st.text_input("Enter your OpenAI API Key:", type="password")
                api_key = manual_key if manual_key else env_api_key
        else:
            st.warning("⚠️ No API key in .env file")
            manual_key = st.text_input("Enter your OpenAI API Key:", type="password", 
                                     help="Get your API key from https://platform.openai.com/")
            api_key = manual_key
        
        # Model Selection
        st.subheader("🧠 AI Model Selection")
        
        model_options = {
            "GPT-4": "gpt-4",
            "GPT-4 Turbo": "gpt-4-turbo-preview", 
            "GPT-3.5 Turbo": "gpt-3.5-turbo",
            "O1-Preview (Reasoning)": "o1-preview",
            "O1-Mini (Fast Reasoning)": "o1-mini"
        }
        
        selected_model_name = st.selectbox(
            "Choose AI Model:",
            list(model_options.keys()),
            index=0,
            help="O1 models are best for complex reasoning, GPT-4 for balanced performance"
        )
        
        selected_model = model_options[selected_model_name]
        
        # Cost Tracking
        st.subheader("💰 Cost Management")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Daily Usage", f"${st.session_state.api_usage_cost:.3f}")
        with col2:
            st.metric("API Calls", st.session_state.api_calls_count)
        
        # Progress bar for cost limit
        cost_percentage = min(st.session_state.api_usage_cost / 1.0, 1.0)
        st.progress(cost_percentage)
        
        if cost_percentage > 0.8:
            st.warning("⚠️ Approaching daily limit ($1.00)")
        elif cost_percentage >= 1.0:
            st.error("🚫 Daily limit reached")
        else:
            st.info(f"💚 ${1.0 - st.session_state.api_usage_cost:.3f} remaining")
        
        # System Status
        st.subheader("📊 System Status")
        
        if api_key:
            st.markdown('<div class="status-connected">🟢 AI CEO Online</div>', unsafe_allow_html=True)
            st.write(f"**Model:** {selected_model_name}")
        else:
            st.markdown('<div class="status-offline">🔴 AI CEO Offline</div>', unsafe_allow_html=True)
            st.write("**Mode:** Offline Framework Analysis")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Reset Daily Usage", help="Reset API usage counter"):
            st.session_state.api_usage_cost = 0.0
            st.session_state.api_calls_count = 0
            st.success("✅ Usage reset!")
            st.experimental_rerun()
        
        # Business Metrics
        st.subheader("📈 WeWine Metrics")
        
        metrics = {
            "Monthly Users": "15,000",
            "Monthly Revenue": "$42,500", 
            "Conversion Rate": "3.2%",
            "App Rating": "4.4⭐"
        }
        
        for metric, value in metrics.items():
            st.metric(metric, value)
        
        return api_key, selected_model

# --- MAIN APPLICATION COMPONENTS ---
def ai_ceo_dashboard(ai_ceo):
    st.markdown('<h1 class="main-header">🍷 WeWine.app Strategic AI Co-Founder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subheader">Your AI-powered business strategy partner for wine-tech success</p>', unsafe_allow_html=True)
    
    # Agent Overview
    st.subheader("🤖 AI Advisory Team")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="agent-card">🎯 CEO Agent<br>Strategic Leadership</div>', unsafe_allow_html=True)
        st.markdown('<div class="agent-card">📊 Market Research<br>Competitive Intelligence</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="agent-card">📈 Growth Agent<br>User Acquisition</div>', unsafe_allow_html=True)
        st.markdown('<div class="agent-card">🛠️ Product Agent<br>Feature Strategy</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="agent-card">💰 CFO Agent<br>Financial Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="agent-card">🎨 Brand Agent<br>Market Positioning</div>', unsafe_allow_html=True)

def strategic_analysis_tab(ai_ceo):
    st.header("🎯 Strategic Business Analysis")
    
    # Quick Analysis Buttons
    st.subheader("🚀 Quick Strategic Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 Competitive Analysis", use_container_width=True):
            with st.spinner("🤖 Analyzing competitive landscape..."):
                response = ai_ceo.generate_competitive_analysis()
                st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    with col2:
        growth_focus = st.selectbox("Growth Focus", 
                                   ["user_acquisition", "retention", "monetization", 
                                    "market_expansion", "product_growth"])
        
        if st.button("📈 Growth Strategy", use_container_width=True):
            with st.spinner(f"📈 Developing {growth_focus} strategy..."):
                response = ai_ceo.generate_growth_strategy(growth_focus)
                st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    with col3:
        roadmap_period = st.selectbox("Roadmap Period", 
                                     ["90_days", "6_months", "1_year"])
        
        if st.button("🛠️ Product Roadmap", use_container_width=True):
            with st.spinner(f"🛠️ Creating {roadmap_period} roadmap..."):
                response = ai_ceo.generate_product_roadmap(roadmap_period)
                st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Custom Strategic Query
    st.subheader("💬 Strategic Consultation")
    
    query_examples = [
        "How can WeWine achieve 100K users in 12 months?",
        "What's our best strategy against Vivino's dominance?",
        "How should we price our premium subscription?",
        "What partnerships should we prioritize for growth?",
        "How can we improve our conversion rate from 3.2% to 5%?"
    ]
    
    example_query = st.selectbox("Example Questions:", ["Custom Question"] + query_examples)
    
    if example_query != "Custom Question":
        custom_query = example_query
    else:
        custom_query = st.text_area(
            "Ask your AI CEO team:",
            placeholder="e.g., How can WeWine differentiate from competitors while scaling to 100K users?",
            height=100
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧠 Single Agent Analysis", type="primary") and custom_query:
            with st.spinner("🧠 AI CEO analyzing..."):
                response = ai_ceo._call_openai_api(custom_query)
                st.markdown(f'<div class="ai-response"><h4>🧠 AI CEO Response</h4>{response}</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("👥 Multi-Agent Analysis", type="primary") and custom_query:
            with st.spinner("👥 Multi-agent team collaborating..."):
                response = ai_ceo.multi_agent_analysis(custom_query)
                st.markdown(f'<div class="ai-response"><h4>👥 Multi-Agent Analysis</h4>{response}</div>', unsafe_allow_html=True)

def competitor_analysis_tab(ai_ceo):
    st.header("🏆 Competitive Intelligence")
    
    # Competitor Database
    competitors = {
        "Vivino": {"users": "70M+", "funding": "$224M", "strength": "Massive community", "weakness": "Information overload"},
        "Delectable": {"users": "2M+", "funding": "$15M+", "strength": "Expert curation", "weakness": "Intimidating for beginners"},
        "Firstleaf": {"users": "1M+", "funding": "$27.6M", "strength": "AI accuracy", "weakness": "US-only, subscription lock-in"},
        "Wine-Searcher": {"users": "5M+", "funding": "Private", "strength": "Price data", "weakness": "Complex interface"},
        "Nakedwines": {"users": "964K", "funding": "$10M", "strength": "Unique model", "weakness": "Limited selection"}
    }
    
    # Competitor Overview
    st.subheader("📊 Competitive Landscape")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Competitors", "20+")
    with col2:
        st.metric("Market Leaders", "5")
    with col3:
        st.metric("Total Funding", "$350M+")
    with col4:
        st.metric("Combined Users", "85M+")
    
    # Competitor Analysis
    st.subheader("🎯 Deep Dive Analysis")
    
    selected_competitor = st.selectbox(
        "Select Competitor for Analysis:",
        list(competitors.keys()),
        format_func=lambda x: f"{x} - {competitors[x]['users']} users"
    )
    
    if selected_competitor:
        comp_data = competitors[selected_competitor]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**👥 Users:** {comp_data['users']}")
            st.write(f"**💰 Funding:** {comp_data['funding']}")
            st.write(f"**💪 Strength:** {comp_data['strength']}")
            st.write(f"**⚠️ Weakness:** {comp_data['weakness']}")
        
        with col2:
            if st.button(f"🔍 Analyze {selected_competitor}", use_container_width=True):
                with st.spinner(f"🔍 Deep-diving into {selected_competitor}..."):
                    analysis = ai_ceo.generate_competitive_analysis(selected_competitor)
                    st.markdown(f'<div class="ai-response"><h4>🔍 {selected_competitor} Analysis</h4>{analysis}</div>', unsafe_allow_html=True)
    
    # Market Positioning
    st.subheader("📈 Market Positioning Strategy")
    
    positioning_questions = [
        "How should WeWine position against market leaders?",
        "What's our unique value proposition vs. Vivino?", 
        "Which competitor should we target first?",
        "What partnerships can counter competitor advantages?"
    ]
    
    selected_question = st.selectbox("Strategic Question:", positioning_questions)
    
    if st.button("💡 Get Positioning Strategy"):
        with st.spinner("💡 Developing positioning strategy..."):
            response = ai_ceo._call_openai_api(selected_question)
            st.markdown(f'<div class="ai-response"><h4>💡 Positioning Strategy</h4>{response}</div>', unsafe_allow_html=True)

def business_metrics_tab():
    st.header("📊 Business Intelligence Dashboard")
    
    # Key Metrics
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Users", "15,000", "+12%")
    with col2:
        st.metric("Monthly Revenue", "$42,500", "+8%") 
    with col3:
        st.metric("Conversion Rate", "3.2%", "+0.3%")
    with col4:
        st.metric("LTV:CAC", "7.1:1", "+0.5")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trend
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        revenue = [35000, 37000, 39000, 41000, 38000, 42500]
        
        fig = px.line(x=months, y=revenue, title="📈 Revenue Growth Trend")
        fig.update_traces(line=dict(color='#B8860B', width=3))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # User acquisition
        users = [8000, 9200, 10500, 11800, 13200, 15000]
        
        fig = px.bar(x=months, y=users, title="👥 User Growth")
        fig.update_traces(marker_color='#722F37')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Business Health
    st.subheader("💊 Business Health Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        st.write("• Strong user growth (+12% monthly)")
        st.write("• Healthy LTV:CAC ratio (7.1:1)")
        st.write("• Good app rating (4.4/5)")
        st.write("• Growing revenue (+8% monthly)")
    
    with col2:
        st.markdown("### 🎯 Improvement Areas")
        st.write("• Conversion rate below target (3.2% vs 5%)")
        st.write("• Need to reduce customer acquisition cost")
        st.write("• Increase average order value") 
        st.write("• Improve retention rates")

def feature_showcase_tab():
    st.header("✨ AI CEO Capabilities")
    
    # Feature Categories
    features = {
        "🎯 Strategic Analysis": [
            "Market positioning and competitive analysis",
            "Growth strategy development with actionable tactics",
            "Product roadmap prioritization using RICE framework",
            "Go-to-market strategy for new markets"
        ],
        "🧠 Multi-Agent Intelligence": [
            "CEO, Growth, Product, CFO, and Brand agent perspectives",
            "Collaborative analysis with synthesized recommendations",
            "Specialized expertise for complex business questions",
            "Diverse viewpoints for comprehensive strategy"
        ],
        "📊 Business Intelligence": [
            "Competitive landscape monitoring",
            "Market opportunity identification", 
            "Financial modeling and unit economics",
            "Performance metrics analysis"
        ],
        "💡 Innovation & Planning": [
            "Feature ideation and prioritization",
            "Partnership strategy development",
            "Fundraising preparation and planning",
            "Crisis management and contingency planning"
        ]
    }
    
    for category, items in features.items():
        with st.expander(category):
            for item in items:
                st.write(f"• {item}")
    
    # Demo Examples
    st.subheader("🎬 Try These Example Analyses")
    
    examples = [
        {
            "title": "🚀 Scale to 100K Users", 
            "query": "Create a comprehensive strategy to scale WeWine from 15K to 100K users in 12 months",
            "description": "Get a detailed growth playbook with tactics, timelines, and success metrics"
        },
        {
            "title": "🏆 Beat Vivino Strategy",
            "query": "How can WeWine effectively compete against Vivino's 70M user advantage?", 
            "description": "Discover positioning strategies and competitive advantages"
        },
        {
            "title": "💰 Monetization Strategy",
            "query": "Develop a premium subscription model that increases ARPU by 50%",
            "description": "Design pricing, features, and go-to-market for premium tiers"
        }
    ]
    
    for example in examples:
        with st.expander(f"📋 {example['title']}"):
            st.write(example['description'])
            if st.button(f"Run Analysis: {example['title']}", key=example['title']):
                st.info("💡 Copy this query to the Strategic Analysis tab to run the full analysis!")
                st.code(example['query'])

# --- MAIN APPLICATION ---
def main():
    # Setup sidebar and get configuration
    api_key, selected_model = setup_sidebar()
    
    # Initialize AI CEO
    ai_ceo = WeWineStrategicAICEO(api_key=api_key, model=selected_model)
    
    # Main content area
    ai_ceo_dashboard(ai_ceo)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Strategic Analysis",
        "🏆 Competitor Intelligence", 
        "📊 Business Metrics",
        "✨ AI Capabilities",
        "📚 Help & Documentation"
    ])
    
    with tab1:
        strategic_analysis_tab(ai_ceo)
    
    with tab2:
        competitor_analysis_tab(ai_ceo)
    
    with tab3:
        business_metrics_tab()
    
    with tab4:
        feature_showcase_tab()
    
    with tab5:
        st.header("📚 Help & Documentation")
        
        st.subheader("🔧 Setup Instructions")
        st.write("1. **API Key Setup**: Add your OpenAI API key via the sidebar or .env file")
        st.write("2. **Model Selection**: Choose between GPT-4, GPT-3.5, or O1 reasoning models")
        st.write("3. **Cost Control**: Daily usage capped at $1.00 to prevent overspend")
        st.write("4. **Offline Mode**: Framework-based analysis when API unavailable")
        
        st.subheader("💡 Best Practices")
        st.write("• Be specific in your questions for better AI responses")
        st.write("• Use multi-agent analysis for complex strategic decisions") 
        st.write("• Try competitor analysis before developing positioning")
        st.write("• Review business metrics regularly to track progress")
        
        st.subheader("🆘 Troubleshooting")
        st.write("• **API Errors**: Check your API key and OpenAI account balance")
        st.write("• **Cost Limit**: Wait for daily reset or increase limit in code")
        st.write("• **Slow Responses**: O1 models take longer but provide better reasoning")
        st.write("• **No Response**: Check internet connection and API key validity")
        
        st.subheader("🔗 Resources")
        st.write("• [OpenAI API Keys](https://platform.openai.com/api-keys)")
        st.write("• [WeWine.app Strategy Framework](https://wewine.app/)")
        st.write("• [Business Model Canvas](https://canvanizer.com/)")

if __name__ == "__main__":
    main()