This file contains the full JSON and human-readable content for all three modules of **Course 2: Ask Questions to Make Data-Driven Decisions**, adhering to the "Learn Your Way" pedagogical model.

## **Module C2-M1: Effective Stakeholder Communication**

### **C2-M1 JSON Object**

{  
  "module\_id": "C2-M1",  
  "title": "Effective Stakeholder Communication",  
  "hours": 8,  
  "objectives": \[  
    "Translate ambiguous business goals into SMART, decision-ready questions.",  
    "Map business decisions to specific metrics, cohorts, and time windows.",  
    "Conduct concise stakeholder interviews to clarify constraints, assumptions, and risks.",  
    "Create a prioritized question backlog to guide an analysis project."  
  \],  
  "prerequisites": \[  
    "C1"  
  \],  
  "success\_criteria": \[  
    "Produces a ranked backlog of 6-10 SMART questions, each linked to a specific decision and metric.",  
    "Documents key assumptions, data sources, and potential risks for a business scenario.",  
    "Successfully role-plays a stakeholder interview to extract key project requirements."  
  \],  
  "personalization": {  
    "grade\_level\_adaptation": "Rewrites key passages for a beginner adult, focusing on professional communication and business acumen.",  
    "interest\_hook": "A product manager wants to 'improve user engagement' for a new app. What does that actually mean? A great analyst knows the first step isn't to open a dataset, but to talk to the stakeholder. This module teaches you how to run those critical conversations, turning vague aspirations into a concrete, measurable plan for analysis that delivers real business value.",  
    "learning\_style\_plan": \[  
      "auditory",  
      "kinesthetic"  
    \]  
  },  
  "representations": {  
    "immersive\_text": {  
      "sections": \[  
        {  
          "heading": "The Decision-First Approach",  
          "content": "Analysis without a decision is just a hobby. Before you write a single line of code, you must answer three questions: 1\) Who is the decision-maker? 2\) What is the specific decision they need to make? 3\) By when do they need to make it? This 'decision-first' mindset anchors your entire project. It prevents you from doing interesting but ultimately useless analysis. The goal is not to create charts; the goal is to influence a specific, timely decision.\\n\\nFor example, if a business leader wants to 'understand customer churn,' your first clarifying question is, 'What decision will you make based on this understanding?' Their answer might be, 'I will decide whether to invest in a new loyalty program or in improving customer service.' Now you have a clear purpose. Your analysis is no longer a vague exploration; it's a targeted investigation to compare the potential impact of two different business strategies."  
        },  
        {  
          "heading": "Running an Effective Stakeholder Interview",  
          "content": "Your most important data source is often the human brain of your stakeholder. A short, structured 30-minute conversation can save you weeks of wasted work. The goal is to extract the project's essential parameters. Use this five-point checklist:\\n1. \*\*Outcome:\*\* What does a successful project look like to you? What metric will move?\\n2. \*\*Constraints:\*\* What is our budget, timeline, and data availability?\\n3. \*\*Success Signal:\*\* How will we know if we've succeeded? (e.g., 'A 5% increase in user retention.')\\n4. \*\*Assumptions:\*\* What are we taking for granted? (e.g., 'We assume our tracking data is accurate.')\\n5. \*\*Trade-offs:\*\* If we can't have everything, what's more important: speed or precision? A quick estimate or a perfect model?"  
        }  
      \],  
      "embedded\_questions": \[  
        {  
          "anchor\_section": "The Decision-First Approach",  
          "mcq": {  
            "stem": "A marketing manager asks you to 'analyze our social media performance.' What is the best 'decision-first' clarifying question?",  
            "choices": \[  
              "A) Which social media platform should I look at first?",  
              "B) What is the deadline for this analysis?",  
              "C) What specific decision about budget or strategy will you make based on these findings?",  
              "D) What tools do I have access to for this analysis?"  
            \],  
            "answer": "C",  
            "why": "This question directly links the analysis request to a concrete business decision, which is the core of the decision-first approach."  
          }  
        }  
      \],  
      "timeline": \[  
        "1. Identify the key decision and stakeholder.",  
        "2. Conduct a structured interview to define scope.",  
        "3. Draft a list of SMART questions.",  
        "4. Map each question to a metric and data source.",  
        "5. Create a prioritized question backlog.",  
        "6. Get stakeholder sign-off on the plan."  
      \],  
      "mnemonic": {  
        "topic": "Stakeholder Interview Checklist (OCSATT)",  
        "sentence": "Our Clever Stakeholders Always Talk Truth"  
      }  
    },  
    "narrated\_slides": {  
      "slides": \[  
        {  
          "title": "From Goal to Metric",  
          "bullets": \[  
            "Vague Goal: 'Improve customer satisfaction.'",  
            "Specific Decision: 'Decide whether to invest in faster shipping or better packaging.'",  
            "SMART Question: 'Which factor, shipping time or package condition upon arrival, has a stronger correlation with customer satisfaction scores for Q3?'",  
            "Metric: Customer Satisfaction Score (CSAT)."  
          \],  
          "speaker\_notes": "The analyst's job is to translate fuzzy business goals into concrete, measurable metrics. This slide shows the translation process. The stakeholder starts with a worthy but vague goal. The analyst pushes for the specific decision that goal is tied to. From that decision, they can formulate a SMART question, which in turn points directly to the key metric that needs to be measured. This chain of logic—from goal to decision to question to metric—is fundamental."  
        },  
        {  
          "title": "Documenting Assumptions and Risks",  
          "bullets": \[  
            "Assumption: 'We believe our survey data accurately reflects the opinions of all our customers.'",  
            "Risk: 'This assumption could be wrong. The survey might have sampling bias, over-representing happier customers.'",  
            "Mitigation: 'We will check the demographic distribution of survey respondents against our overall customer base to check for bias.'"  
          \],  
          "speaker\_notes": "Every analysis is built on a foundation of assumptions. A professional analyst doesn't ignore them; they document them. For every assumption you make, identify the corresponding risk if that assumption is wrong. Then, propose a mitigation—a way to check or reduce that risk. This practice builds trust with your stakeholders, as it shows you are thinking critically and being transparent about the limitations of your analysis."  
        }  
      \]  
    },  
    "audio\_lesson\_script": {  
      "dialogue": \[  
        {  
          "role": "Teacher",  
          "text": "Let's role-play. I'm your stakeholder. I tell you, 'I need a dashboard.' What's your first response?"  
        },  
        {  
          "role": "Student",  
          "text": "I'd avoid saying 'Okay, I'll build it.' I think I should ask a question first."  
        },  
        {  
          "role": "Teacher",  
          "text": "Good instinct. What question?"  
        },  
        {  
          "role": "Student",  
          "text": "Tell me about a recent decision you had to make where you wished you had better data. What was it, and what information was missing?"  
        },  
        {  
          "role": "Teacher",  
          "text": "That's a fantastic question. It's much better than asking 'What do you want on the dashboard?' because it focuses on a past pain point. It forces me to think about a real business problem, which will lead us to the metrics that truly matter for the decisions I have to make. You've just uncovered the \*need\* behind the \*request\*."  
        }  
      \],  
      "misconception\_checks": \[  
        "Believing your job is to fulfill requests exactly as they are given (your job is to be a thought partner and clarify the underlying need).",  
        "Thinking that asking clarifying questions is a sign of weakness (it is a sign of professionalism and competence)."  
      \]  
    },  
    "mind\_map": {  
      "root": "Stakeholder Communication",  
      "nodes": \[  
        { "parent": "Stakeholder Communication", "label": "Decision-First Mindset" },  
        { "parent": "Decision-First Mindset", "label": "Who, What, When" },  
        { "parent": "Stakeholder Communication", "label": "Interviewing" },  
        { "parent": "Interviewing", "label": "Outcomes & Constraints" },  
        { "parent": "Interviewing", "label": "Assumptions & Risks" },  
        { "parent": "Stakeholder Communication", "label": "SMART Questions" },  
        { "parent": "Stakeholder Communication", "label": "Question Backlog" }  
      \]  
    }  
  },  
  "hands\_on": {  
    "labs": \[  
      {  
        "tool": "Google Docs",  
        "task": "Given a one-paragraph business scenario (e.g., a gym owner wants to increase member retention), write a full 'Decision Brief and Question Backlog'. The brief should define the key decision, stakeholders, and success metrics. The backlog should contain at least five prioritized SMART questions.",  
        "dataset": "N/A \- Scenario-based.",  
        "check": "The document clearly separates the brief from the backlog, and all five questions meet the SMART criteria."  
      }  
    \],  
    "datasets": \[\]  
  },  
  "adaptive\_quiz": {  
    "items": \[  
      {  
        "id": "C2M1\_001",  
        "difficulty": "easy",  
        "type": "mcq",  
        "stem": "What is the primary goal of a stakeholder interview for a data analyst?",  
        "answer": "To clarify the business problem and define the scope and success metrics for the analysis.",  
        "rationale": "The interview is about understanding the 'why' behind the request to ensure the analysis is relevant and actionable."  
      },  
      {  
        "id": "C2M1\_002",  
        "difficulty": "medium",  
        "type": "mcq",  
        "stem": "A documented assumption in an analysis plan is 'We assume the past three months of sales data are representative of a typical year.' What is the biggest risk associated with this assumption?",  
        "answer": "Seasonality: The past three months might be an unusually high or low period, leading to incorrect forecasts.",  
        "rationale": "Assumptions about timeframes often carry the risk of ignoring seasonal or cyclical patterns in the data."  
      }  
    \],  
    "summary\_feedback": {  
      "glows": \[  
        "You excel at translating vague goals into more specific questions."  
      \],  
      "grows": \[  
        "Practice explicitly identifying the risks and assumptions tied to your questions. This is a key step for building trust."  
      \],  
      "next\_steps": \[  
        "Review the narrated slide 'Documenting Assumptions and Risks' and apply that framework to your lab submission."  
      \]  
    }  
  },  
  "portfolio\_artifact": {  
    "deliverable": "A professional, one-page Decision Brief and Question Backlog for a business scenario in your chosen interest area.",  
    "rubric": \[  
      "Criterion: Decision Clarity; 4 Levels: The brief clearly and concisely defines the primary business decision, the decision-maker, and the timeline."  
    \],  
    "github\_requirements": \[  
      "Create a new folder in your repository named 'C2-Asking-Questions'.",  
      "Create a new file named 'C2-M1-Decision-Brief.md'.",  
      "Format your brief and backlog professionally using Markdown and commit the file."  
    \]  
  },  
  "accessibility": \[  
    "Role-playing scripts will be available as text.",  
    "Checklist templates will be provided in accessible document formats.",  
    "Visual frameworks like mind maps will have text-based outlines available."  
  \],  
  "ethics\_and\_bias": \[  
    "Bias to watch for: Stakeholder bias. Your stakeholder may already have a desired outcome in mind. Your job is to be an objective partner. Phrase your questions neutrally to uncover the true problem, not just to confirm their hypothesis.",  
    "Privacy note: During the 'Ask' phase, clarify what level of data granularity is truly needed. Push for using aggregated or anonymized data whenever possible to protect privacy from the very start of the project."  
  \],  
  "time\_on\_task": {  
    "reading": 2,  
    "videos": 1.5,  
    "labs": 3.5,  
    "assessments": 1  
  }  
}

