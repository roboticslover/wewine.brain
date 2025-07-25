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
    initial_sidebar_state="collapsed"  # Better for mobile
)

# --- ENHANCED MOBILE-RESPONSIVE CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Enhanced typography hierarchy */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: clamp(2rem, 6vw, 3.5rem);
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #722F37 0%, #B8860B 50%, #DAA520 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .main-subheader {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1rem, 3vw, 1.2rem);
        font-weight: 400;
        color: #B8860B;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.4;
    }

    /* Mobile-optimized AI response box */
    .ai-response {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        border-left: 4px solid #B8860B;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #EAEAEA;
        box-shadow: 0 4px 20px rgba(184, 134, 11, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(184, 134, 11, 0.2);
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .ai-response h1, .ai-response h2, .ai-response h3, .ai-response h4 {
        font-family: 'Playfair Display', serif;
        color: #FFFFFF;
        border-bottom: 1px solid rgba(184, 134, 11, 0.3);
        padding-bottom: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        font-size: clamp(1.1rem, 4vw, 1.4rem);
    }
    
    .ai-response strong {
        color: #DAA520;
        font-weight: 600;
    }

    .ai-response p {
        margin-bottom: 0.75rem;
    }

    .ai-response ul, .ai-response ol {
        padding-left: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .ai-response li {
        margin-bottom: 0.25rem;
    }

    /* Enhanced status indicators */
    .status-connected {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        box-shadow: 0 2px 10px rgba(40, 167, 69, 0.3);
    }
    
    .status-offline {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        box-shadow: 0 2px 10px rgba(220, 53, 69, 0.3);
    }
    
    .cost-tracker {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }

    /* Mobile-optimized buttons */
    .stButton > button {
        border-radius: 12px;
        border: 2px solid #B8860B;
        color: #B8860B;
        background: linear-gradient(135deg, rgba(184, 134, 11, 0.1) 0%, rgba(184, 134, 11, 0.05) 100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        width: 100%;
        min-height: 2.5rem;
        backdrop-filter: blur(5px);
    }
    
    .stButton > button:hover {
        border-color: #DAA520;
        color: #FFFFFF;
        background: linear-gradient(135deg, #B8860B 0%, #DAA520 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(184, 134, 11, 0.4);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Enhanced feature cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%);
        border: 1px solid rgba(184, 134, 11, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(184, 134, 11, 0.25);
        border-color: rgba(184, 134, 11, 0.5);
    }

    /* Enhanced agent cards with better mobile layout */
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }

    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }

    /* Mobile-optimized tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 48px;
        background: linear-gradient(135deg, rgba(184, 134, 11, 0.1) 0%, rgba(184, 134, 11, 0.05) 100%);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        white-space: nowrap;
        border: 1px solid rgba(184, 134, 11, 0.2);
        color: #B8860B;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #B8860B 0%, #DAA520 100%);
        color: #FFFFFF;
        font-weight: 600;
        border-color: #DAA520;
        box-shadow: 0 2px 10px rgba(184, 134, 11, 0.3);
    }

    /* Mobile-responsive metrics */
    .metric-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(184, 134, 11, 0.2);
        margin: 0.5rem 0;
    }

    /* Enhanced selectbox styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid rgba(184, 134, 11, 0.3);
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }

    /* Enhanced text area styling */
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid rgba(184, 134, 11, 0.3);
        border-radius: 8px;
        color: #EAEAEA;
        backdrop-filter: blur(5px);
    }

    /* Loading spinner enhancement */
    .stSpinner > div {
        border-top-color: #B8860B !important;
    }

    /* Mobile-optimized sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }

    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(184, 134, 11, 0.1) 0%, rgba(184, 134, 11, 0.05) 100%);
        border-radius: 8px;
        border: 1px solid rgba(184, 134, 11, 0.2);
        backdrop-filter: blur(5px);
    }

    /* Responsive grid improvements */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        .agent-card {
            font-size: 0.8rem;
            padding: 0.75rem;
            min-height: 70px;
        }
        
        .ai-response {
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
    }

    /* Enhanced progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #28a745, #B8860B, #dc3545);
    }

    /* Better code block styling */
    .stCodeBlock {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid rgba(184, 134, 11, 0.2);
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }

    /* Enhanced info/warning/error boxes */
    .stAlert {
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(184, 134, 11, 0.2);
    }

    /* Smooth animations */
    * {
        transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }

    /* Mobile navigation hint */
    .mobile-nav-hint {
        display: none;
        background: linear-gradient(135deg, rgba(184, 134, 11, 0.1) 0%, rgba(184, 134, 11, 0.05) 100%);
        color: #B8860B;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
        font-size: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(184, 134, 11, 0.2);
    }

    @media (max-width: 768px) {
        .mobile-nav-hint {
            display: block;
        }
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

# --- ENHANCED MOBILE-RESPONSIVE SIDEBAR ---
def setup_sidebar():
    with st.sidebar:
        st.markdown('<h2 style="color: #B8860B; text-align: center; margin-bottom: 1.5rem;">🍷 AI CEO Control</h2>', unsafe_allow_html=True)
        
        # API Configuration with improved UX
        with st.expander("🔑 API Settings", expanded=True):
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
        
        # Model Selection with better layout
        with st.expander("🧠 AI Model", expanded=False):
            model_options = {
                "GPT-4": "gpt-4",
                "GPT-4 Turbo": "gpt-4-turbo-preview", 
                "GPT-3.5 Turbo": "gpt-3.5-turbo",
                "O1-Preview": "o1-preview",
                "O1-Mini": "o1-mini"
            }
            
            selected_model_name = st.selectbox(
                "Choose AI Model:",
                list(model_options.keys()),
                index=0,
                help="O1 models are best for complex reasoning"
            )
            
            selected_model = model_options[selected_model_name]
        
        # Enhanced Cost Tracking
        st.markdown("### 💰 Usage Monitor")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Daily Cost", f"${st.session_state.api_usage_cost:.3f}", "")
        with col2:
            st.metric("API Calls", st.session_state.api_calls_count, "")
        
        # Enhanced progress bar
        cost_percentage = min(st.session_state.api_usage_cost / 1.0, 1.0)
        st.progress(cost_percentage)
        
        remaining = 1.0 - st.session_state.api_usage_cost
        
        if cost_percentage > 0.8:
            st.warning(f"⚠️ ${remaining:.3f} remaining")
        elif cost_percentage >= 1.0:
            st.error("🚫 Daily limit reached")
        else:
            st.info(f"💚 ${remaining:.3f} available")
        
        # System Status with better visual feedback
        st.markdown("### 📊 Status")
        
        if api_key:
            st.markdown('<div class="status-connected">🟢 AI CEO Online</div>', unsafe_allow_html=True)
            st.caption(f"Model: {selected_model_name}")
        else:
            st.markdown('<div class="status-offline">🔴 Offline Mode</div>', unsafe_allow_html=True)
            st.caption("Framework Analysis Only")
        
        # Quick Actions
        if st.button("🔄 Reset Usage", help="Reset daily API usage", use_container_width=True):
            st.session_state.api_usage_cost = 0.0
            st.session_state.api_calls_count = 0
            st.success("✅ Usage reset!")
            st.rerun()
        
        # Compact Business Metrics
        with st.expander("📈 Key Metrics"):
            metrics = {
                "Monthly Users": "15,000",
                "Monthly Revenue": "$42.5K", 
                "Conversion Rate": "3.2%",
                "App Rating": "4.4⭐"
            }
            
            for metric, value in metrics.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.caption(metric)
                with col2:
                    st.write(value)
        
        return api_key, selected_model

# --- ENHANCED MAIN DASHBOARD ---
def ai_ceo_dashboard(ai_ceo):
    # Mobile navigation hint
    st.markdown('<div class="mobile-nav-hint">👆 Use sidebar for settings • Swipe tabs to navigate</div>', unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🍷 WeWine Strategic AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subheader">Your AI-powered business strategy partner for wine-tech success</p>', unsafe_allow_html=True)
    
    # Compact Agent Overview for mobile
    st.subheader("🤖 AI Advisory Team")
    
    # Responsive grid layout
    col1, col2, col3 = st.columns(3)
    
    agents = [
        ("🎯 CEO Agent", "Strategic Leadership"),
        ("📊 Market Research", "Competitive Intel"),
        ("📈 Growth Agent", "User Acquisition"),
        ("🛠️ Product Agent", "Feature Strategy"),
        ("💰 CFO Agent", "Financial Analysis"),
        ("🎨 Brand Agent", "Market Positioning")
    ]
    
    for i, (title, desc) in enumerate(agents):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f'<div class="agent-card">{title}<br><small>{desc}</small></div>', unsafe_allow_html=True)

# --- ENHANCED STRATEGIC ANALYSIS TAB ---
def strategic_analysis_tab(ai_ceo):
    st.header("🎯 Strategic Analysis")
    
    # Quick Actions with better mobile layout
    st.subheader("⚡ Quick Insights")
    
    # Single column layout for mobile-first
    if st.button("🏆 Competitive Analysis", use_container_width=True):
        with st.spinner("🤖 Analyzing competitive landscape..."):
            response = ai_ceo.generate_competitive_analysis()
            st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    # Inline selectors for better mobile UX
    col1, col2 = st.columns(2)
    with col1:
        growth_focus = st.selectbox("Growth Focus", 
                                   ["user_acquisition", "retention", "monetization", 
                                    "market_expansion", "product_growth"], key="growth_focus")
    
    with col2:
        roadmap_period = st.selectbox("Roadmap Period", 
                                     ["90_days", "6_months", "1_year"], key="roadmap_period")
    
    if st.button("📈 Growth Strategy", use_container_width=True):
        with st.spinner(f"📈 Developing {growth_focus} strategy..."):
            response = ai_ceo.generate_growth_strategy(growth_focus)
            st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    if st.button("🛠️ Product Roadmap", use_container_width=True):
        with st.spinner(f"🛠️ Creating {roadmap_period} roadmap..."):
            response = ai_ceo.generate_product_roadmap(roadmap_period)
            st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Enhanced Custom Query Section
    st.subheader("💬 Strategic Consultation")
    
    # Expandable examples for cleaner mobile view
    with st.expander("💡 Example Questions"):
        query_examples = [
            "How can WeWine achieve 100K users in 12 months?",
            "What's our best strategy against Vivino's dominance?",
            "How should we price our premium subscription?",
            "What partnerships should we prioritize for growth?",
            "How can we improve our conversion rate from 3.2% to 5%?"
        ]
        
        for example in query_examples:
            if st.button(f"📝 {example}", key=f"example_{example[:20]}", use_container_width=True):
                st.session_state.custom_query = example
    
    # Custom query input
    custom_query = st.text_area(
        "Ask your AI CEO team:",
        value=st.session_state.get('custom_query', ''),
        placeholder="e.g., How can WeWine differentiate from competitors while scaling to 100K users?",
        height=100,
        key="custom_query_input"
    )
    
    # Action buttons with better mobile layout
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧠 Single Agent", type="primary", use_container_width=True) and custom_query:
            with st.spinner("🧠 AI CEO analyzing..."):
                response = ai_ceo._call_openai_api(custom_query)
                st.markdown(f'<div class="ai-response"><h4>🧠 AI CEO Response</h4>{response}</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("👥 Multi-Agent", type="primary", use_container_width=True) and custom_query:
            with st.spinner("👥 Multi-agent team collaborating..."):
                response = ai_ceo.multi_agent_analysis(custom_query)
                st.markdown(f'<div class="ai-response"><h4>👥 Team Analysis</h4>{response}</div>', unsafe_allow_html=True)

# --- ENHANCED COMPETITOR ANALYSIS TAB ---
def competitor_analysis_tab(ai_ceo):
    st.header("🏆 Competitive Intelligence")
    
    # Mobile-optimized competitor overview
    st.subheader("📊 Market Landscape")
    
    # Responsive metrics grid
    metrics_data = [
        ("Total Competitors", "20+"),
        ("Market Leaders", "5"),
        ("Total Funding", "$350M+"),
        ("Combined Users", "85M+")
    ]
    
    cols = st.columns(2)
    for i, (metric, value) in enumerate(metrics_data):
        with cols[i % 2]:
            st.metric(metric, value)
    
    # Competitor database with better mobile layout
    competitors = {
        "Vivino": {"users": "70M+", "funding": "$224M", "strength": "Massive community", "weakness": "Information overload"},
        "Delectable": {"users": "2M+", "funding": "$15M+", "strength": "Expert curation", "weakness": "Intimidating for beginners"},
        "Firstleaf": {"users": "1M+", "funding": "$27.6M", "strength": "AI accuracy", "weakness": "US-only, subscription lock-in"},
        "Wine-Searcher": {"users": "5M+", "funding": "Private", "strength": "Price data", "weakness": "Complex interface"},
        "Nakedwines": {"users": "964K", "funding": "$10M", "strength": "Unique model", "weakness": "Limited selection"}
    }
    
    st.subheader("🎯 Competitor Analysis")
    
    selected_competitor = st.selectbox(
        "Select Competitor:",
        list(competitors.keys()),
        format_func=lambda x: f"{x} ({competitors[x]['users']} users)"
    )
    
    if selected_competitor:
        comp_data = competitors[selected_competitor]
        
        # Mobile-friendly info display
        with st.expander(f"📋 {selected_competitor} Details", expanded=True):
            st.write(f"**👥 Users:** {comp_data['users']}")
            st.write(f"**💰 Funding:** {comp_data['funding']}")
            st.write(f"**💪 Strength:** {comp_data['strength']}")
            st.write(f"**⚠️ Weakness:** {comp_data['weakness']}")
        
        if st.button(f"🔍 Analyze {selected_competitor}", use_container_width=True):
            with st.spinner(f"🔍 Analyzing {selected_competitor}..."):
                analysis = ai_ceo.generate_competitive_analysis(selected_competitor)
                st.markdown(f'<div class="ai-response"><h4>🔍 {selected_competitor} Analysis</h4>{analysis}</div>', unsafe_allow_html=True)
    
    # Strategic positioning with better UX
    st.subheader("📈 Positioning Strategy")
    
    positioning_questions = [
        "How should WeWine position against market leaders?",
        "What's our unique value proposition vs. Vivino?", 
        "Which competitor should we target first?",
        "What partnerships can counter competitor advantages?"
    ]
    
    selected_question = st.selectbox("Strategic Question:", positioning_questions)
    
    if st.button("💡 Get Strategy", use_container_width=True):
        with st.spinner("💡 Developing positioning strategy..."):
            response = ai_ceo._call_openai_api(selected_question)
            st.markdown(f'<div class="ai-response"><h4>💡 Positioning Strategy</h4>{response}</div>', unsafe_allow_html=True)

# --- ENHANCED BUSINESS METRICS TAB ---
def business_metrics_tab():
    st.header("📊 Business Intelligence")
    
    # Mobile-optimized KPI grid
    st.subheader("📈 Key Metrics")
    
    metrics_data = [
        ("Monthly Users", "15,000", "+12%", "success"),
        ("Monthly Revenue", "$42,500", "+8%", "success"), 
        ("Conversion Rate", "3.2%", "+0.3%", "normal"),
        ("LTV:CAC", "7.1:1", "+0.5", "success")
    ]
    
    # Responsive 2x2 grid for mobile
    for i in range(0, len(metrics_data), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(metrics_data):
                metric, value, delta, _ = metrics_data[i + j]
                with col:
                    st.metric(metric, value, delta)
    
    # Mobile-friendly charts
    st.subheader("📈 Growth Trends")
    
    # Single column layout for better mobile viewing
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [35000, 37000, 39000, 41000, 38000, 42500]
    users = [8000, 9200, 10500, 11800, 13200, 15000]
    
    # Revenue chart
    fig_revenue = px.line(x=months, y=revenue, title="💰 Revenue Growth")
    fig_revenue.update_traces(line=dict(color='#B8860B', width=3))
    fig_revenue.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # User growth chart
    fig_users = px.bar(x=months, y=users, title="👥 User Growth")
    fig_users.update_traces(marker_color='#722F37')
    fig_users.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_users, use_container_width=True)
    
    # Business health check with expandable sections
    st.subheader("💊 Business Health")
    
    with st.expander("✅ Strengths", expanded=True):
        strengths = [
            "Strong user growth (+12% monthly)",
            "Healthy LTV:CAC ratio (7.1:1)",
            "Good app rating (4.4/5)",
            "Growing revenue (+8% monthly)"
        ]
        for strength in strengths:
            st.write(f"• {strength}")
    
    with st.expander("🎯 Areas for Improvement"):
        improvements = [
            "Conversion rate below target (3.2% vs 5%)",
            "Need to reduce customer acquisition cost",
            "Increase average order value",
            "Improve retention rates"
        ]
        for improvement in improvements:
            st.write(f"• {improvement}")

# --- ENHANCED FEATURE SHOWCASE TAB ---
def feature_showcase_tab():
    st.header("✨ AI Capabilities")
    
    # Mobile-optimized feature showcase
    features = {
        "🎯 Strategic Analysis": [
            "Market positioning and competitive analysis",
            "Growth strategy with actionable tactics",
            "Product roadmap using RICE framework",
            "Go-to-market strategy for new markets"
        ],
        "🧠 Multi-Agent Intelligence": [
            "CEO, Growth, Product, CFO, Brand perspectives",
            "Collaborative analysis with synthesis",
            "Specialized expertise for complex questions",
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
        with st.expander(category, expanded=False):
            for item in items:
                st.write(f"• {item}")
    
    # Demo examples with better mobile UX
    st.subheader("🎬 Try These Examples")
    
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
        with st.expander(f"📋 {example['title']}", expanded=False):
            st.write(example['description'])
            if st.button(f"Copy Query", key=f"copy_{example['title']}", use_container_width=True):
                st.code(example['query'])
                st.success("✅ Query copied! Paste it in Strategic Analysis tab.")

# --- ENHANCED HELP TAB ---
def help_documentation_tab():
    st.header("📚 Help & Documentation")
    
    # Mobile-optimized help sections
    with st.expander("🔧 Setup Guide", expanded=True):
        st.write("**1. API Key Setup**")
        st.write("Add your OpenAI API key via sidebar or .env file")
        
        st.write("**2. Model Selection**")
        st.write("Choose between GPT-4, GPT-3.5, or O1 reasoning models")
        
        st.write("**3. Cost Control**")
        st.write("Daily usage capped at $1.00 to prevent overspend")
        
        st.write("**4. Offline Mode**")
        st.write("Framework-based analysis when API unavailable")
    
    with st.expander("💡 Best Practices"):
        practices = [
            "Be specific in your questions for better AI responses",
            "Use multi-agent analysis for complex strategic decisions",
            "Try competitor analysis before developing positioning",
            "Review business metrics regularly to track progress"
        ]
        for practice in practices:
            st.write(f"• {practice}")
    
    with st.expander("🆘 Troubleshooting"):
        issues = [
            ("API Errors", "Check your API key and OpenAI account balance"),
            ("Cost Limit", "Wait for daily reset or increase limit in code"),
            ("Slow Responses", "O1 models take longer but provide better reasoning"),
            ("No Response", "Check internet connection and API key validity")
        ]
        for issue, solution in issues:
            st.write(f"**{issue}:** {solution}")
    
    with st.expander("🔗 Useful Resources"):
        resources = [
            ("[OpenAI API Keys](https://platform.openai.com/api-keys)", "Get your API key"),
            ("[WeWine Strategy](https://wewine.app/)", "Company information"),
            ("[Business Canvas](https://canvanizer.com/)", "Strategy planning tool")
        ]
        for resource, desc in resources:
            st.write(f"• {resource} - {desc}")

# --- MAIN APPLICATION ---
def main():
    # Initialize session state for mobile UX
    if 'custom_query' not in st.session_state:
        st.session_state.custom_query = ''
    
    # Setup sidebar and get configuration
    api_key, selected_model = setup_sidebar()
    
    # Initialize AI CEO
    ai_ceo = WeWineStrategicAICEO(api_key=api_key, model=selected_model)
    
    # Main dashboard
    ai_ceo_dashboard(ai_ceo)
    
    # Enhanced mobile-friendly navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Strategy",
        "🏆 Competitors", 
        "📊 Metrics",
        "✨ Features",
        "📚 Help"
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
        help_documentation_tab()

if __name__ == "__main__":
    main()
