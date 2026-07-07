# 📚 INTERVIEW MASTER INDEX
## Complete Navigation for Multi-Agent Loan System Interview Preparation

---

## 🚀 START HERE

### For First-Time Learners: 15-Minute Quick Start
1. **Start**: `QUICK_START_INTERVIEW.md` (5 min)
   - One-sentence explanation
   - Problem vs solution
   - Architecture overview
   - Top 10 questions

2. **Learn**: `PROCESS_FLOWCHART.md` (10 min)
   - Visual flow of how system works
   - Example with Rajesh Kumar scenario
   - Each agent's detailed process

### For Intermediate Prep: 60-Minute Deep Dive
1. **Questions**: `INTERVIEW_QUESTIONS_SHORT.md` (30 min)
   - 50 questions organized by category
   - Quick answers format
   - Easy to memorize

2. **Understanding**: `PROCESS_FLOWCHART.md` (20 min)
   - See actual data flow
   - Understand timing breakdown
   - Learn about audit trails

3. **Details**: `INTERVIEW_GUIDE.md` (10 min)
   - Deep dive on concepts you're weak on
   - Live coding examples

### For Advanced Mastery: 2-Hour Complete Study
1. `QUICK_START_INTERVIEW.md` - Mental model
2. `INTERVIEW_QUESTIONS_SHORT.md` - All 50 questions
3. `INTERVIEW_GUIDE.md` - Advanced topics
4. `PROCESS_FLOWCHART.md` - Visual understanding
5. `README.md` - Project context
6. Live code examples from `INTERVIEW_GUIDE.md`

---

## 📖 DOCUMENT OVERVIEW

### 1. QUICK_START_INTERVIEW.md (⭐ START HERE)
**Reading Time**: 5-10 minutes  
**Difficulty**: Beginner  
**Content**:
- One-sentence problem/solution
- 6-step workflow overview
- Technology stack overview
- Top 10 most important questions
- Common mistakes to avoid
- Interview strategy
- Confidence checklist

**Use When**: You have 15 minutes and want to understand the basics

---

### 2. INTERVIEW_QUESTIONS_SHORT.md
**Reading Time**: 20-30 minutes  
**Difficulty**: Beginner to Intermediate  
**Content**:
- 50 organized questions
- Quick, memorizable answers
- 8 categories:
  - Fundamentals (Q1-Q10)
  - Architecture (Q11-Q20)
  - Agent Details (Q21-Q30)
  - Technical Implementation (Q31-Q40)
  - Business & Compliance (Q41-Q50)
- Quick reference tables
- Sample live coding questions

**Use When**: You want to practice answering likely interview questions

---

### 3. INTERVIEW_GUIDE.md
**Reading Time**: 45-60 minutes  
**Difficulty**: Intermediate to Advanced  
**Content**:
- 24 detailed interview questions
- 7 categories with depth
- Live coding examples (Python, LangGraph, FastAPI)
- Production readiness checklist
- Failure modes and mitigation
- Advanced concepts (feedback loops, bias prevention)
- Failure scenarios and handling

**Use When**: You want deep understanding and coding practice

---

### 4. PROCESS_FLOWCHART.md
**Reading Time**: 20-30 minutes  
**Difficulty**: Visual/Intermediate  
**Content**:
- Complete end-to-end flow diagram
- Detailed breakdown for each agent:
  - Agent 1: Applicant Profile (input → analysis → output)
  - Agent 2: Financial Risk (DTI, credit score, etc.)
  - Agent 3: Loan Decision (synthesis & thresholds)
  - Agent 4: Compliance (regulatory checks)
- Final output to user
- Complete workflow timeline
- Data flow summary

**Use When**: You learn better from visuals, or want to trace through example

---

### 5. README.md
**Reading Time**: 10-15 minutes  
**Difficulty**: Beginner  
**Content**:
- Project overview
- Solution architecture (brief)
- 4 agent descriptions
- Decision thresholds
- Features list
- Performance metrics
- Quick start instructions
- Project structure