### **C2-M1 Human-Readable Rendering**

This module focuses on the most important and often-overlooked part of data analysis: asking the right questions. Before you even touch a piece of data, you need to be an expert communicator. We'll teach you how to conduct professional stakeholder interviews to turn vague requests like "improve engagement" into a concrete, actionable plan. You'll learn the "decision-first" approach and master writing SMART questions. The hands-on project involves creating a "Decision Brief and Question Backlog," a core document used by analysts at top companies to ensure their work has a real business impact.

## **Module C2-M2: Data Storytelling & Narrative Structure**

### **C2-M2 JSON Object**

{  
  "module\_id": "C2-M2",  
  "title": "Data Storytelling & Narrative Structure",  
  "hours": 8,  
  "objectives": \[  
    "Structure an analytical presentation using a clear narrative arc.",  
    "Design effective and minimalist slides with one clear takeaway per slide.",  
    "Select audience-appropriate visualizations to support a key message.",  
    "Deliver a concise stakeholder presentation with clear recommendations."  
  \],  
  "prerequisites": \[  
    "C2-M1"  
  \],  
  "success\_criteria": \[  
    "Produces a 6-8 slide deck with a logical story flow and a single, clear takeaway.",  
    "Designs slides where each title is a full-sentence headline stating the key insight.",  
    "Presents a 3-5 minute talk that earns a 'pass' on clarity, evidence, and actionability from peer review.",  
    "Uses chart encodings appropriate for the data and the message."  
  \],  
  "personalization": {  
    "grade\_level\_adaptation": "Rewrites key passages for a beginner adult, using analogies from filmmaking and journalism to explain narrative structure.",  
    "interest\_hook": "How does a record label convince a radio station to play their new artist? They don't just send a spreadsheet of streaming numbers. They tell a story: 'This artist is exploding in this key demographic, their sound is similar to this established star, and their engagement on TikTok predicts a breakout hit.' This module teaches you how to be a data storyteller—to weave your findings into a compelling narrative that persuades stakeholders to act.",  
    "learning\_style\_plan": \[  
      "visual",  
      "auditory"  
    \]  
  },  
  "representations": {  
    "immersive\_text": {  
      "sections": \[  
        {  
          "heading": "Your Analysis is a Story",  
          "content": "Stakeholders rarely have time to admire the complexity of your analysis. They have a problem, and they need to know if you have an answer. The most effective way to communicate your findings is not as a list of facts, but as a story. A good data story has a clear beginning (the business problem), a middle (the key evidence you found), and an end (your recommendation). \\n\\nYour job is to guide your audience on a journey from confusion to clarity. Don't just show them your data; explain what it means. The narrative provides the context that makes your numbers memorable and meaningful. Every chart and every bullet point should serve a single purpose: to advance that central narrative."  
        },  
        {  
          "heading": "The Headline Principle: One Takeaway Per Slide",  
          "content": "The most common mistake in data presentations is creating cluttered slides with generic titles like 'Sales by Quarter.' A professional analyst designs slides with the key takeaway as the title. Instead of 'Sales by Quarter,' the title should be a full sentence: 'Q3 Sales Increased 15% Driven by the New Product Launch.'\\n\\nThis 'headline principle' forces you to have a single, clear point for each slide. The chart or table on the slide then serves as the evidence for that headline. This makes your presentation incredibly easy for a busy executive to follow. They can understand the entire story just by reading your slide titles. Everything else is supporting detail."  
        }  
      \],  
      "embedded\_questions": \[  
        {  
          "anchor\_section": "The Headline Principle: One Takeaway Per Slide",  
          "mcq": {  
            "stem": "Which of the following is the best example of a slide title that follows the 'headline principle'?",  
            "choices": \[  
              "A) User Retention Data",  
              "B) User Retention Dropped 5% in May for New Sign-Ups",  
              "C) Chart of User Retention",  
              "D) Analysis of User Retention Metrics"  
            \],  
            "answer": "B",  
            "why": "It's a full sentence that states the single most important finding or takeaway that the visual on the slide will support."  
          }  
        }  
      \],  
      "timeline": \[  
        "1. Start with the final recommendation.",  
        "2. State the business question you answered.",  
        "3. Provide the single most important piece of evidence (the 'aha\!' moment).",  
        "4. Briefly show supporting evidence.",  
        "5. Conclude by restating your recommendation and defining the next step."  
      \],  
      "mnemonic": {  
        "topic": "Presentation Story Arc (R-Q-E-S-R)",  
        "sentence": "Recommendations Quietly Echo Supported Results"  
      }  
    },  
    "narrated\_slides": {  
      "slides": \[  
        {  
          "title": "Before: A Bad Slide",  
          "bullets": \[  
            "Title: 'Marketing Data'",  
            "Shows a dense table of numbers.",  
            "Includes three different charts with no clear connection.",  
            "Has a paragraph of text in the footer."  
          \],  
          "speaker\_notes": "Let's look at a common example of what not to do. This slide is titled 'Marketing Data'—it tells the audience nothing. The body is a confusing mix of a dense table and unrelated charts. A stakeholder looking at this has no idea what they are supposed to conclude. This is not communication; it's a data dump. It puts all the work of interpretation onto the audience, and busy people will just tune out."  
        },  
        {  
          "title": "After: A Good Slide",  
          "bullets": \[  
            "Title: 'The Summer Campaign Drove a 30% Increase in New User Sign-Ups'",  
            "Shows one simple bar chart comparing sign-ups before and after the campaign.",  
            "Uses color to highlight the 'after' bar.",  
            "Includes a single annotation: '+30%'"  
          \],  
          "speaker\_notes": "Now, let's see the same information presented effectively. The title is a full sentence that tells the audience the main point immediately. There is only one simple chart that provides the evidence for that headline. Color is used strategically to draw the eye. There is no clutter. A stakeholder can understand the key finding in less than five seconds. This is a slide that respects the audience's time and communicates with clarity and impact."  
        }  
      \]  
    },  
    "audio\_lesson\_script": {  
      "dialogue": \[  
        {  
          "role": "Teacher",  
          "text": "You've finished your analysis and found a really interesting insight. You're excited to share it. What's the most common trap analysts fall into at this stage?"  
        },  
        {  
          "role": "Student",  
          "text": "Trying to share \*everything\*? Like showing all the work and every single thing they found?"  
        },  
        {  
          "role": "Teacher",  
          "text": "Exactly. It's called the 'curse of knowledge.' You are so deep in the data that you forget your audience isn't. They don't need to see your 100-line SQL query or every failed analysis you tried. Your job is to curate. You must have the discipline to find the single most important insight and build your story around that one thing."  
        },  
        {  
          "role": "Student",  
          "text": "So, it's more about editing than just presenting."  
        },  
        {  
          "role": "Teacher",  
          "text": "That's the perfect way to put it. A great data storyteller is a ruthless editor. They find the gem of the insight and then cut away everything that doesn't make that gem shine brighter."  
        }  
      \],  
      "misconception\_checks": \[  
        "Believing that a good presentation shows how much work you did (it shows how much value you created).",  
        "Thinking that more data on a slide is better (less is almost always more)."  
      \]  
    },  
    "mind\_map": {  
      "root": "Data Storytelling",  
      "nodes": \[  
        { "parent": "Data Storytelling", "label": "Narrative Arc" },  
        { "parent": "Narrative Arc", "label": "Problem \-\> Evidence \-\> Recommendation" },  
        { "parent": "Data Storytelling", "label": "Slide Design" },  
        { "parent": "Slide Design", "label": "Headline Principle" },  
        { "parent": "Slide Design", "label": "Minimalism" },  
        { "parent": "Data Storytelling", "label": "Audience" },  
        { "parent": "Audience", "label": "Tailor the Message" },  
        { "parent": "Data Storytelling", "label": "The Recommendation" }  
      \]  
    }  
  },  
  "hands\_on": {  
    "labs": \[  
      {  
        "tool": "Google Slides / PowerPoint",  
        "task": "Given a simple dataset and a key finding (e.g., 'Sales in the West region have declined by 15%'), create a 3-slide mini-presentation that tells this story. Slide 1: State the problem. Slide 2: Show the evidence with a simple chart. Slide 3: Propose a recommendation and next step. All slides must follow the 'headline principle'.",  
        "dataset": "mini\_sales\_data.csv",  
        "check": "The submission is a 3-slide deck where each slide title is a full, declarative sentence summarizing the slide's content."  
      }  
    \],  
    "datasets": \[\]  
  },  
  "adaptive\_quiz": {  
    "items": \[  
      {  
        "id": "C2M2\_001",  
        "difficulty": "easy",  
        "type": "mcq",  
        "stem": "What is the 'headline principle' in slide design?",  
        "answer": "Making the slide title a full sentence that states the main takeaway of the slide.",  
        "rationale": "This principle forces clarity and makes the presentation easy to follow for a busy audience."  
      },  
      {  
        "id": "C2M2\_002",  
        "difficulty": "medium",  
        "type": "mcq",  
        "stem": "You are presenting to a non-technical CEO. Your presentation should prioritize:",  
        "answer": "A clear narrative and actionable recommendations.",  
        "rationale": "Executives care about the business implication of your findings, not the technical details of your analysis."  
      }  
    \],  
    "summary\_feedback": {  
      "glows": \[  
        "You have a great grasp of the headline principle for slide titles."  
      \],  
      "grows": \[  
        "Focus on building a clear narrative arc. Ensure your slides flow logically from the problem to the solution."  
      \],  
      "next\_steps": \[  
        "Review the 'Presentation Story Arc' timeline and try to structure your next lab submission using that sequence."  
      \]  
    }  
  },  
  "portfolio\_artifact": {  
    "deliverable": "A 6-8 slide 'decision-first' presentation deck for the business scenario from the C2-M1 lab. The deck should include speaker notes and at least two visualizations.",  
    "rubric": \[  
      "Criterion: Clarity of Takeaway; 4 Levels: The presentation has a single, unambiguous main point that is supported by all slides and easy for a non-expert to understand."  
    \],  
    "github\_requirements": \[  
      "Navigate to your 'C2-Asking-Questions' folder.",  
      "Create a new file named 'C2-M2-Storytelling-Deck.pdf'.",  
      "Export your slide deck as a PDF and commit the file."  
    \]  
  },  
  "accessibility": \[  
    "All charts and graphs will require descriptive alt text or a detailed caption.",  
    "Presentations will use large, sans-serif fonts and high-contrast color palettes.",  
    "Speaker notes will be provided as a transcript for all presentation examples."  
  \],  
  "ethics\_and\_bias": \[  
    "Bias to watch for: Cherry-picking. This is the act of only showing data that supports your desired conclusion. A responsible analyst tells the whole story, including findings that may contradict their hypothesis or the stakeholder's beliefs. Always include limitations and uncertainties in your presentation.",  
    "Privacy note: When creating visuals, ensure they are aggregated to a level that prevents the re-identification of any individual."  
  \],  
  "time\_on\_task": {  
    "reading": 2,  
    "videos": 1.5,  
    "labs": 3.5,  
    "assessments": 1  
  }  
}

