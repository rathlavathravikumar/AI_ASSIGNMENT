"""
Task definitions for the Email Triage OpenEnv.

Three tasks of increasing difficulty, each with:
  - A rich, realistic email dataset
  - A ground-truth answer key
  - A programmatic grader returning a score in [0, 1]
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import (
    Category,
    Email,
    EmailClassification,
    FlagType,
    Priority,
)


# ---------------------------------------------------------------------------
# TASK 1  —  Easy: Priority & Category Classifier
# ---------------------------------------------------------------------------

TASK1_EMAILS: List[Email] = [
    Email(
        id="e01",
        subject="URGENT: Production server is down!",
        sender="Ops Team",
        sender_email="ops@company.com",
        body=(
            "Our production database server has crashed. "
            "All customer-facing services are offline. "
            "Need immediate attention from the engineering team. "
            "ETA for fix? Customers are calling in."
        ),
        timestamp="2026-04-07T09:00:00Z",
        labels=["ops"],
    ),
    Email(
        id="e02",
        subject="Your April newsletter from TechDigest",
        sender="TechDigest",
        sender_email="noreply@techdigest.io",
        body=(
            "This month in tech: AI breakthroughs, new frameworks, "
            "and the latest developer tools. Click to read more. "
            "Unsubscribe at any time."
        ),
        timestamp="2026-04-07T08:00:00Z",
        labels=["newsletter"],
    ),
    Email(
        id="e03",
        subject="Invoice #INV-2026-0412 from AWS",
        sender="AWS Billing",
        sender_email="billing@aws.amazon.com",
        body=(
            "Your AWS invoice for March 2026 is ready. "
            "Total amount due: $4,312.87. "
            "Payment is due by April 15, 2026. "
            "Log in to the AWS console to view the full invoice."
        ),
        timestamp="2026-04-07T07:30:00Z",
        labels=["finance"],
        attachments=["invoice_march2026.pdf"],
    ),
    Email(
        id="e04",
        subject="Congratulations! You've won a $500 gift card!",
        sender="Rewards Center",
        sender_email="rewards@promo-deals-win.biz",
        body=(
            "You have been selected as our lucky winner! "
            "Click here to claim your $500 Amazon gift card. "
            "Offer expires in 24 hours. "
            "No purchase necessary."
        ),
        timestamp="2026-04-07T06:15:00Z",
        labels=[],
    ),
    Email(
        id="e05",
        subject="Q2 roadmap review — please confirm attendance",
        sender="Sarah Chen",
        sender_email="sarah.chen@company.com",
        body=(
            "Hi team, we have a roadmap review scheduled for Friday at 2 PM. "
            "Please confirm your attendance by tomorrow EOD. "
            "The agenda and pre-read docs are attached."
        ),
        timestamp="2026-04-07T10:00:00Z",
        labels=["work"],
        attachments=["q2_roadmap_prereads.pdf"],
    ),
    Email(
        id="e06",
        subject="Mom's birthday dinner — Saturday 7pm",
        sender="Dad",
        sender_email="dad@family.com",
        body=(
            "Hey! Just a reminder that we're doing dinner for mom's birthday "
            "on Saturday at 7pm at La Trattoria. Let me know if you can make it. "
            "Bring your famous tiramisu if possible!"
        ),
        timestamp="2026-04-07T09:45:00Z",
        labels=["personal"],
    ),
    Email(
        id="e07",
        subject="Security Alert: New sign-in from unknown device",
        sender="Security Team",
        sender_email="security@company.com",
        body=(
            "We detected a new sign-in to your account from an unrecognized device "
            "in Lagos, Nigeria at 03:42 UTC. "
            "If this was you, no action is needed. "
            "If not, please secure your account immediately by clicking here."
        ),
        timestamp="2026-04-07T04:00:00Z",
        labels=["security"],
    ),
    Email(
        id="e08",
        subject="Weekly team standup notes — April 7",
        sender="Slack Bot",
        sender_email="notifications@slack.com",
        body=(
            "Here is your automated weekly standup digest: "
            "3 blockers reported, 12 tasks completed, 5 PRs merged. "
            "No action needed — this is an automated summary."
        ),
        timestamp="2026-04-07T09:30:00Z",
        labels=["newsletter"],
    ),
    Email(
        id="e09",
        subject="Customer complaint: Order #ORD-88423 not delivered",
        sender="Support System",
        sender_email="support@company.com",
        body=(
            "Customer John Patel (john.patel@gmail.com) has filed a complaint. "
            "Order #ORD-88423 was expected April 3rd and has not arrived. "
            "Customer is requesting a full refund if not resolved within 24 hours. "
            "SLA breach imminent."
        ),
        timestamp="2026-04-07T11:00:00Z",
        labels=["support"],
    ),
    Email(
        id="e10",
        subject="Lunch at the new ramen place?",
        sender="Alex Kumar",
        sender_email="alex.kumar@company.com",
        body=(
            "Hey! Have you tried that new ramen spot on 5th Ave? "
            "A few of us are going tomorrow at noon — want to join? "
            "No pressure, just thought it'd be fun."
        ),
        timestamp="2026-04-07T10:30:00Z",
        labels=["personal"],
    ),
]

TASK1_GROUND_TRUTH: Dict[str, EmailClassification] = {
    "e01": EmailClassification(email_id="e01", priority=Priority.URGENT,  category=Category.WORK,       flag=FlagType.URGENT,           requires_reply=True),
    "e02": EmailClassification(email_id="e02", priority=Priority.LOW,     category=Category.NEWSLETTER,  flag=None,                      requires_reply=False),
    "e03": EmailClassification(email_id="e03", priority=Priority.NORMAL,  category=Category.FINANCE,     flag=FlagType.ACTION_REQUIRED,  requires_reply=False),
    "e04": EmailClassification(email_id="e04", priority=Priority.LOW,     category=Category.SPAM,        flag=None,                      requires_reply=False),
    "e05": EmailClassification(email_id="e05", priority=Priority.NORMAL,  category=Category.WORK,        flag=FlagType.ACTION_REQUIRED,  requires_reply=True),
    "e06": EmailClassification(email_id="e06", priority=Priority.LOW,     category=Category.PERSONAL,    flag=None,                      requires_reply=False),
    "e07": EmailClassification(email_id="e07", priority=Priority.URGENT,  category=Category.WORK,        flag=FlagType.URGENT,           requires_reply=True),
    "e08": EmailClassification(email_id="e08", priority=Priority.LOW,     category=Category.NEWSLETTER,  flag=None,                      requires_reply=False),
    "e09": EmailClassification(email_id="e09", priority=Priority.URGENT,  category=Category.SUPPORT,     flag=FlagType.URGENT,           requires_reply=True),
    "e10": EmailClassification(email_id="e10", priority=Priority.LOW,     category=Category.PERSONAL,    flag=None,                      requires_reply=False),
}


# ---------------------------------------------------------------------------
# TASK 2  —  Medium: Inbox Zero — multi-action triage
# ---------------------------------------------------------------------------

TASK2_EMAILS: List[Email] = [
    Email(id="m01", subject="URGENT: Contract renewal — deadline TODAY", sender="Legal Team", sender_email="legal@company.com",
          body="The vendor contract for our SaaS platform expires TODAY at midnight. Need sign-off from management ASAP or we lose access. Please escalate immediately.", timestamp="2026-04-07T08:00:00Z"),
    Email(id="m02", subject="Your Spotify Weekly Digest", sender="Spotify", sender_email="noreply@spotify.com",
          body="Here's what's new in music this week. Discover 20 new tracks based on your listening history.", timestamp="2026-04-07T07:00:00Z"),
    Email(id="m03", subject="Re: Project Phoenix — blocker on API integration", sender="Dev Team Lead", sender_email="dev.lead@company.com",
          body="We are completely blocked on the payment gateway integration. The sandbox credentials you provided last week are expired. Can you send new ones? The launch is in 3 days.", timestamp="2026-04-07T09:15:00Z"),
    Email(id="m04", subject="Claim your free iPhone 15!", sender="Prize Zone", sender_email="no-reply@prize-zone-win.net",
          body="Congratulations, you've been selected! Fill out this quick survey to receive your free iPhone 15 Pro Max. Limited time only!", timestamp="2026-04-06T22:00:00Z"),
    Email(id="m05", subject="Monthly marketing newsletter — March roundup", sender="Marketing Bot", sender_email="newsletter@company.com",
          body="March in review: 4.2% CTR improvement, 3 campaigns launched, 1 A/B test completed. Full report attached.", timestamp="2026-04-07T06:30:00Z"),
    Email(id="m06", subject="Performance review form due Friday", sender="HR Team", sender_email="hr@company.com",
          body="Reminder: your annual performance self-review form is due this Friday. Please complete it in the HR portal by 5 PM.", timestamp="2026-04-07T08:30:00Z"),
    Email(id="m07", subject="You have a new Jira comment", sender="Jira", sender_email="jira@atlassian.com",
          body="Alex Kumar commented on PROJ-441: 'Pushed the fix. Ready for review.' View the issue in Jira.", timestamp="2026-04-07T09:00:00Z"),
    Email(id="m08", subject="VIP Client — Acme Corp is threatening to churn", sender="Account Manager", sender_email="accounts@company.com",
          body="URGENT: Acme Corp (our $2M ARR client) has escalated to their C-suite. They're unhappy with response times. CEO wants a call by EOD today. Please prioritize.", timestamp="2026-04-07T10:30:00Z"),
    Email(id="m09", subject="Coupon: 40% off your next order!", sender="Amazon", sender_email="deals@amazon.com",
          body="Your personalized Amazon deal: 40% off electronics this weekend. Shop now before the offer expires.", timestamp="2026-04-07T07:45:00Z"),
    Email(id="m10", subject="Budget approval needed — Q2 headcount", sender="Finance", sender_email="finance@company.com",
          body="The Q2 headcount request (3 engineers, 1 PM) needs budget approval by end of week. Please review the spreadsheet and respond with approval or comments.", timestamp="2026-04-07T09:00:00Z"),
    Email(id="m11", subject="Podcast recommendation: 'Software Architecture Weekly'", sender="Friend", sender_email="friend@gmail.com",
          body="Hey! You should check out this podcast. I've been listening for 3 months and it's super insightful for engineering leaders.", timestamp="2026-04-06T18:00:00Z"),
    Email(id="m12", subject="System maintenance window — April 10, 2-4 AM", sender="DevOps", sender_email="devops@company.com",
          body="Scheduled maintenance: April 10, 2-4 AM UTC. All services will be briefly unavailable. No action needed from your side — just a heads-up.", timestamp="2026-04-07T08:00:00Z"),
    Email(id="m13", subject="RE: Missed deadline on Report #7", sender="Stakeholder", sender_email="vp.product@company.com",
          body="This is the second time the weekly report has been missed. Please respond with an explanation and a corrective action plan by tomorrow morning.", timestamp="2026-04-07T11:00:00Z"),
    Email(id="m14", subject="Your GitHub Actions run failed", sender="GitHub", sender_email="noreply@github.com",
          body="Workflow 'CI/CD Pipeline' failed on branch main. Job 'test' exited with code 1. View the run details in GitHub Actions.", timestamp="2026-04-07T09:45:00Z"),
    Email(id="m15", subject="Webinar invite: Future of AI in Enterprise", sender="TechConf", sender_email="events@techconf.io",
          body="Join us April 20th for a free webinar on AI adoption in enterprise settings. Register now to save your seat.", timestamp="2026-04-07T07:00:00Z"),
    Email(id="m16", subject="Data breach — immediate response required", sender="Security Team", sender_email="security@company.com",
          body="We have detected unauthorized access to our customer data warehouse. Approximately 50,000 records may be exposed. Incident response team has been activated. You must join the emergency bridge call NOW: +1-800-SECURITY.", timestamp="2026-04-07T10:00:00Z"),
    Email(id="m17", subject="Your subscription receipt — April", sender="Figma", sender_email="billing@figma.com",
          body="Receipt for your Figma Professional subscription: $15.00 charged on April 7, 2026. Transaction ID: TXN-928374.", timestamp="2026-04-07T08:15:00Z"),
    Email(id="m18", subject="Lunch meetup — downtown coffee?", sender="Colleague", sender_email="colleague@company.com",
          body="Hey! A few of us are grabbing coffee downtown on Thursday. Want to join? Totally casual, no agenda.", timestamp="2026-04-07T10:00:00Z"),
    Email(id="m19", subject="New feature request from enterprise customer", sender="Customer Success", sender_email="cs@company.com",
          body="Enterprise customer DataCorp has formally requested SSO integration (SAML 2.0). This was promised in Q3 last year. They're escalating if not on roadmap by April 15.", timestamp="2026-04-07T09:30:00Z"),
    Email(id="m20", subject="April Fool's recap — best pranks of 2026", sender="BuzzFeed", sender_email="newsletter@buzzfeed.com",
          body="You won't believe these April Fool's pranks! Click to see the 25 best pranks of 2026 from around the world.", timestamp="2026-04-07T06:00:00Z"),
]

# Ground truth: expected actions per email
# Format: {email_id: {"action": "archive"|"delete"|"flag"|"reply", "flag_type": ..., "priority": ..., "category": ...}}
TASK2_GROUND_TRUTH: Dict[str, Dict[str, Any]] = {
    "m01": {"action": "flag",    "flag_type": "urgent",           "priority": "urgent", "category": "work"},
    "m02": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "newsletter"},
    "m03": {"action": "flag",    "flag_type": "action_required",  "priority": "urgent", "category": "work"},
    "m04": {"action": "delete",  "flag_type": None,               "priority": "low",    "category": "spam"},
    "m05": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "newsletter"},
    "m06": {"action": "flag",    "flag_type": "action_required",  "priority": "normal", "category": "work"},
    "m07": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "work"},
    "m08": {"action": "flag",    "flag_type": "urgent",           "priority": "urgent", "category": "support"},
    "m09": {"action": "delete",  "flag_type": None,               "priority": "low",    "category": "spam"},
    "m10": {"action": "flag",    "flag_type": "action_required",  "priority": "normal", "category": "finance"},
    "m11": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "personal"},
    "m12": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "work"},
    "m13": {"action": "flag",    "flag_type": "urgent",           "priority": "urgent", "category": "work"},
    "m14": {"action": "flag",    "flag_type": "action_required",  "priority": "normal", "category": "work"},
    "m15": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "newsletter"},
    "m16": {"action": "flag",    "flag_type": "urgent",           "priority": "urgent", "category": "work"},
    "m17": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "finance"},
    "m18": {"action": "archive", "flag_type": None,               "priority": "low",    "category": "personal"},
    "m19": {"action": "flag",    "flag_type": "action_required",  "priority": "normal", "category": "support"},
    "m20": {"action": "delete",  "flag_type": None,               "priority": "low",    "category": "newsletter"},
}


# ---------------------------------------------------------------------------
# TASK 3  —  Hard: Executive Assistant — full end-to-end triage
# ---------------------------------------------------------------------------

TASK3_EMAILS: List[Email] = [
    Email(id="h01", subject="Board meeting moved to April 9 — confirmation needed", sender="CEO", sender_email="ceo@company.com",
          body="The board meeting has been moved to April 9 at 10 AM EST. I need you to confirm attendance on my behalf, update the calendar invite, and prepare a 1-page executive summary of Q1 performance to circulate beforehand. The deck is attached — please summarize slides 3-7.", timestamp="2026-04-07T07:00:00Z", attachments=["board_deck_q1.pdf"], thread_id="t01"),
    Email(id="h02", subject="RE: Board meeting moved to April 9 — confirmation needed", sender="Board Secretary", sender_email="secretary@board.com",
          body="Hi, following up on the board meeting confirmation. We need a response by 5 PM today to finalize the quorum. Please confirm the CEO's attendance and provide the Q1 summary.", timestamp="2026-04-07T11:00:00Z", thread_id="t01"),
    Email(id="h03", subject="CRITICAL: Payment processing is broken — revenue impact", sender="CTO", sender_email="cto@company.com",
          body="Our payment processor Stripe threw errors for the past 2 hours. Estimated $80K in lost revenue. I need you to: (1) contact Stripe support immediately, (2) notify the CEO, (3) draft a customer-facing status page update, (4) schedule a post-mortem for next Monday.", timestamp="2026-04-07T09:30:00Z"),
    Email(id="h04", subject="Duplicate: Server issues — payment down", sender="VP Engineering", sender_email="vp.eng@company.com",
          body="Heads up — payment processing is down due to Stripe API issues. Engineering is working on it. Just flagging for executive visibility.", timestamp="2026-04-07T09:35:00Z"),
    Email(id="h05", subject="Partnership opportunity with Google Cloud", sender="Google Cloud Partnerships", sender_email="partnerships@google.com",
          body="We'd like to explore a formal technology partnership. This would include co-marketing, joint case studies, and preferred pricing for your customers. Please have the appropriate executive reach out to schedule an initial call.", timestamp="2026-04-07T08:00:00Z"),
    Email(id="h06", subject="RE: Partnership opportunity with Google Cloud", sender="CEO", sender_email="ceo@company.com",
          body="This looks promising. Please respond on my behalf expressing interest and request a call next week. Also loop in our VP of Business Development.", timestamp="2026-04-07T08:30:00Z", thread_id="t02"),
    Email(id="h07", subject="Employee complaint — hostile work environment", sender="HR Director", sender_email="hr.director@company.com",
          body="We have received a formal complaint from a senior engineer regarding a hostile work environment in the infrastructure team. This is confidential. The CEO needs to be aware and we need to schedule a meeting with Legal and HR by end of week.", timestamp="2026-04-07T10:00:00Z"),
    Email(id="h08", subject="Press inquiry — TechCrunch wants a comment on layoff rumors", sender="PR Team", sender_email="pr@company.com",
          body="TechCrunch reporter Jane Smith is writing a story about rumored layoffs in the tech sector and wants a comment from our CEO. Deadline is 3 PM today. We recommend a 'no comment' or a carefully worded response. Please advise.", timestamp="2026-04-07T09:00:00Z"),
    Email(id="h09", subject="Your LinkedIn Weekly Top Stories", sender="LinkedIn", sender_email="messages-noreply@linkedin.com",
          body="See what's trending in your network this week. 5 people in your network found new jobs. 3 posts in your feed are getting traction.", timestamp="2026-04-07T07:30:00Z"),
    Email(id="h10", subject="Sales team needs updated pricing deck by noon", sender="Head of Sales", sender_email="sales@company.com",
          body="We have a major demo with Fortune 500 prospect at 2 PM today. The current pricing deck is outdated (still shows 2025 prices). Need the updated Q2 2026 pricing document — can you locate and send it? This deal is worth $1.5M ARR.", timestamp="2026-04-07T08:45:00Z"),
    Email(id="h11", subject="Re: Sales team needs updated pricing deck by noon", sender="CFO", sender_email="cfo@company.com",
          body="The new pricing doc is finalized and approved. File is in the shared drive under /Finance/Pricing/Q2_2026_Pricing_Final.xlsx. Please forward to sales immediately.", timestamp="2026-04-07T09:00:00Z", thread_id="t03"),
    Email(id="h12", subject="Reminder: CEO keynote draft due end of day", sender="Events Team", sender_email="events@company.com",
          body="Just a reminder that the CEO's keynote draft for TechSummit 2026 (April 25) is due end of today. The speaking slot is 45 minutes. Theme: 'Building Resilient Systems at Scale'. Please ensure the CEO reviews and approves the draft.", timestamp="2026-04-07T09:15:00Z"),
    Email(id="h13", subject="Vendor invoice dispute — $120K overcharge", sender="Finance Team", sender_email="finance@company.com",
          body="We've identified a $120,000 overcharge on our annual SaaS contract with Salesforce. The contract clearly states $380K but we were billed $500K. Need executive sign-off to escalate to Salesforce's enterprise account team.", timestamp="2026-04-07T10:15:00Z"),
    Email(id="h14", subject="Happy birthday! 🎂", sender="Company Bot", sender_email="bot@company.com",
          body="Today is David Park's birthday! Send him a birthday message.", timestamp="2026-04-07T08:00:00Z"),
    Email(id="h15", subject="Acquisition target — confidential", sender="Board Member", sender_email="board.member@investors.com",
          body="CONFIDENTIAL. The board is considering acquiring Dataflow Inc (ARR: $8M, team: 42 engineers). The CEO needs to review the term sheet attached and respond before Thursday's board call. This must not be shared beyond the CEO and CFO.", timestamp="2026-04-07T07:45:00Z", attachments=["termsheet_dataflow_confidential.pdf"]),
    Email(id="h16", subject="Newsletter: Best productivity apps of 2026", sender="ProductivityHacks", sender_email="newsletter@productivityhacks.io",
          body="Top 10 productivity apps you need right now! GTD tools, focus timers, AI writing assistants and more.", timestamp="2026-04-07T06:00:00Z"),
    Email(id="h17", subject="Customer escalation — SLA breach for 3rd time", sender="Enterprise Support", sender_email="enterprise.support@company.com",
          body="FinBank Corp (Tier 1 customer, $3.2M ARR) has experienced their 3rd SLA breach this quarter. They are threatening legal action. Need executive intervention — CEO or COO should reach out personally today.", timestamp="2026-04-07T10:30:00Z"),
    Email(id="h18", subject="Spam: Make $5000/day from home!", sender="Money Fast", sender_email="makerich@get-money-fast.biz",
          body="Work from home, make $5000 per day! No experience needed. Click here to start your journey to financial freedom.", timestamp="2026-04-07T05:00:00Z"),
    Email(id="h19", subject="Q1 OKR review — slide deck draft", sender="Strategy Team", sender_email="strategy@company.com",
          body="Attached is the Q1 OKR review deck draft for the executive team. Please review and provide feedback by Thursday. Key highlights: 7/10 OKRs met, 2 missed by >20%.", timestamp="2026-04-07T09:00:00Z", attachments=["q1_okr_review_draft.pptx"]),
    Email(id="h20", subject="DUPLICATE: Stripe payment issues — executive FYI", sender="Engineering Manager", sender_email="eng.manager@company.com",
          body="Forwarding for executive visibility — we are experiencing Stripe payment processing issues. CTO is already handling this. No action needed from your side.", timestamp="2026-04-07T09:40:00Z"),
]

# Ground truth for Task 3: complex multi-criteria scoring
TASK3_GROUND_TRUTH: Dict[str, Dict[str, Any]] = {
    "h01": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": True,  "thread_id": "t01"},
    "h02": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "urgent",          "requires_reply": True,  "is_thread": True,  "thread_id": "t01"},
    "h03": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "urgent",          "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h04": {"action": "archive", "priority": "low",     "category": "work",       "flag_type": None,              "requires_reply": False, "is_duplicate": True},
    "h05": {"action": "flag",    "priority": "normal",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": True,  "thread_id": "t02"},
    "h06": {"action": "flag",    "priority": "normal",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": True,  "thread_id": "t02"},
    "h07": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "urgent",          "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h08": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h09": {"action": "archive", "priority": "low",     "category": "newsletter", "flag_type": None,              "requires_reply": False, "is_thread": False, "thread_id": None},
    "h10": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": True,  "thread_id": "t03"},
    "h11": {"action": "archive", "priority": "low",     "category": "work",       "flag_type": None,              "requires_reply": False, "is_thread": True,  "thread_id": "t03"},
    "h12": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h13": {"action": "flag",    "priority": "urgent",  "category": "finance",    "flag_type": "action_required", "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h14": {"action": "archive", "priority": "low",     "category": "work",       "flag_type": None,              "requires_reply": False, "is_thread": False, "thread_id": None},
    "h15": {"action": "flag",    "priority": "urgent",  "category": "work",       "flag_type": "action_required", "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h16": {"action": "archive", "priority": "low",     "category": "newsletter", "flag_type": None,              "requires_reply": False, "is_thread": False, "thread_id": None},
    "h17": {"action": "flag",    "priority": "urgent",  "category": "support",    "flag_type": "urgent",          "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h18": {"action": "delete",  "priority": "low",     "category": "spam",       "flag_type": None,              "requires_reply": False, "is_thread": False, "thread_id": None},
    "h19": {"action": "flag",    "priority": "normal",  "category": "work",       "flag_type": "follow_up",       "requires_reply": True,  "is_thread": False, "thread_id": None},
    "h20": {"action": "archive", "priority": "low",     "category": "work",       "flag_type": None,              "requires_reply": False, "is_duplicate": True},
}


# ---------------------------------------------------------------------------
# Task registry
# ---------------------------------------------------------------------------

TASKS: Dict[str, Dict[str, Any]] = {
    "task_1": {
        "name": "Priority Inbox Classifier",
        "difficulty": "easy",
        "description": (
            "You are an AI email assistant. Your inbox contains 10 emails. "
            "For each email, classify it with the correct priority (urgent/normal/low) "
            "and category (work/personal/spam/newsletter/finance/support). "
            "Additionally, flag emails that are urgent or require action, and identify "
            "which emails need a reply. Accuracy of classification is scored."
        ),
        "emails": TASK1_EMAILS,
        "ground_truth": TASK1_GROUND_TRUTH,
        "max_steps": 40,
        "grader": "grade_task1",
    },
    "task_2": {
        "name": "Inbox Zero Challenge",
        "difficulty": "medium",
        "description": (
            "You have 20 emails waiting. Your goal is to achieve Inbox Zero by taking the "
            "correct action on every email: archive low-value messages, delete spam, flag "
            "urgent/action-required emails, and classify every email with priority and category. "
            "You must process all emails. Score is based on action correctness, classification "
            "accuracy, and coverage (% of emails processed)."
        ),
        "emails": TASK2_EMAILS,
        "ground_truth": TASK2_GROUND_TRUTH,
        "max_steps": 80,
        "grader": "grade_task2",
    },
    "task_3": {
        "name": "Executive Assistant Email Management",
        "difficulty": "hard",
        "description": (
            "You are the AI executive assistant to a CEO. You have 20 emails in the inbox. "
            "Your responsibilities: (1) identify and consolidate email threads, (2) detect and "
            "archive duplicate/FYI emails, (3) flag emails requiring CEO action with correct "
            "urgency, (4) identify emails requiring a drafted reply, (5) classify all emails "
            "by priority and category. Scoring is weighted: thread management (20%), duplicate "
            "detection (10%), action correctness (40%), reply identification (15%), "
            "classification accuracy (15%)."
        ),
        "emails": TASK3_EMAILS,
        "ground_truth": TASK3_GROUND_TRUTH,
        "max_steps": 100,
        "grader": "grade_task3",
    },
}


# ---------------------------------------------------------------------------
# Graders
# ---------------------------------------------------------------------------

def grade_task1(state_data: Dict[str, Any]) -> Dict[str, float]:
    """Score = weighted average of priority, category, flag, reply accuracy."""
    classifications: Dict[str, Dict] = state_data.get("classifications", {})
    flagged: Dict[str, str] = state_data.get("flagged", {})
    deleted: List[str] = state_data.get("deleted", [])
    archived: List[str] = state_data.get("archived", [])

    total = len(TASK1_GROUND_TRUTH)
    priority_hits = 0
    category_hits = 0
    flag_hits = 0
    reply_hits = 0

    for eid, gt in TASK1_GROUND_TRUTH.items():
        # Handle spam/delete: if ground truth is spam, deleting counts as correct category
        gt_cat = gt.category if isinstance(gt.category, str) else gt.category.value
        gt_pri = gt.priority if isinstance(gt.priority, str) else gt.priority.value

        if eid in classifications:
            pred = classifications[eid]
            pred_pri = pred.get("priority") or pred.get("priority", "")
            pred_cat = pred.get("category") or pred.get("category", "")

            if str(pred_pri) == gt_pri:
                priority_hits += 1
            if str(pred_cat) == gt_cat:
                category_hits += 1

            pred_reply = pred.get("requires_reply", False)
            if bool(pred_reply) == bool(gt.requires_reply):
                reply_hits += 1
        elif eid in deleted and gt_cat == "spam":
            # Deleting a spam email without classifying still shows good judgment
            category_hits += 1
            priority_hits += 1
            reply_hits += 1  # spam doesn't need reply

        # Flag scoring (EmailClassification uses field name 'flag', not 'flag_type')
        raw_flag = gt.flag if hasattr(gt, "flag") else gt.get("flag_type") if isinstance(gt, dict) else None
        gt_flag = raw_flag.value if raw_flag and hasattr(raw_flag, "value") else raw_flag
        pred_flag = flagged.get(eid)
        if gt_flag is None and pred_flag is None:
            flag_hits += 1
        elif gt_flag is not None and pred_flag is not None:
            flag_hits += 1  # partial credit for flagging (any flag)

    weights = {"priority": 0.30, "category": 0.35, "flag": 0.20, "reply": 0.15}
    score = (
        weights["priority"] * (priority_hits / total)
        + weights["category"] * (category_hits / total)
        + weights["flag"] * (flag_hits / total)
        + weights["reply"] * (reply_hits / total)
    )

    # Step efficiency bonus (up to 0.05 extra)
    steps_used = state_data.get("step_count", 40)
    max_steps = state_data.get("max_steps", 40)
    efficiency_bonus = max(0.0, 0.05 * (1 - steps_used / max_steps))
    score = min(1.0, score + efficiency_bonus)

    return {
        "total_score": round(score, 4),
        "priority_accuracy": round(priority_hits / total, 4),
        "category_accuracy": round(category_hits / total, 4),
        "flag_accuracy": round(flag_hits / total, 4),
        "reply_accuracy": round(reply_hits / total, 4),
        "efficiency_bonus": round(efficiency_bonus, 4),
    }


def grade_task2(state_data: Dict[str, Any]) -> Dict[str, float]:
    """Score = action correctness + classification accuracy + coverage."""
    classifications: Dict[str, Dict] = state_data.get("classifications", {})
    flagged: Dict[str, str] = state_data.get("flagged", {})
    archived: List[str] = state_data.get("archived", [])
    deleted: List[str] = state_data.get("deleted", [])

    total = len(TASK2_GROUND_TRUTH)
    action_hits = 0
    priority_hits = 0
    category_hits = 0
    processed = set()

    def inferred_action(eid: str) -> str:
        if eid in deleted:
            return "delete"
        if eid in archived:
            return "archive"
        if eid in flagged:
            return "flag"
        if eid in classifications:
            return "classify"
        return "none"

    for eid, gt in TASK2_GROUND_TRUTH.items():
        pred_action = inferred_action(eid)
        if pred_action != "none":
            processed.add(eid)
        if pred_action == gt["action"]:
            action_hits += 1

        gt_pri = gt["priority"]
        gt_cat = gt["category"]

        if eid in classifications:
            pred = classifications[eid]
            if str(pred.get("priority", "")) == gt_pri:
                priority_hits += 1
            if str(pred.get("category", "")) == gt_cat:
                category_hits += 1
        elif eid in deleted and gt_cat == "spam":
            priority_hits += 1
            category_hits += 1
        elif eid in archived and gt["action"] == "archive":
            # Archiving without explicit classify — give partial category credit
            pass

    coverage = len(processed) / total
    action_acc = action_hits / total
    priority_acc = priority_hits / total
    category_acc = category_hits / total

    weights = {"action": 0.40, "priority": 0.20, "category": 0.25, "coverage": 0.15}
    score = (
        weights["action"] * action_acc
        + weights["priority"] * priority_acc
        + weights["category"] * category_acc
        + weights["coverage"] * coverage
    )

    steps_used = state_data.get("step_count", 80)
    max_steps = state_data.get("max_steps", 80)
    efficiency_bonus = max(0.0, 0.03 * (1 - steps_used / max_steps))
    score = min(1.0, score + efficiency_bonus)

    return {
        "total_score": round(score, 4),
        "action_accuracy": round(action_acc, 4),
        "priority_accuracy": round(priority_acc, 4),
        "category_accuracy": round(category_acc, 4),
        "coverage": round(coverage, 4),
        "efficiency_bonus": round(efficiency_bonus, 4),
    }


def grade_task3(state_data: Dict[str, Any]) -> Dict[str, float]:
    """Multi-criteria grader for the hard task."""
    classifications: Dict[str, Dict] = state_data.get("classifications", {})
    flagged: Dict[str, str] = state_data.get("flagged", {})
    archived: List[str] = state_data.get("archived", [])
    deleted: List[str] = state_data.get("deleted", [])
    replies: Dict[str, str] = state_data.get("replies", {})

    total = len(TASK3_GROUND_TRUTH)

    def inferred_action(eid: str) -> str:
        if eid in deleted:
            return "delete"
        if eid in archived:
            return "archive"
        if eid in flagged:
            return "flag"
        return "none"

    # 1. Thread management: emails in same thread_id should be grouped/handled consistently
    threads: Dict[str, List[str]] = {}
    for eid, gt in TASK3_GROUND_TRUTH.items():
        tid = gt.get("thread_id")
        if tid:
            threads.setdefault(tid, []).append(eid)

    thread_score = 0.0
    thread_total = 0
    for tid, eids in threads.items():
        for eid in eids:
            gt = TASK3_GROUND_TRUTH[eid]
            action = inferred_action(eid)
            if action == gt["action"]:
                thread_score += 1
            thread_total += 1
    thread_score = (thread_score / thread_total) if thread_total > 0 else 0.0

    # 2. Duplicate detection: h04 and h20 are duplicates — should be archived
    duplicates = [eid for eid, gt in TASK3_GROUND_TRUTH.items() if gt.get("is_duplicate")]
    dup_hits = sum(1 for eid in duplicates if eid in archived)
    dup_score = dup_hits / len(duplicates) if duplicates else 0.0

    # 3. Action correctness
    action_hits = 0
    priority_hits = 0
    category_hits = 0
    reply_hits = 0

    for eid, gt in TASK3_GROUND_TRUTH.items():
        action = inferred_action(eid)
        if action == gt["action"]:
            action_hits += 1

        if eid in classifications:
            pred = classifications[eid]
            if str(pred.get("priority", "")) == gt["priority"]:
                priority_hits += 1
            if str(pred.get("category", "")) == gt["category"]:
                category_hits += 1
        elif eid in deleted and gt["category"] == "spam":
            priority_hits += 1
            category_hits += 1

        # Reply identification: email has a reply drafted
        if gt.get("requires_reply"):
            if eid in replies and len(replies[eid].strip()) > 10:
                reply_hits += 1

    reply_needed = sum(1 for gt in TASK3_GROUND_TRUTH.values() if gt.get("requires_reply"))
    reply_score = reply_hits / reply_needed if reply_needed > 0 else 1.0
    action_acc = action_hits / total
    class_acc = (priority_hits + category_hits) / (2 * total)

    weights = {
        "thread":   0.20,
        "dup":      0.10,
        "action":   0.40,
        "reply":    0.15,
        "classify": 0.15,
    }
    score = (
        weights["thread"]   * thread_score
        + weights["dup"]    * dup_score
        + weights["action"] * action_acc
        + weights["reply"]  * reply_score
        + weights["classify"] * class_acc
    )

    steps_used = state_data.get("step_count", 100)
    max_steps = state_data.get("max_steps", 100)
    efficiency_bonus = max(0.0, 0.02 * (1 - steps_used / max_steps))
    score = min(1.0, score + efficiency_bonus)

    return {
        "total_score": round(score, 4),
        "thread_management": round(thread_score, 4),
        "duplicate_detection": round(dup_score, 4),
        "action_accuracy": round(action_acc, 4),
        "reply_identification": round(reply_score, 4),
        "classification_accuracy": round(class_acc, 4),
        "efficiency_bonus": round(efficiency_bonus, 4),
    }


def run_grader(task_id: str, state_data: Dict[str, Any]) -> Dict[str, float]:
    graders = {
        "task_1": grade_task1,
        "task_2": grade_task2,
        "task_3": grade_task3,
    }
    if task_id not in graders:
        raise ValueError(f"Unknown task_id: {task_id}")
    return graders[task_id](state_data)