**Use When**: You need project context or want to see the original description

---

### 6. SCHEMA_VISUAL_GUIDE.md
**Reading Time**: 15-20 minutes  
**Difficulty**: Intermediate  
**Content**:
- Database schema diagram
- 6 tables explained:
  - loan_applications
  - applicants
  - evaluations
  - audit_logs
  - credit_history
  - aml_screening
- Data relationships
- Query examples
- Application lifecycle diagram

**Use When**: Interview questions about database, audit trails, or data persistence

---

## 🎯 INTERVIEW QUESTION CATEGORIES

### Fundamentals (Easy)
- What is the core problem?
- Why use multiple agents?
- What are the 4 agents?
- What is LangGraph?
- What is MCP?
- **Find in**: INTERVIEW_QUESTIONS_SHORT.md Q1-Q10

### Architecture (Medium)
- Draw the system architecture
- Explain each layer
- How do agents communicate?
- **Find in**: INTERVIEW_QUESTIONS_SHORT.md Q11-Q20 or INTERVIEW_GUIDE.md

### Agents (Medium)
- Describe each agent in detail
- What makes employment risky?
- What is DTI? How calculated?
- What is the decision logic?
- **Find in**: INTERVIEW_QUESTIONS_SHORT.md Q21-Q30 or PROCESS_FLOWCHART.md

### Technical (Hard)
- Implement Agent 1 code
- Create LangGraph workflow
- Write FastAPI endpoint
- Handle errors
- **Find in**: INTERVIEW_GUIDE.md Q31-Q40 (with code examples)

### Business & Compliance (Medium)
- Regulatory requirements
- Appeal/dispute handling
- Bias prevention
- Metrics tracking
- **Find in**: INTERVIEW_QUESTIONS_SHORT.md Q41-Q50 or INTERVIEW_GUIDE.md

---

## 🔑 KEY CONCEPTS QUICK REFERENCE

### Scoring
- **Formula**: (A1×0.15) + (A2×0.30) + (A3×0.30) + (A4×0.25)
- **Decision Thresholds**: ≥70 = Approve, 45-69 = Review, <45 = Reject
- **Find details**: INTERVIEW_QUESTIONS_SHORT.md Q27 or PROCESS_FLOWCHART.md

### DTI (Debt-to-Income)
- **Definition**: (Monthly Debt / Monthly Income) × 100%
- **Benchmark**: <43% good, >50% risky
- **Example**: Income Rs.1L/month, debt Rs.40k/month → 40% DTI
- **Find details**: INTERVIEW_QUESTIONS_SHORT.md Q24 or PROCESS_FLOWCHART.md

### Agents
- **Agent 1** (Profile): 15% weight, evaluates applicant stability
- **Agent 2** (Risk): 30% weight, calculates financial risk
- **Agent 3** (Decision): 30% weight, synthesizes results
- **Agent 4** (Compliance): 25% weight, verifies regulations
- **Find details**: INTERVIEW_QUESTIONS_SHORT.md Q21-Q30

### Technology
- **UI**: Streamlit (chatbot)
- **API**: FastAPI (validation & routing)
- **Orchestration**: LangGraph (workflow management)
- **Communication**: MCP (standardized protocol)
- **Database**: MySQL (storage & audit trail)
- **LLM**: Claude Sonnet (explanations)
- **Find details**: QUICK_START_INTERVIEW.md or README.md

---

## 💡 LEARNING PATHS

### Path 1: Visual Learner (60 min)
1. PROCESS_FLOWCHART.md (understand via diagrams)
2. QUICK_START_INTERVIEW.md (quick summary)
3. INTERVIEW_QUESTIONS_SHORT.md Q1-Q10 (fundamentals)
4. INTERVIEW_GUIDE.md Q1-Q5 (expand on architecture)

