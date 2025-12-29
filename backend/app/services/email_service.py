"""
Email Marketing Service
Email campaigns, newsletters, and automated sequences
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class EmailTemplate(BaseModel):
    """Email template model"""
    name: str
    subject: str
    html_content: str
    text_content: str
    variables: List[str] = []


class EmailCampaign(BaseModel):
    """Email campaign model"""
    name: str
    template_name: str
    segment: str  # all, free, premium, inactive
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, sending, sent, failed


class EmailService:
    """Service for sending emails and managing campaigns"""
    
    def __init__(self, db):
        self.db = db
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@german-ai.com")
        self.from_name = os.getenv("FROM_NAME", "German AI")
        
        # Email templates
        self.templates = {
            "welcome": EmailTemplate(
                name="welcome",
                subject="Welcome to German AI! 🎉",
                html_content=self._get_welcome_template(),
                text_content="Welcome to German AI! Start your German learning journey today.",
                variables=["name", "signup_date"]
            ),
            "trial_ending": EmailTemplate(
                name="trial_ending",
                subject="Your trial is ending soon ⏰",
                html_content=self._get_trial_ending_template(),
                text_content="Your trial is ending in 3 days. Upgrade to continue learning!",
                variables=["name", "trial_end_date"]
            ),
            "subscription_confirmed": EmailTemplate(
                name="subscription_confirmed",
                subject="Subscription Confirmed! 🎊",
                html_content=self._get_subscription_confirmed_template(),
                text_content="Your subscription has been confirmed. Thank you!",
                variables=["name", "tier", "amount"]
            ),
            "re_engagement": EmailTemplate(
                name="re_engagement",
                subject="We miss you! Come back to German AI 💙",
                html_content=self._get_re_engagement_template(),
                text_content="We noticed you haven't been active. Come back and continue learning!",
                variables=["name", "last_active_date"]
            ),
            "achievement_unlocked": EmailTemplate(
                name="achievement_unlocked",
                subject="🏆 New Achievement Unlocked!",
                html_content=self._get_achievement_template(),
                text_content="Congratulations! You've unlocked a new achievement.",
                variables=["name", "achievement_name", "achievement_description"]
            ),
            "weekly_progress": EmailTemplate(
                name="weekly_progress",
                subject="Your Weekly Progress Report 📊",
                html_content=self._get_weekly_progress_template(),
                text_content="Here's your weekly progress summary.",
                variables=["name", "scenarios_completed", "words_learned", "streak"]
            ),
            "referral_reward": EmailTemplate(
                name="referral_reward",
                subject="🎁 Referral Reward Earned!",
                html_content=self._get_referral_reward_template(),
                text_content="You've earned a referral reward!",
                variables=["name", "reward_value", "referred_name"]
            )
        }
    
    def _get_welcome_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #3B82F6;">Welcome to German AI! 🎉</h1>
            <p>Hi {{name}},</p>
            <p>We're thrilled to have you join our community of German learners!</p>
            <p>Here's what you can do to get started:</p>
            <ul>
                <li>Complete your first scenario</li>
                <li>Practice with AI conversations</li>
                <li>Learn new vocabulary</li>
                <li>Track your progress</li>
            </ul>
            <a href="https://german-ai.com/scenarios" style="background-color: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                Start Learning
            </a>
            <p>Happy learning!<br>The German AI Team</p>
        </body>
        </html>
        """
    
    def _get_trial_ending_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #F59E0B;">Your Trial is Ending Soon ⏰</h1>
            <p>Hi {{name}},</p>
            <p>Your trial period ends on {{trial_end_date}}.</p>
            <p>Don't lose access to:</p>
            <ul>
                <li>Unlimited AI conversations</li>
                <li>All premium scenarios</li>
                <li>Advanced grammar checking</li>
                <li>Progress tracking</li>
            </ul>
            <a href="https://german-ai.com/pricing" style="background-color: #F59E0B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                Upgrade Now
            </a>
        </body>
        </html>
        """
    
    def _get_subscription_confirmed_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #10B981;">Subscription Confirmed! 🎊</h1>
            <p>Hi {{name}},</p>
            <p>Your {{tier}} subscription has been confirmed.</p>
            <p>Amount: ${{amount}}</p>
            <p>You now have access to all premium features!</p>
            <a href="https://german-ai.com/dashboard" style="background-color: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                Go to Dashboard
            </a>
        </body>
        </html>
        """
    
    def _get_re_engagement_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #8B5CF6;">We Miss You! 💙</h1>
            <p>Hi {{name}},</p>
            <p>We noticed you haven't been active since {{last_active_date}}.</p>
            <p>Come back and continue your German learning journey!</p>
            <p>New features added:</p>
            <ul>
                <li>5 new scenarios</li>
                <li>Improved AI responses</li>
                <li>New achievements</li>
            </ul>
            <a href="https://german-ai.com/login" style="background-color: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                Continue Learning
            </a>
        </body>
        </html>
        """
    
    def _get_achievement_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #F59E0B;">🏆 Achievement Unlocked!</h1>
            <p>Hi {{name}},</p>
            <p>Congratulations! You've unlocked:</p>
            <h2 style="color: #3B82F6;">{{achievement_name}}</h2>
            <p>{{achievement_description}}</p>
            <a href="https://german-ai.com/achievements" style="background-color: #F59E0B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                View All Achievements
            </a>
        </body>
        </html>
        """
    
    def _get_weekly_progress_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #3B82F6;">Your Weekly Progress 📊</h1>
            <p>Hi {{name}},</p>
            <p>Here's what you accomplished this week:</p>
            <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Scenarios Completed:</strong> {{scenarios_completed}}</p>
                <p><strong>Words Learned:</strong> {{words_learned}}</p>
                <p><strong>Current Streak:</strong> {{streak}} days 🔥</p>
            </div>
            <p>Keep up the great work!</p>
            <a href="https://german-ai.com/dashboard" style="background-color: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                View Full Stats
            </a>
        </body>
        </html>
        """
    
    def _get_referral_reward_template(self) -> str:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #10B981;">🎁 Referral Reward Earned!</h1>
            <p>Hi {{name}},</p>
            <p>Great news! {{referred_name}} just signed up using your referral code.</p>
            <p>You've earned: <strong>{{reward_value}} days of premium</strong></p>
            <a href="https://german-ai.com/referrals" style="background-color: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">
                Claim Reward
            </a>
            <p>Share your referral code with more friends to earn more rewards!</p>
        </body>
        </html>
        """
    
    async def send_email(
        self,
        to_email: str,
        template_name: str,
        variables: Dict[str, Any]
    ) -> bool:
        """Send an email using a template"""
        try:
            template = self.templates.get(template_name)
            if not template:
                raise Exception(f"Template {template_name} not found")
            
            # Replace variables in content
            html_content = template.html_content
            text_content = template.text_content
            subject = template.subject
            
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                html_content = html_content.replace(placeholder, str(value))
                text_content = text_content.replace(placeholder, str(value))
                subject = subject.replace(placeholder, str(value))
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # Attach parts
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email (mock in development)
            if os.getenv("ENVIRONMENT") == "production" and self.smtp_user:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                # Log email in development
                print(f"[EMAIL] To: {to_email}, Subject: {subject}")
            
            # Log email sent
            await self.db["email_logs"].insert_one({
                "to_email": to_email,
                "template_name": template_name,
                "subject": subject,
                "sent_at": datetime.utcnow(),
                "status": "sent"
            })
            
            return True
        
        except Exception as e:
            # Log error
            await self.db["email_logs"].insert_one({
                "to_email": to_email,
                "template_name": template_name,
                "sent_at": datetime.utcnow(),
                "status": "failed",
                "error": str(e)
            })
            return False
    
    async def send_welcome_email(self, user_id: str):
        """Send welcome email to new user"""
        user = await self.db["users"].find_one({"_id": user_id})
        if not user:
            return
        
        await self.send_email(
            to_email=user["email"],
            template_name="welcome",
            variables={
                "name": user.get("name", "there"),
                "signup_date": datetime.utcnow().strftime("%B %d, %Y")
            }
        )
    
    async def send_trial_ending_emails(self):
        """Send trial ending emails (run daily)"""
        # Find users whose trial ends in 3 days
        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        
        subscriptions = await self.db["subscriptions"].find({
            "status": "trialing",
            "trial_end": {
                "$gte": three_days_from_now,
                "$lt": three_days_from_now + timedelta(days=1)
            }
        }).to_list(length=1000)
        
        for subscription in subscriptions:
            user = await self.db["users"].find_one({"_id": subscription["user_id"]})
            if user:
                await self.send_email(
                    to_email=user["email"],
                    template_name="trial_ending",
                    variables={
                        "name": user.get("name", "there"),
                        "trial_end_date": subscription["trial_end"].strftime("%B %d, %Y")
                    }
                )
    
    async def send_re_engagement_emails(self):
        """Send re-engagement emails to inactive users (run weekly)"""
        # Find users inactive for 7+ days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        inactive_users = await self.db["users"].find({
            "last_active": {"$lt": seven_days_ago}
        }).to_list(length=1000)
        
        for user in inactive_users:
            # Check if we already sent re-engagement email recently
            recent_email = await self.db["email_logs"].find_one({
                "to_email": user["email"],
                "template_name": "re_engagement",
                "sent_at": {"$gte": datetime.utcnow() - timedelta(days=14)}
            })
            
            if not recent_email:
                await self.send_email(
                    to_email=user["email"],
                    template_name="re_engagement",
                    variables={
                        "name": user.get("name", "there"),
                        "last_active_date": user.get("last_active", datetime.utcnow()).strftime("%B %d, %Y")
                    }
                )
    
    async def send_weekly_progress_emails(self):
        """Send weekly progress emails (run weekly)"""
        # Get all active users
        users = await self.db["users"].find({
            "last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}
        }).to_list(length=10000)
        
        for user in users:
            # Get user stats
            stats = await self.db["user_stats"].find_one({"user_id": str(user["_id"])})
            if stats:
                await self.send_email(
                    to_email=user["email"],
                    template_name="weekly_progress",
                    variables={
                        "name": user.get("name", "there"),
                        "scenarios_completed": stats.get("scenarios_completed", 0),
                        "words_learned": stats.get("words_learned", 0),
                        "streak": stats.get("current_streak", 0)
                    }
                )