### **C2-M2 Human-Readable Rendering**

An analysis is useless if you can't convince anyone to act on it. This module transforms you from a data cruncher into a data storyteller. Using analogies from the music industry, you'll learn how to structure your findings into a compelling narrative that guides your audience from a problem to a solution. We'll focus on the art of minimalist and effective presentation design, including the powerful "headline principle" where every slide has one clear, actionable takeaway. Your hands-on work will be to build a professional, persuasive slide deck based on the business problem you defined in the last module, preparing you for the course capstone presentation.

## **Module C2-M3: Structuring an Analysis Plan**

### **C2-M3 JSON Object**

{  
  "module\_id": "C2-M3",  
  "title": "Structuring an Analysis Plan",  
  "hours": 6,  
  "objectives": \[  
    "Decompose a business problem into distinct analytical tasks.",  
    "Create a formal, one-page analysis plan document.",  
    "Estimate timelines and scope for an analytics project.",  
    "Identify necessary data sources and potential roadblocks."  
  \],  
  "prerequisites": \[  
    "C2-M1"  
  \],  
  "success\_criteria": \[  
    "Submits a complete analysis plan for a case study that includes all seven required sections.",  
    "The plan's timeline and scope are realistic for the problem described.",  
    "The plan correctly identifies the required data and at least one significant potential roadblock."  
  \],  
  "personalization": {  
    "grade\_level\_adaptation": "Rewrites key passages for a beginner adult, using a project management and recipe-following analogy.",  
    "interest\_hook": "Before a top restaurant chain like Chipotle develops a new menu item, their analytics team creates a detailed plan. They define how they'll measure success, what data they need to collect (from taste tests, supply chain costs, and sales pilots), the timeline for the analysis, and the key risks. This upfront planning is what separates professional analysis from amateur exploration. This module teaches you how to create that professional-grade analysis plan.",  
    "learning\_style\_plan": \[  
      "visual",  
      "kinesthetic"  
    \]  
  },  
  "representations": {  
    "immersive\_text": {  
      "sections": \[  
        {  
          "heading": "The Blueprint for Your Analysis",  
          "content": "An analysis plan is a document that outlines the 'what, why, how, and when' of your project. It is your blueprint. Just as you wouldn't build a house without a blueprint, you shouldn't start a complex analysis without a plan. This document serves two critical purposes: first, it forces you to think through the entire project from start to finish, helping you anticipate problems. Second, it serves as a communication tool to get alignment with your stakeholders. It ensures everyone agrees on the project's goals, scope, and deliverables \*before\* you begin the work."  
        },  
        {  
          "heading": "The 7 Key Components of an Analysis Plan",  
          "content": "A concise, one-page analysis plan is a powerful tool. It should contain these seven sections:\\n1. \*\*Background & Business Question:\*\* 1-2 sentences explaining the problem and the primary question from your backlog.\\n2. \*\*Stakeholders & Decision:\*\* Who is this for and what specific decision will they make?\\n3. \*\*Success Metrics:\*\* How will we measure success? What is the target for our key metric?\\n4. \*\*Methodology & Tasks:\*\* A high-level, bulleted list of the steps you will take (e.g., 'Extract data from sales DB', 'Clean and process data', 'Analyze regional performance', 'Visualize findings in Tableau').\\n5. \*\*Data Sources:\*\* A list of the specific tables, files, or APIs you will need to access.\\n6. \*\*Timeline & Deliverables:\*\* A simple timeline with key milestones and a clear list of what you will deliver at the end (e.g., 'A slide deck and an interactive dashboard').\\n7. \*\*Risks & Roadblocks:\*\* 1-2 potential problems you might encounter (e.g., 'Risk: Data quality in the marketing table is known to be poor.')"  
        }  
      \],  
      "embedded\_questions": \[  
        {  
          "anchor\_section": "The 7 Key Components of an Analysis Plan",  
          "mcq": {  
            "stem": "Which section of the analysis plan is designed to get alignment with your manager on the project's final output?",  
            "choices": \[  
              "A) Data Sources",  
              "B) Success Metrics",  
              "C) Timeline & Deliverables",  
              "D) Risks & Roadblocks"  
            \],  
            "answer": "C",  
            "why": "The 'Timeline & Deliverables' section explicitly lists what the stakeholder will receive at the end of the project, which is critical for managing expectations and getting alignment."  
          }  
        }  
      \],  
      "timeline": \[  
        "1. Finalize Question Backlog (from C2-M1).",  
        "2. Draft the 7 sections of the analysis plan.",  
        "3. Review the draft with a peer or mentor for clarity.",  
        "4. Present the plan to your stakeholder for feedback.",  
        "5. Get official sign-off before starting the analysis."  
      \],  
      "mnemonic": {  
        "topic": "Analysis Plan Sections (BSSMMTR)",  
        "sentence": "Busy Stakeholders Seldom Make Major Timeline Risks"  
      }  
    },  
    "narrated\_slides": {  
      "slides": \[  
        {  
          "title": "Example Analysis Plan: One-Pager",  
          "bullets": \[  
            "Shows a visually clean, one-page document with the 7 sections clearly labeled.",  
            "Uses a fictional restaurant chain scenario: 'Analyzing the Impact of Delivery Apps on In-Store Sales.'"  
          \],  
          "speaker\_notes": "Here is a concrete example of what a good, concise analysis plan looks like. Notice it's not a 20-page document; it's a one-page summary. It clearly states the business question, the stakeholders, and the success metrics. The methodology is a simple bulleted list, not a technical essay. It lists the exact data tables needed. The timeline is simple, and the deliverables are unambiguous. Finally, it calls out a key risk. This single document contains everything a stakeholder needs to know to approve your project."  
        },  
        {  
          "title": "Scoping: The Art of the Possible",  
          "bullets": \[  
            "Good Scope: 'Analyze the impact of our Q3 email campaign on sales in the US market.'",  
            "Bad Scope (Too Broad): 'Analyze all of marketing's impact on all sales.'",  
            "Bad Scope (Too Narrow): 'Analyze the open rate of one email's subject line.'",  
            "A well-scoped project is answerable within the given timeline and data constraints."  
          \],  
          "speaker\_notes": "Scoping is one of the hardest parts of project planning. A common mistake for new analysts is to define a scope that is either way too big or way too small. A project to 'analyze all of marketing' could take years. A project to analyze a single subject line might not be impactful enough. The sweet spot is a question that is big enough to be meaningful but small enough to be answerable in a reasonable timeframe. Getting this right comes with experience, but starting with a formal plan helps you practice."  
        }  
      \]  
    },  
    "audio\_lesson\_script": {  
      "dialogue": \[  
        {  
          "role": "Teacher",  
          "text": "You've presented your beautiful, one-page analysis plan to your stakeholder. They love it, but they say, 'This is great, but can you also add an analysis of our top three competitors?' What do you do?"  
        },  
        {  
          "role": "Student",  
          "text": "My first instinct is to say 'yes' because I want to be helpful."  
        },  
        {  
          "role": "Teacher",  
          "text": "A very common instinct\! But what is the danger of just saying 'yes'?"  
        },  
        {  
          "role": "Student",  
          "text": "It will add more work and could delay the original project. It's 'scope creep'."  
        },  
        {  
          "role": "Teacher",  
          "text": "Exactly. This is where your analysis plan becomes your best friend. A professional response would be: 'That's a great question. It's not in the original scope of our plan, which will affect our timeline. Let's discuss the trade-offs. We can either push back the deadline for the current analysis to include this, or we can scope this as a separate, fast-follow project after we finish the first one. Which would you prefer?'"  
        }  
      \],  
      "misconception\_checks": \[  
        "Thinking an analysis plan is a permanent, rigid document (it's a living document, but changes must be consciously discussed and approved).",  
        "Believing that planning is wasted time that could be spent analyzing (good planning saves huge amounts of time later by preventing rework and misalignment)."  
      \]  
    },  
    "mind\_map": {  
      "root": "Analysis Plan",  
      "nodes": \[  
        { "parent": "Analysis Plan", "label": "Business Question" },  
        { "parent": "Analysis Plan", "label": "Stakeholders & Decision" },  
        { "parent": "Analysis Plan", "label": "Success Metrics" },  
        { "parent": "Analysis Plan", "label": "Methodology" },  
        { "parent": "Analysis Plan", "label": "Data Sources" },  
        { "parent": "Analysis Plan", "label": "Timeline & Deliverables" },  
        { "parent": "Analysis Plan", "label": "Risks" }  
      \]  
    }  
  },  
  "hands\_on": {  
    "labs": \[  
      {  
        "tool": "Google Docs",  
        "task": "Using the business scenario and question backlog you developed in C2-M1, create a complete, one-page Analysis Plan. The plan must include all seven sections discussed in the module.",  
        "dataset": "N/A \- Uses prior work.",  
        "check": "The submitted document is one page, contains all seven required sections, and is consistent with the user's previously developed question backlog."  
      }  
    \],  
    "datasets": \[\]  
  },  
  "adaptive\_quiz": {  
    "items": \[  
      {  
        "id": "C2M3\_001",  
        "difficulty": "easy",  
        "type": "mcq",  
        "stem": "What are the two primary purposes of an analysis plan?",  
        "answer": "To force the analyst to think through the project, and to get alignment with stakeholders.",  
        "rationale": "An analysis plan is both a thinking tool for the analyst and a communication tool for the team."  
      },  
      {  
        "id": "C2M3\_002",  
        "difficulty": "medium",  
        "type": "short",  
        "stem": "You discover that a key data source you listed in your plan is unavailable. This should have been listed in which section of your analysis plan?",  
        "answer": "Risks & Roadblocks",  
        "rationale": "Dependency on unavailable or poor-quality data is a classic project risk that should be identified upfront."  
      }  
    \],  
    "summary\_feedback": {  
      "glows": \[  
        "You're doing an excellent job of connecting the business question to the success metrics."  
      \],  
      "grows": \[  
        "Be more specific when listing your methodology. Instead of 'Analyze the data,' break it down into more concrete tasks like 'Calculate weekly conversion rate' and 'Segment by user demographic.'"  
      \],  
      "next\_steps": \[  
        "Look at the example analysis plan again and notice the level of detail in the 'Methodology & Tasks' section."  
      \]  
    }  
  },  
  "portfolio\_artifact": {  
    "deliverable": "A professional, one-page Analysis Plan for your C2-M2 storytelling deck project.",  
    "rubric": \[  
      "Criterion: Completeness; 4 Levels: The plan includes all seven required sections, and each section is filled out with relevant, specific information."  
    \],  
    "github\_requirements": \[  
      "Navigate to your 'C2-Asking-Questions' folder.",  
      "Create a new file named 'C2-M3-Analysis-Plan.md'.",  
      "Write your one-page plan in Markdown and commit the file."  
    \]  
  },  
  "accessibility": \[  
    "Analysis plan templates will be provided as accessible documents.",  
    "Examples will be explained in detail in audio and text formats.",  
    "The 7-part structure provides a clear, logical flow for all learners to follow."  
  \],  
  "ethics\_and\_bias": \[  
    "Bias to watch for: Planning fallacy. This is the human tendency to underestimate the time needed to complete a future task. When creating your timeline, be realistic. It's always better to under-promise and over-deliver. Consider adding a buffer for unexpected problems.",  
    "Privacy note: Your analysis plan should explicitly state how you will handle PII. Mentioning that you will use 'anonymized transaction data' is a good practice to include in the 'Data Sources' section."  
  \],  
  "time\_on\_task": {  
    "reading": 1.5,  
    "videos": 1,  
    "labs": 2.5,  
    "assessments": 1  
  }  
}

### **C2-M3 Human-Readable Rendering**

This module teaches you how to create the single most important document for any analytics project: the analysis plan. Think of it as a recipe you write before you start cooking. Using a scenario from a major restaurant chain, you'll learn the seven key components of a professional analysis plan, from defining the business question to identifying risks. This plan will become your blueprint, forcing you to think through every step of your project and, crucially, serving as a communication tool to get agreement from your stakeholders *before* you start the actual work. Your hands-on project is to create a complete, one-page analysis plan for the presentation you outlined in the previous module, adding another key professional document to your portfolio.