### Path 2: Theory-First (90 min)
1. QUICK_START_INTERVIEW.md (conceptual overview)
2. INTERVIEW_GUIDE.md Sections 1-3 (understand principles)
3. PROCESS_FLOWCHART.md (see in action)
4. INTERVIEW_QUESTIONS_SHORT.md (practice Q&A)

### Path 3: Hands-On Coder (120 min)
1. README.md (project context)
2. INTERVIEW_GUIDE.md Sections 1-2 (architecture)
3. INTERVIEW_GUIDE.md Sections 4 (live coding Q17-Q19)
4. INTERVIEW_QUESTIONS_SHORT.md (verify understanding)
5. PROCESS_FLOWCHART.md (trace through code path)

### Path 4: Compliance-Focused (90 min)
1. QUICK_START_INTERVIEW.md (overview)
2. SCHEMA_VISUAL_GUIDE.md (audit trail & data)
3. INTERVIEW_GUIDE.md Sections 7 (regulatory & business)
4. INTERVIEW_QUESTIONS_SHORT.md Q41-Q50 (compliance Q&A)
5. PROCESS_FLOWCHART.md Agent 4 section (compliance in action)

---

## 🎬 PRE-INTERVIEW CHECKLIST

### 1 Week Before
- [ ] Read QUICK_START_INTERVIEW.md
- [ ] Skim INTERVIEW_QUESTIONS_SHORT.md
- [ ] Understand the 4 agents (high level)

### 3 Days Before
- [ ] Study INTERVIEW_GUIDE.md Sections 1-3
- [ ] Practice drawing architecture diagram
- [ ] Memorize decision thresholds

### 1 Day Before
- [ ] Review PROCESS_FLOWCHART.md
- [ ] Practice writing Agent code (INTERVIEW_GUIDE.md Q31-Q40)
- [ ] Know answers to top 10 questions

### Morning Of
- [ ] Read QUICK_START_INTERVIEW.md confidence checklist
- [ ] Do 10-minute warm-up: write DTI formula & scoring formula from memory
- [ ] Review top 10 questions
- [ ] Relax! You've got this.

---

## 🎤 DURING INTERVIEW

### Structure Your Answer
1. **Answer the question directly** (yes/no if applicable)
2. **Provide brief explanation** (2-3 sentences)
3. **Give an example** (use Rajesh Kumar scenario from PROCESS_FLOWCHART.md)
4. **Ask if they want more detail** (shows politeness & confidence)

### Example Answer Pattern:
**Q: What is DTI?**
"DTI is Debt-to-Income ratio - monthly debt divided by monthly income. For example, if someone earns Rs. 1 lakh per month and has Rs. 40,000 in monthly debt obligations, their DTI is 40%. The benchmark is less than 43% is good, above 50% is risky. That's why Agent 2 calculates it to assess loan affordability."

### If You're Stuck
- "Can I think about that for a moment?"
- Draw a diagram
- Ask clarifying questions
- Admit "I'm not 100% sure, but my understanding is..."

### Live Coding
- Clarify requirements first
- Write pseudocode first
- Then write actual code
- Explain each line
- Test with examples

---

## 📊 DIFFICULTY PROGRESSION

```
Easy Questions (Q1-Q15)
├─ Problem statement
├─ Architecture overview
├─ Agent purposes
└─ Basic technology

Medium Questions (Q16-Q35)
├─ Detailed agent logic
├─ Orchestration details
├─ Scoring calculations
└─ Database relationships

Hard Questions (Q36-Q50)
├─ Live coding
├─ Error handling
├─ Production readiness
├─ Regulatory compliance
└─ Advanced concepts
```

**Recommended**: Practice easy first, then medium, then hard.

---

## 🔗 CROSS-REFERENCES

### If Interview Asks About...

**"Explain the architecture"**
→ See: QUICK_START_INTERVIEW.md or INTERVIEW_GUIDE.md Q4-Q10

**"What does each agent do?"**
→ See: INTERVIEW_QUESTIONS_SHORT.md Q21-Q30 or PROCESS_FLOWCHART.md

**"How does scoring work?"**
→ See: INTERVIEW_QUESTIONS_SHORT.md Q27 or PROCESS_FLOWCHART.md Agent 3

**"Calculate DTI for this scenario"**
→ See: PROCESS_FLOWCHART.md Agent 2 section

**"Write the code"**
→ See: INTERVIEW_GUIDE.md Q31-Q40

**"Regulatory requirements?"**
→ See: INTERVIEW_QUESTIONS_SHORT.md Q41 or PROCESS_FLOWCHART.md Agent 4

**"Performance/scalability"**
→ See: INTERVIEW_GUIDE.md Q15-Q16 or README.md

**"Database/Audit trail"**
→ See: SCHEMA_VISUAL_GUIDE.md or INTERVIEW_GUIDE.md Q12

---

## ⏱️ TIME MANAGEMENT

### 90-Minute Interview
- 0-5 min: Introduction & background
- 5-20 min: System architecture discussion
- 20-40 min: Agent deep-dive (Q3-Q10)
- 40-60 min: Live coding (Q31-Q40)
- 60-85 min: Technical details & edge cases
- 85-90 min: Questions, wrap-up

### Prep Schedule
- **Week 1**: Read & understand (2-3 hours)
- **Week 2**: Practice answers (1-2 hours)
- **Week 3**: Live coding practice (1-2 hours)
- **Day Before**: Final review (30 min)

---

## 🏆 SUCCESS TIPS

✅ **Understand the WHY** - Not just what, but why each agent exists
✅ **Use Examples** - Reference Rajesh Kumar scenario from PROCESS_FLOWCHART.md
✅ **Draw Diagrams** - Shows you can think visually
✅ **Mention Tradeoffs** - "This approach is fast but uses more memory"
✅ **Show Business Value** - "555x faster means we process in microseconds"
✅ **Ask Questions** - "Should I explain X in more detail?"
✅ **Be Honest** - "I don't know that, but I'd research it"

---

## 📞 SUPPORT

### Stuck on a Topic?
1. Find it in the cross-reference table above
2. Read that section of the appropriate document
3. Come back to the question

### Forgotten a Concept?
1. Check QUICK_START_INTERVIEW.md for quick definitions
2. See "KEY CONCEPTS QUICK REFERENCE" section above

### Need Code Examples?
→ INTERVIEW_GUIDE.md Sections 4 & 5 (Q31-Q40) have working Python code

### Need Visuals?
→ PROCESS_FLOWCHART.md has detailed ASCII diagrams for each agent

---

## 📈 CONFIDENCE LEVELS

After reading each document, you should be confident about:

**After QUICK_START_INTERVIEW.md**: 60% confident
- You understand the big picture
- You can explain problem/solution
- You know the 4 agents

**After INTERVIEW_QUESTIONS_SHORT.md**: 75% confident
- You can answer quick Q&As
- You know the terminology
- You can handle easy questions

**After INTERVIEW_GUIDE.md**: 85% confident
- You understand deep architecture
- You can handle medium questions
- You have coding examples

**After PROCESS_FLOWCHART.md**: 90% confident
- You can trace through example
- You understand data flow
- You can draw diagrams

**After Practice + Full Study**: 95% confident
- You've answered all 50 questions
- You've written code examples
- You've explained to someone else

---

## 🎯 FINAL ADVICE

**Remember**: Interviewers want to see:
1. **Understanding**: Do you get why this system works?
2. **Communication**: Can you explain it clearly?
3. **Technical Depth**: Can you code it?
4. **Problem-Solving**: How would you handle edge cases?
5. **Business Sense**: Do you understand the value?

**This repo covers ALL of those.**

Good luck! You've got this! 🚀

---

**Last Updated**: July 5, 2026  
**Total Prep Time**: 2-3 hours (comprehensive)  
**Interview Duration**: 60-120 minutes  
**Success Rate**: High (with this preparation!)
