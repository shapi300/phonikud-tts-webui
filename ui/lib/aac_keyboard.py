"""AAC (Augmentative & Alternative Communication) Hebrew Predictive Keyboard."""

import gradio as gr
import json
import os
from typing import List, Tuple, Optional

# Common Hebrew words organized by category and frequency
# Male version
HEBREW_WORDS_MALE = {
    # Pronouns - male
    "pronouns": [
        "אני", "אתה", "הוא", "אנחנו", "אתם", "הם", 
        "זה", "אלה", "הזה", "שלי", "שלך", "שלו", "שלנו", "שלכם", "שלהם"
    ],
    # Common verbs
    "verbs": [
        "רוצה", "צריך", "יכול", "אוהב", "יודע", "הולך", "בא", "אוכל", "שותה", "ישן", 
        "קם", "יושב", "עושה", "אומר", "רואה", "שומע", "חושב", "מרגיש", "נותן", "לוקח",
        "עובד", "לומד", "משחק", "רץ", "הולך", "חוזר", "נכנס", "יוצא", "מחכה", "מבין"
    ],
    # Questions
    "questions": [
        "מה", "מי", "איפה", "מתי", "למה", "איך", "כמה", "איזה", "האם", "איזה",
        "לאן", "מאיפה", "כמה זמן", "מה זה", "מי זה"
    ],
    # Yes/No/Basic
    "basic": [
        "כן", "לא", "אולי", "טוב", "רע", "בסדר", "מצוין", "נהדר", "בבקשה", "תודה",
        "סליחה", "חבל", "יפה", "נכון", "לא נכון", "חשוב", "מעניין", "קל", "קשה"
    ],
    # Food & Drink
    "food": [
        "מים", "אוכל", "לחם", "חלב", "קפה", "תה", "פירות", "ירקות", "בשר", "עוף",
        "דג", "גבינה", "ביצה", "אורז", "פסטה", "פיצה", "המבורגר", "סלט", "מרק",
        "עוגה", "עוגייה", "גלידה", "שוקולד", "מיץ", "בירה", "יין", "סוכר", "מלח"
    ],
    # Feelings
    "feelings": [
        "שמח", "עצוב", "כועס", "עייף", "רעב", "צמא", "חולה", "פוחד", "רגוע", "לחוץ",
        "נרגש", "מאושר", "מודאג", "עצבני", "בודד", "אהבה", "שנאה", "תקווה", "גאווה", "בושה"
    ],
    # Actions
    "actions": [
        "לאכול", "לשתות", "ללכת", "לישון", "לקרוא", "לכתוב", "לראות", "לשחק", "לדבר", "לשמוע",
        "לעזור", "לחכות", "לרוץ", "לשיר", "לרקוד", "לצחוק", "לבכות", "לחבק", "לנשק", "ללמוד",
        "ללמד", "לעבוד", "לנסוע", "לטוס", "לשחות", "לבשל", "לנקות", "לקנות", "למכור"
    ],
    # Places
    "places": [
        "בית", "בית ספר", "עבודה", "חנות", "מסעדה", "פארק", "בית חולים", "רופא", "שירותים",
        "מטבח", "חדר", "מיטה", "רחוב", "עיר", "כפר", "ים", "חוף", "הר", "יער", "גינה",
        "ספרייה", "בנק", "דואר", "תחנה", "שוק", "קניון", "בית קפה", "מכון כושר"
    ],
    # Time
    "time": [
        "עכשיו", "מאוחר", "מוקדם", "היום", "מחר", "אתמול", "בוקר", "צהריים", "ערב", "לילה",
        "שבוע", "חודש", "שנה", "יום", "שעה", "דקה", "שנייה", "תמיד", "לפעמים", "לעולם",
        "כבר", "עדיין", "אחרי", "לפני", "בקרוב", "מאוחר יותר"
    ],
    # People
    "people": [
        "אמא", "אבא", "אח", "אחות", "בן", "בת", "חבר", "חברה", "מורה", "רופא", "משפחה",
        "סבא", "סבתא", "דוד", "דודה", "בן דוד", "בת דודה", "שכן", "שכנה", "ילד", "ילדה",
        "תינוק", "מבוגר", "זקן", "איש", "אישה", "בעל", "אישה", "חברים"
    ],
    # Common adjectives
    "adjectives": [
        "גדול", "קטן", "טוב", "רע", "יפה", "מכוער", "חדש", "ישן", "חם", "קר",
        "מהיר", "איטי", "חזק", "חלש", "עשיר", "עני", "שמח", "עצוב", "כבד", "קל",
        "ארוך", "קצר", "רחב", "צר", "גבוה", "נמוך", "רעשן", "שקט", "נקי", "מלוכלך"
    ],
    # Requests
    "requests": [
        "בבקשה", "תודה", "סליחה", "עזרה", "רגע", "חכה", "בוא", "לך", "תן לי", "קח",
        "הבא", "הביאי", "שמור", "זהירות", "אל תעשה", "תעשה", "תחכה", "תחזור", "תבוא"
    ],
    # Body parts
    "body": [
        "יד", "רגל", "ראש", "עין", "אוזן", "פה", "אף", "שיניים", "לשון", "גב",
        "בטן", "לב", "מוח", "עצם", "עור", "שיער", "צוואר", "כתף", "ברך"
    ],
    # Weather
    "weather": [
        "שמש", "גשם", "שלג", "רוח", "ענן", "סערה", "חם", "קר", "קריר", "חמים",
        "לח", "יבש", "בהיר", "מעונן"
    ],
    # Numbers
    "numbers": [
        "אחד", "שניים", "שלושה", "ארבעה", "חמישה", "שישה", "שבעה", "שמונה", "תשעה", "עשרה",
        "מאה", "אלף", "מיליון", "ראשון", "שני", "אחרון"
    ],
    # Colors
    "colors": [
        "אדום", "כחול", "ירוק", "צהוב", "לבן", "שחור", "כתום", "סגול", "ורוד", "חום",
        "אפור", "תכלת", "זהב", "כסף"
    ],
    # Daily activities
    "daily": [
        "לקום", "להתלבש", "להתקלח", "לצחצח שיניים", "לסרק", "לאכול ארוחת בוקר", 
        "לצאת", "לחזור הביתה", "לישון", "לנוח", "לראות טלוויזיה", "לגלוש באינטרנט"
    ],
    # Finance & Banking
    "finance": [
        "כסף", "בנק", "חשבון", "כרטיס", "מזומן", "אשראי", "העברה", "המחאה", 
        "יתרה", "פיקדון", "הלוואה", "חסכון", "בנקומט", "משיכה", "הפקדה", "עמלה"
    ],
    # Shopping & Supermarket
    "shopping": [
        "קניות", "סל", "מחיר", "הנחה", "קבלה", "תשלום", "חשבונית", "עגלה", 
        "מדף", "מבצע", "רשימה", "שקית", "קופה", "פקח", "החזר", "תוית"
    ],
    # Medical & Health
    "medical": [
        "רופא", "תרופה", "בית חולים", "בדיקה", "כאב", "חום", "מרשם", "אמבולנס", 
        "ביטוח", "מרפאה", "אחות", "טיפול", "זריקה", "כדור", "רוקח", "מרפא"
    ],
    # Transportation
    "transportation": [
        "אוטובוס", "רכבת", "מונית", "רכב", "תחנה", "כרטיס", "נסיעה", "נהג", 
        "כביש", "רחוב", "שביל", "חניה", "אופניים", "הולך רגל", "רמזור", "מעבר"
    ],
    # Home & Utilities
    "home": [
        "חשמל", "מים", "גז", "טלפון", "אינטרנט", "טלוויזיה", "מזגן", "חימום", 
        "מפתח", "דלת", "חלון", "מנורה", "שקע", "מפסק", "חשבון", "תשלום"
    ],
    # Communication
    "communication": [
        "טלפון", "הודעה", "מייל", "וואטסאפ", "שיחה", "צלצל", "התקשר", "ענה", 
        "כתוב", "קרא", "שלח", "קבל", "סמס", "וידאו", "תמונה", "קול"
    ],
    # Clothing
    "clothing": [
        "בגד", "חולצה", "מכנסיים", "שמלה", "נעליים", "סנדל", "גרביים", "תחתונים", 
        "חזייה", "כובע", "מעיל", "ז'קט", "סוודר", "בגד ים", "פיג'מה", "חגורה"
    ],
    # Family & Relations
    "family": [
        "משפחה", "אמא", "אבא", "אח", "אחות", "סבא", "סבתא", "דוד", 
        "דודה", "בן דוד", "בת דודה", "נכד", "נכדה", "חתן", "כלה", "זוג"
    ],
    # Work & Office
    "work": [
        "עבודה", "פגישה", "מייל", "מחשב", "דדליין", "בוס", "קולגה", "לקוח", 
        "פרויקט", "משימה", "דוח", "הצגה", "משרד", "צוות", "מנהל", "עובד"
    ],
    # Technology
    "technology": [
        "טלפון", "מחשב", "נטען", "וויפי", "סיסמה", "אפליקציה", "מסך", "מקלדת", 
        "עכבר", "תיקון", "סוללה", "זיכרון", "קובץ", "תיקייה", "הדפסה", "סריקה"
    ],
    # Social & Entertainment
    "entertainment": [
        "סרט", "מוזיקה", "משחק", "חבר", "מסיבה", "מסעדה", "בר", "טיול", 
        "חופשה", "הופעה", "תיאטרון", "ספר", "ספורט", "כדורגל", "כדורסל", "חוף"
    ],
    # Emergency
    "emergency": [
        "עזרה!", "משטרה", "אמבולנס", "אש", "חירום", "מהר", "תקשר לעזרה", "רופא עכשיו", 
        "לא טוב", "כואב מאוד", "צלצל", "בבקשה תעזור", "מסוכן", "תיזהר", "דלת", "מפתח"
    ],
    # Context Questions
    "context_questions": [
        "איפה זה?", "כמה זה עולה?", "מתי זה מתחיל?", "למה לא?", "איך עושים?", "מי זה היה?",
        "מה קורה?", "איפה ה...?", "מתי נגמר?", "לאן הולכים?", "מאיפה מביאים?", "כמה זמן?",
        "זה בסדר?", "אפשר לעזור?", "מה השעה?", "איפה השירותים?"
    ],
}

# Quick phrases for common communication
QUICK_PHRASES = [
    "שלום",
    "תודה",
    "בבקשה",
    "סליחה",
    "כן",
    "לא",
    "עזרה",
    "אני רוצה",
    "אני צריך",
    "מה קורה",
    "בסדר",
    "לא בסדר",
]

# Ready Answers - complete phrases for typical day-to-day communication
# Organized by category for easy access
READY_ANSWERS = {
    # Greetings & Polite
    "greetings": [
        "שלום!",
        "בוקר טוב!",
        "צהריים טובים!",
        "ערב טוב!",
        "לילה טוב!",
        "מה נשמע?",
        "איך אתה?",
        "איך את?",
        "נעים להכיר",
        "להתראות!",
        "יום טוב!",
        "סוף שבוע נעים",
    ],
    # Responses & Acknowledgments
    "responses": [
        "כן, בבקשה",
        "לא, תודה",
        "בסדר גמור",
        "בטח!",
        "אולי",
        "אני מסכים",
        "אני לא מסכים",
        "תודה רבה!",
        "תודה על העזרה",
        "סליחה, לא הבנתי",
        "רגע בבקשה",
        "אני חושב על זה",
        "זה בסדר",
        "לא נורא",
        "מצוין!",
        "נהדר!",
    ],
    # Requests for Help
    "help_requests": [
        "אפשר לקבל עזרה?",
        "תוכל לעזור לי?",
        "תוכלי לעזור לי?",
        "אני צריך עזרה",
        "אני לא מצליח",
        "זה לא עובד",
        "איך עושים את זה?",
        "תסביר לי בבקשה",
        "אפשר לשאול שאלה?",
        "יש לי בעיה",
        "משהו לא בסדר",
        "אני צריך משהו",
    ],
    # Needs & Wants
    "needs": [
        "אני רוצה לשתות",
        "אני רוצה לאכול",
        "אני צמא",
        "אני רעב",
        "אני צריך מים",
        "אני רוצה קפה",
        "אני רוצה תה",
        "אני צריך לנוח",
        "אני עייף",
        "אני רוצה לישון",
        "אני רוצה לצאת",
        "אני רוצה ללכת הביתה",
    ],
    # Feelings & State
    "feelings_state": [
        "טוב לי",
        "לא טוב לי",
        "אני שמח",
        "אני עצוב",
        "אני כועס",
        "אני עייף מאוד",
        "אני לחוץ",
        "אני דואג",
        "אני פוחד",
        "אני רגוע",
        "כואב לי",
        "אני חולה",
        "אני מרגיש טוב",
        "אני מרגיש לא טוב",
    ],
    # Questions
    "common_questions": [
        "מה השעה?",
        "איפה השירותים?",
        "מתי זה מתחיל?",
        "מתי זה נגמר?",
        "כמה זה עולה?",
        "איפה זה נמצא?",
        "לאן הולכים?",
        "מי זה?",
        "מה זה?",
        "למה?",
        "איך מגיעים ל...?",
        "כמה זמן זה לוקח?",
    ],
    # Social & Conversations
    "social": [
        "מה אתה חושב?",
        "מה דעתך?",
        "אני מסכים איתך",
        "יפה אמרת",
        "זה נכון",
        "זה לא נכון",
        "ספר לי עוד",
        "מעניין!",
        "מצחיק!",
        "חבל",
        "נכון מאוד",
        "אני מבין",
    ],
    # Places & Directions
    "places": [
        "אני רוצה ללכת ל...",
        "איפה היציאה?",
        "איפה הכניסה?",
        "אני צריך להגיע ל...",
        "איך מגיעים לשם?",
        "זה רחוק?",
        "אני הולך לשירותים",
        "אני חוזר עכשיו",
        "תחכה לי רגע",
        "אני יוצא החוצה",
    ],
    # Daily Activities
    "daily": [
        "אני רוצה לראות טלוויזיה",
        "אני רוצה לשחק",
        "אני רוצה לקרוא",
        "אני רוצה לשמוע מוזיקה",
        "אני רוצה לגלוש באינטרנט",
        "אני רוצה לדבר עם...",
        "תתקשר לי ל...",
        "אני רוצה ללמוד",
        "אני רוצה לעבוד",
        "אני רוצה לנוח",
    ],
    # Food & Meals
    "food": [
        "בתיאבון!",
        "היה טעים",
        "תודה על האוכל",
        "אני רוצה עוד",
        "אני שבע",
        "זה טעים!",
        "זה לא טעים",
        "אני לא אוהב את זה",
        "מה יש לאכול?",
        "מתי האוכל?",
        "אני רוצה משהו מתוק",
        "אני רוצה שתייה קרה",
    ],
    # Medical & Emergency
    "medical": [
        "אני לא מרגיש טוב",
        "כואב לי פה",
        "אני צריך רופא",
        "תביאו לי תרופה",
        "אני צריך לשכב",
        "תקראו לעזרה",
        "זה מכאיב לי",
        "אני מרגיש חולשה",
        "אני צריך מנוחה",
        "תביאו לי מים",
    ],
    # Weather & Temperature
    "weather": [
        "חם לי",
        "קר לי",
        "נעים פה",
        "אני רוצה מזגן",
        "אני רוצה חימום",
        "פתחו חלון",
        "סגרו חלון",
        "מה מזג האוויר?",
        "יש שמש?",
        "ירד גשם?",
    ],
    # Phone & Communication
    "communication": [
        "תתקשר לי",
        "שלח לי הודעה",
        "אני רוצה לדבר בטלפון",
        "תענה לטלפון",
        "מי צלצל?",
        "יש לי הודעה?",
        "תשלח וואטסאפ",
        "אני רוצה לשלוח תמונה",
        "תצלם אותי",
        "אני רוצה לראות וידאו",
    ],
    # Shopping & Money
    "shopping": [
        "כמה זה?",
        "זה יקר מדי",
        "בבקשה קבלה",
        "אני רוצה לקנות",
        "יש הנחה?",
        "אני משלם במזומן",
        "אני משלם באשראי",
        "איפה הקופה?",
        "תעטוף לי את זה",
        "תודה, לא צריך",
    ],
    # Work & Tasks
    "work": [
        "יש לי פגישה",
        "אני עסוק",
        "תזכיר לי",
        "אני צריך לסיים",
        "מתי ההפסקה?",
        "אני גמרתי",
        "זה מוכן",
        "עוד רגע",
        "אני באמצע",
        "תחכה שאסיים",
    ],
}

# Ready Answers in female form
READY_ANSWERS_FEMALE = {
    # Greetings & Polite (same)
    "greetings": [
        "שלום!",
        "בוקר טוב!",
        "צהריים טובים!",
        "ערב טוב!",
        "לילה טוב!",
        "מה נשמע?",
        "איך אתה?",
        "איך את?",
        "נעים להכיר",
        "להתראות!",
        "יום טוב!",
        "סוף שבוע נעים",
    ],
    # Responses & Acknowledgments (same)
    "responses": [
        "כן, בבקשה",
        "לא, תודה",
        "בסדר גמור",
        "בטח!",
        "אולי",
        "אני מסכימה",
        "אני לא מסכימה",
        "תודה רבה!",
        "תודה על העזרה",
        "סליחה, לא הבנתי",
        "רגע בבקשה",
        "אני חושבת על זה",
        "זה בסדר",
        "לא נורא",
        "מצוין!",
        "נהדר!",
    ],
    # Requests for Help (female)
    "help_requests": [
        "אפשר לקבל עזרה?",
        "תוכל לעזור לי?",
        "תוכלי לעזור לי?",
        "אני צריכה עזרה",
        "אני לא מצליחה",
        "זה לא עובד",
        "איך עושים את זה?",
        "תסביר לי בבקשה",
        "אפשר לשאול שאלה?",
        "יש לי בעיה",
        "משהו לא בסדר",
        "אני צריכה משהו",
    ],
    # Needs & Wants (female)
    "needs": [
        "אני רוצה לשתות",
        "אני רוצה לאכול",
        "אני צמאה",
        "אני רעבה",
        "אני צריכה מים",
        "אני רוצה קפה",
        "אני רוצה תה",
        "אני צריכה לנוח",
        "אני עייפה",
        "אני רוצה לישון",
        "אני רוצה לצאת",
        "אני רוצה ללכת הביתה",
    ],
    # Feelings & State (female)
    "feelings_state": [
        "טוב לי",
        "לא טוב לי",
        "אני שמחה",
        "אני עצובה",
        "אני כועסת",
        "אני עייפה מאוד",
        "אני לחוצה",
        "אני דואגת",
        "אני פוחדת",
        "אני רגועה",
        "כואב לי",
        "אני חולה",
        "אני מרגישה טוב",
        "אני מרגישה לא טוב",
    ],
    # Questions (same)
    "common_questions": [
        "מה השעה?",
        "איפה השירותים?",
        "מתי זה מתחיל?",
        "מתי זה נגמר?",
        "כמה זה עולה?",
        "איפה זה נמצא?",
        "לאן הולכים?",
        "מי זה?",
        "מה זה?",
        "למה?",
        "איך מגיעים ל...?",
        "כמה זמן זה לוקח?",
    ],
    # Social & Conversations (female)
    "social": [
        "מה אתה חושב?",
        "מה דעתך?",
        "אני מסכימה איתך",
        "יפה אמרת",
        "זה נכון",
        "זה לא נכון",
        "ספר לי עוד",
        "מעניין!",
        "מצחיק!",
        "חבל",
        "נכון מאוד",
        "אני מבינה",
    ],
    # Places & Directions (female)
    "places": [
        "אני רוצה ללכת ל...",
        "איפה היציאה?",
        "איפה הכניסה?",
        "אני צריכה להגיע ל...",
        "איך מגיעים לשם?",
        "זה רחוק?",
        "אני הולכת לשירותים",
        "אני חוזרת עכשיו",
        "תחכי לי רגע",
        "אני יוצאת החוצה",
    ],
    # Daily Activities (same)
    "daily": [
        "אני רוצה לראות טלוויזיה",
        "אני רוצה לשחק",
        "אני רוצה לקרוא",
        "אני רוצה לשמוע מוזיקה",
        "אני רוצה לגלוש באינטרנט",
        "אני רוצה לדבר עם...",
        "תתקשרי לי ל...",
        "אני רוצה ללמוד",
        "אני רוצה לעבוד",
        "אני רוצה לנוח",
    ],
    # Food & Meals (same)
    "food": [
        "בתיאבון!",
        "היה טעים",
        "תודה על האוכל",
        "אני רוצה עוד",
        "אני שבעה",
        "זה טעים!",
        "זה לא טעים",
        "אני לא אוהבת את זה",
        "מה יש לאכול?",
        "מתי האוכל?",
        "אני רוצה משהו מתוק",
        "אני רוצה שתייה קרה",
    ],
    # Medical & Emergency (female)
    "medical": [
        "אני לא מרגישה טוב",
        "כואב לי פה",
        "אני צריכה רופא",
        "תביאו לי תרופה",
        "אני צריכה לשכב",
        "תקראו לעזרה",
        "זה מכאיב לי",
        "אני מרגישה חולשה",
        "אני צריכה מנוחה",
        "תביאו לי מים",
    ],
    # Weather & Temperature (same)
    "weather": [
        "חם לי",
        "קר לי",
        "נעים פה",
        "אני רוצה מזגן",
        "אני רוצה חימום",
        "פתחו חלון",
        "סגרו חלון",
        "מה מזג האוויר?",
        "יש שמש?",
        "ירד גשם?",
    ],
    # Phone & Communication (same)
    "communication": [
        "תתקשרי לי",
        "שלחי לי הודעה",
        "אני רוצה לדבר בטלפון",
        "תעני לטלפון",
        "מי צלצל?",
        "יש לי הודעה?",
        "תשלחי וואטסאפ",
        "אני רוצה לשלוח תמונה",
        "תצלמי אותי",
        "אני רוצה לראות וידאו",
    ],
    # Shopping & Money (same)
    "shopping": [
        "כמה זה?",
        "זה יקר מדי",
        "בבקשה קבלה",
        "אני רוצה לקנות",
        "יש הנחה?",
        "אני משלמת במזומן",
        "אני משלמת באשראי",
        "איפה הקופה?",
        "תעטפי לי את זה",
        "תודה, לא צריך",
    ],
    # Work & Tasks (female)
    "work": [
        "יש לי פגישה",
        "אני עסוקה",
        "תזכירי לי",
        "אני צריכה לסיים",
        "מתי ההפסקה?",
        "אני גמרתי",
        "זה מוכן",
        "עוד רגע",
        "אני באמצע",
        "תחכי שאסיים",
    ],
}

def get_ready_answers_for_gender(gender: str) -> dict:
    """Get the appropriate ready answers set for the specified gender."""
    if gender == "female":
        return READY_ANSWERS_FEMALE
    return READY_ANSWERS

# Ready answer category labels for UI
READY_ANSWER_CATEGORIES = {
    "greetings": "👋 ברכות",
    "responses": "✅ תגובות",
    "help_requests": "🆘 בקשת עזרה",
    "needs": "🍽️ צרכים",
    "feelings_state": "❤️ הרגשות",
    "common_questions": "❓ שאלות",
    "social": "👥 חברה",
    "places": "📍 מקומות",
    "daily": "📅 יומיום",
    "food": "🍴 אוכל",
    "medical": "🏥 רפואי",
    "weather": "🌤️ מזג אוויר",
    "communication": "📞 תקשורת",
    "shopping": "🛒 קניות",
    "work": "💼 עבודה",
}

# Female version - Hebrew words with feminine grammar
HEBREW_WORDS_FEMALE = {
    # Pronouns - female
    "pronouns": [
        "אני", "את", "היא", "אנחנו", "אתן", "הן", 
        "זאת", "אלה", "הזאת", "שלי", "שלך", "שלה", "שלנו", "שלכן", "שלהן"
    ],
    # Common verbs - female
    "verbs": [
        "רוצה", "צריכה", "יכולה", "אוהבת", "יודעת", "הולכת", "באה", "אוכלת", "שותה", "ישנה", 
        "קמה", "יושבת", "עושה", "אומרת", "רואה", "שומעת", "חושבת", "מרגישה", "נותנת", "לוקחת",
        "עובדת", "לומדת", "משחקת", "רצה", "הולכת", "חוזרת", "נכנסת", "יוצאת", "מחכה", "מבינה"
    ],
    # Questions (same for both)
    "questions": [
        "מה", "מי", "איפה", "מתי", "למה", "איך", "כמה", "איזו", "האם", "איזו",
        "לאן", "מאיפה", "כמה זמן", "מה זאת", "מי זאת"
    ],
    # Yes/No/Basic (same for both)
    "basic": [
        "כן", "לא", "אולי", "טוב", "רע", "בסדר", "מצוין", "נהדר", "בבקשה", "תודה",
        "סליחה", "חבל", "יפה", "נכון", "לא נכון", "חשוב", "מעניין", "קל", "קשה"
    ],
    # Food & Drink (same for both)
    "food": [
        "מים", "אוכל", "לחם", "חלב", "קפה", "תה", "פירות", "ירקות", "בשר", "עוף",
        "דג", "גבינה", "ביצה", "אורז", "פסטה", "פיצה", "המבורגר", "סלט", "מרק",
        "עוגה", "עוגייה", "גלידה", "שוקולד", "מיץ", "בירה", "יין", "סוכר", "מלח"
    ],
    # Feelings - female
    "feelings": [
        "שמחה", "עצובה", "כועסת", "עייפה", "רעבה", "צמאה", "חולה", "פוחדת", "רגועה", "לחוצה",
        "נרגשת", "מאושרת", "מודאגת", "עצבנית", "בודדה", "אהבה", "שנאה", "תקווה", "גאווה", "בושה"
    ],
    # Actions (same for both - infinitive)
    "actions": [
        "לאכול", "לשתות", "ללכת", "לישון", "לקרוא", "לכתוב", "לראות", "לשחק", "לדבר", "לשמוע",
        "לעזור", "לחכות", "לרוץ", "לשיר", "לרקוד", "לצחוק", "לבכות", "לחבק", "לנשק", "ללמוד",
        "ללמד", "לעבוד", "לנסוע", "לטוס", "לשחות", "לבשל", "לנקות", "לקנות", "למכור"
    ],
    # Places (same for both)
    "places": [
        "בית", "בית ספר", "עבודה", "חנות", "מסעדה", "פארק", "בית חולים", "רופא", "שירותים",
        "מטבח", "חדר", "מיטה", "רחוב", "עיר", "כפר", "ים", "חוף", "הר", "יער", "גינה",
        "ספרייה", "בנק", "דואר", "תחנה", "שוק", "קניון", "בית קפה", "מכון כושר"
    ],
    # Time (same for both)
    "time": [
        "עכשיו", "מאוחר", "מוקדם", "היום", "מחר", "אתמול", "בוקר", "צהריים", "ערב", "לילה",
        "שבוע", "חודש", "שנה", "יום", "שעה", "דקה", "שנייה", "תמיד", "לפעמים", "לעולם",
        "כבר", "עדיין", "אחרי", "לפני", "בקרוב", "מאוחר יותר"
    ],
    # People (same for both)
    "people": [
        "אמא", "אבא", "אח", "אחות", "בן", "בת", "חבר", "חברה", "מורה", "רופא", "משפחה",
        "סבא", "סבתא", "דוד", "דודה", "בן דוד", "בת דודה", "שכן", "שכנה", "ילד", "ילדה",
        "תינוק", "מבוגר", "זקן", "איש", "אישה", "בעל", "אישה", "חברים"
    ],
    # Common adjectives - female
    "adjectives": [
        "גדולה", "קטנה", "טובה", "רעה", "יפה", "מכוערת", "חדשה", "ישנה", "חמה", "קרה",
        "מהירה", "איטית", "חזקה", "חלשה", "עשירה", "ענייה", "שמחה", "עצובה", "כבדה", "קלה",
        "ארוכה", "קצרה", "רחבה", "צרה", "גבוהה", "נמוכה", "רועשת", "שקטה", "נקייה", "מלוכלכת"
    ],
    # Requests - female
    "requests": [
        "בבקשה", "תודה", "סליחה", "עזרה", "רגע", "חכי", "בואי", "לכי", "תני לי", "קחי",
        "הביאי", "הבא", "שמרי", "זהירות", "אל תעשי", "תעשי", "תחכי", "תחזרי", "תבואי"
    ],
    # Body parts (same for both)
    "body": [
        "יד", "רגל", "ראש", "עין", "אוזן", "פה", "אף", "שיניים", "לשון", "גב",
        "בטן", "לב", "מוח", "עצם", "עור", "שיער", "צוואר", "כתף", "ברך"
    ],
    # Weather (same for both)
    "weather": [
        "שמש", "גשם", "שלג", "רוח", "ענן", "סערה", "חם", "קר", "קריר", "חמים",
        "לח", "יבש", "בהיר", "מעונן"
    ],
    # Numbers - female
    "numbers": [
        "אחת", "שתיים", "שלוש", "ארבע", "חמש", "שש", "שבע", "שמונה", "תשע", "עשר",
        "מאה", "אלף", "מיליון", "ראשונה", "שנייה", "אחרונה"
    ],
    # Colors - female form
    "colors": [
        "אדומה", "כחולה", "ירוקה", "צהובה", "לבנה", "שחורה", "כתומה", "סגולה", "ורודה", "חומה",
        "אפורה", "תכלת", "זהב", "כסף"
    ],
    # Daily activities (same for both)
    "daily": [
        "לקום", "להתלבש", "להתקלח", "לצחצח שיניים", "לסרק", "לאכול ארוחת בוקר", 
        "לצאת", "לחזור הביתה", "לישון", "לנוח", "לראות טלוויזיה", "לגלוש באינטרנט"
    ],
    # Finance & Banking (same for both)
    "finance": [
        "כסף", "בנק", "חשבון", "כרטיס", "מזומן", "אשראי", "העברה", "המחאה", 
        "יתרה", "פיקדון", "הלוואה", "חסכון", "בנקומט", "משיכה", "הפקדה", "עמלה"
    ],
    # Shopping & Supermarket (same for both)
    "shopping": [
        "קניות", "סל", "מחיר", "הנחה", "קבלה", "תשלום", "חשבונית", "עגלה", 
        "מדף", "מבצע", "רשימה", "שקית", "קופה", "פקח", "החזר", "תוית"
    ],
    # Medical & Health (same for both)
    "medical": [
        "רופא", "תרופה", "בית חולים", "בדיקה", "כאב", "חום", "מרשם", "אמבולנס", 
        "ביטוח", "מרפאה", "אחות", "טיפול", "זריקה", "כדור", "רוקח", "מרפא"
    ],
    # Transportation (same for both)
    "transportation": [
        "אוטובוס", "רכבת", "מונית", "רכב", "תחנה", "כרטיס", "נסיעה", "נהג", 
        "כביש", "רחוב", "שביל", "חניה", "אופניים", "הולך רגל", "רמזור", "מעבר"
    ],
    # Home & Utilities (same for both)
    "home": [
        "חשמל", "מים", "גז", "טלפון", "אינטרנט", "טלוויזיה", "מזגן", "חימום", 
        "מפתח", "דלת", "חלון", "מנורה", "שקע", "מפסק", "חשבון", "תשלום"
    ],
    # Communication (same for both)
    "communication": [
        "טלפון", "הודעה", "מייל", "וואטסאפ", "שיחה", "צלצל", "התקשר", "ענה", 
        "כתוב", "קרא", "שלח", "קבל", "סמס", "וידאו", "תמונה", "קול"
    ],
    # Clothing (same for both)
    "clothing": [
        "בגד", "חולצה", "מכנסיים", "שמלה", "נעליים", "סנדל", "גרביים", "תחתונים", 
        "חזייה", "כובע", "מעיל", "ז'קט", "סוודר", "בגד ים", "פיג'מה", "חגורה"
    ],
    # Family & Relations (same for both)
    "family": [
        "משפחה", "אמא", "אבא", "אח", "אחות", "סבא", "סבתא", "דוד", 
        "דודה", "בן דוד", "בת דודה", "נכד", "נכדה", "חתן", "כלה", "זוג"
    ],
    # Work & Office (same for both)
    "work": [
        "עבודה", "פגישה", "מייל", "מחשב", "דדליין", "בוס", "קולגה", "לקוח", 
        "פרויקט", "משימה", "דוח", "הצגה", "משרד", "צוות", "מנהל", "עובד"
    ],
    # Technology (same for both)
    "technology": [
        "טלפון", "מחשב", "נטען", "וויפי", "סיסמה", "אפליקציה", "מסך", "מקלדת", 
        "עכבר", "תיקון", "סוללה", "זיכרון", "קובץ", "תיקייה", "הדפסה", "סריקה"
    ],
    # Social & Entertainment (same for both)
    "entertainment": [
        "סרט", "מוזיקה", "משחק", "חבר", "מסיבה", "מסעדה", "בר", "טיול", 
        "חופשה", "הופעה", "תיאטרון", "ספר", "ספורט", "כדורגל", "כדורסל", "חוף"
    ],
    # Emergency (same for both)
    "emergency": [
        "עזרה!", "משטרה", "אמבולנס", "אש", "חירום", "מהר", "תקשרי לעזרה", "רופא עכשיו", 
        "לא טוב", "כואב מאוד", "צלצלי", "בבקשה תעזרי", "מסוכן", "תיזהרי", "דלת", "מפתח"
    ],
    # Context Questions (same for both)
    "context_questions": [
        "איפה זאת?", "כמה זאת עולה?", "מתי זה מתחיל?", "למה לא?", "איך עושים?", "מי זאת הייתה?",
        "מה קורה?", "איפה ה...?", "מתי נגמר?", "לאן הולכים?", "מאיפה מביאים?", "כמה זמן?",
        "זה בסדר?", "אפשר לעזור?", "מה השעה?", "איפה השירותים?"
    ],
}

# Default to male version for backward compatibility
HEBREW_WORDS = HEBREW_WORDS_MALE

def get_words_for_gender(gender: str) -> dict:
    """Get the appropriate word set for the specified gender."""
    if gender == "female":
        return HEBREW_WORDS_FEMALE
    return HEBREW_WORDS_MALE

# Word prediction context patterns (what words commonly follow others)
NEXT_WORD_PATTERNS = {
    "אני": ["רוצה", "צריך", "יכול", "אוהב", "הולך", "אוכל", "שותה", "חושב", "מרגיש"],
    "רוצה": ["לאכול", "לשתות", "ללכת", "לישון", "לראות", "לשחק", "לקרוא", "מים", "אוכל"],
    "צריך": ["עזרה", "מים", "אוכל", "ללכת", "לנוח", "רופא", "תרופה"],
    "אוכל": ["טעים", "עכשיו", "בבקשה", "מה", "לאכול"],
    "מים": ["בבקשה", "קרים", "חמים", "לשתות"],
    "איפה": ["זה", "נמצא", "את", "ה", "השירותים", "האוכל"],
    "מה": ["קורה", "זה", "אתה", "את", "השעה", "אוכלים"],
    "מתי": ["נלך", "נאכל", "זה", "מגיע", "נגמר"],
    "לאכול": ["עכשיו", "משהו", "ארוחת", "בבקשה"],
    "לשתות": ["מים", "קפה", "תה", "משהו"],
    "ללכת": ["ל", "הביתה", "לישון", "עכשיו"],
    "שלום": ["מה", "קורה", "איך", "אתה", "את"],
    "תודה": ["רבה", "לך", "על", "הכל"],
    "בבקשה": ["תעזור", "מים", "אוכל", "תביא"],
    "סליחה": ["אני", "לא", "הבנתי", "יכול"],
    "עזרה": ["בבקשה", "אני", "צריך", "לי"],
    "טוב": ["מאוד", "לי", "בסדר", "יותר"],
    "רע": ["לי", "מאוד", "לא", "היום"],
    "אמא": ["שלי", "איפה", "בבקשה", "תבואי"],
    "אבא": ["שלי", "איפה", "בבקשה", "תבוא"],
}

# Saved phrases file path
SAVED_PHRASES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "saved_phrases.json")


def load_saved_phrases() -> dict:
    """Load saved phrases from file."""
    try:
        if os.path.exists(SAVED_PHRASES_FILE):
            with open(SAVED_PHRASES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading saved phrases: {e}")
    return {"quick_phrases": QUICK_PHRASES.copy(), "saved": [], "history": []}


def save_saved_phrases(data: dict) -> None:
    """Save phrases to file."""
    try:
        os.makedirs(os.path.dirname(SAVED_PHRASES_FILE), exist_ok=True)
        with open(SAVED_PHRASES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving phrases: {e}")


def get_predictions(current_sentence: str, typed_text: str = "") -> List[str]:
    """Get word predictions based on current sentence context."""
    predictions = []
    
    # If user is typing, suggest words starting with typed text
    if typed_text:
        all_words = []
        for category_words in HEBREW_WORDS.values():
            all_words.extend(category_words)
        all_words = list(set(all_words))
        
        # Filter words starting with typed text
        typed_lower = typed_text.lower()
        matching = [w for w in all_words if w.startswith(typed_text) or w.startswith(typed_lower)]
        if matching:
            predictions.extend(matching[:16])
    
    # Get context-based predictions from last word
    if current_sentence:
        words = current_sentence.strip().split()
        if words:
            last_word = words[-1]
            if last_word in NEXT_WORD_PATTERNS:
                context_preds = NEXT_WORD_PATTERNS[last_word]
                for word in context_preds:
                    if word not in predictions:
                        predictions.append(word)
    
    # Add common words if we need more predictions
    if len(predictions) < 16:
        common_words = [
            "אני", "רוצה", "עכשיו", "בבקשה", "לא", "כן", "מים", "אוכל",
            "טוב", "רע", "היום", "מחר", "פה", "שם", "לי", "לך",
            "מה", "מי", "איפה", "מתי", "למה", "איך", "כמה", "איזה",
            "הוא", "היא", "אתה", "את", "אנחנו", "הם", "הן", "זה"
        ]
        for word in common_words:
            if word not in predictions and len(predictions) < 16:
                predictions.append(word)
    
    return predictions[:16]


def create_aac_interface():
    """Create the AAC keyboard interface."""
    
    # Load saved data
    saved_data = load_saved_phrases()
    
    css = """
        /* AAC Keyboard Styles */
        .aac-container {
            max-width: 100%;
            padding: 10px;
        }
        
        /* Sentence display */
        .sentence-display {
            background: rgba(0, 0, 0, 0.4);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            min-height: 80px;
            margin-bottom: 15px;
            font-size: 28px;
            color: #fff;
            text-align: right;
            direction: rtl;
        }
        
        /* Action buttons row */
        .action-row {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        /* Quick phrases container */
        .quick-phrases {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(40, 40, 40, 0.5);
            border-radius: 12px;
        }
        
        /* Word grid */
        .word-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        
        /* Large touch-friendly buttons */
        .word-btn {
            min-height: 60px;
            font-size: 20px;
            border-radius: 12px;
            background: rgba(60, 60, 60, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            transition: all 0.2s ease;
        }
        
        .word-btn:hover {
            background: rgba(80, 80, 80, 0.9);
            border-color: #F97317;
        }
        
        /* Speak button - prominent */
        .speak-btn {
            background: linear-gradient(135deg, #F97317, #ea580c) !important;
            font-size: 24px !important;
            min-height: 70px !important;
            border-radius: 16px !important;
        }
        
        /* Category tabs */
        .category-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        
        .category-tab {
            padding: 8px 16px;
            border-radius: 20px;
            background: rgba(50, 50, 50, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .category-tab.active {
            background: rgba(249, 115, 23, 0.3);
            border-color: #F97317;
            color: #fff;
        }
        
        /* Input area */
        .type-input input {
            font-size: 20px;
            padding: 15px;
            text-align: right;
            direction: rtl;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .word-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .word-btn {
                min-height: 50px;
                font-size: 18px;
            }
            
            .sentence-display {
                font-size: 22px;
                padding: 15px;
            }
        }
    """
    
    with gr.Column(elem_classes=["aac-container"]):
        # Sentence display
        sentence_display = gr.HTML(
            value='<div class="sentence-display" id="sentence-display">הטקסט יופיע כאן...</div>',
        )
        
        # Hidden state for sentence
        sentence_state = gr.State(value="")
        
        # Action buttons
        with gr.Row():
            clear_btn = gr.Button("🗑️ נקה", size="lg", scale=1)
            backspace_btn = gr.Button("⬅️ מחק מילה", size="lg", scale=1)
            speak_btn = gr.Button("🔊 דברי!", size="lg", scale=2, variant="primary", elem_classes=["speak-btn"])
        
        # Quick phrases
        gr.HTML('<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin: 10px 0;">ביטויים מהירים:</div>')
        
        with gr.Row():
            quick_phrase_btns = []
            for phrase in saved_data.get("quick_phrases", QUICK_PHRASES)[:6]:
                btn = gr.Button(phrase, size="lg", elem_classes=["word-btn"])
                quick_phrase_btns.append(btn)
        
        # Category tabs
        gr.HTML('<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin: 15px 0 10px;">קטגוריות:</div>')
        
        category_choices = ["הכל", "כינויים", "פעלים", "שאלות", "בסיסי", "אוכל", "רגשות", "פעולות", "מקומות", "זמן", "אנשים"]
        category_dropdown = gr.Dropdown(
            choices=category_choices,
            value="הכל",
            label="",
            show_label=False,
            container=False,
        )
        
        # Word predictions grid
        gr.HTML('<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin: 15px 0 10px;">הקש על מילה להוספה למשפט:</div>')
        
        prediction_btns = []
        with gr.Row():
            for i in range(4):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                prediction_btns.append(btn)
        
        with gr.Row():
            for i in range(4):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                prediction_btns.append(btn)
        
        # Text input for typing
        gr.HTML('<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin: 15px 0 10px;">או הקלד טקסט:</div>')
        type_input = gr.Textbox(
            placeholder="הקלד כאן...",
            show_label=False,
            rtl=True,
            elem_classes=["type-input"],
        )
        
        # Add typed word button
        add_typed_btn = gr.Button("➕ הוסף מילה", size="lg")
        
        # Save phrase section
        with gr.Row():
            save_phrase_name = gr.Textbox(placeholder="שם לשמירה...", show_label=False, scale=1)
            save_phrase_btn = gr.Button("💾 שמור ביטוי", size="lg", scale=1)
        
        # Saved phrases display
        saved_phrases_display = gr.HTML(
            value='<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 10px;">ביטויים שמורים יופיעו כאן</div>'
        )
        
        # Ready Answers Section
        gr.HTML('<hr style="margin: 25px 0; border-color: rgba(255,255,255,0.1);">')
        gr.HTML('<div style="font-size: 18px; color: #F97317; margin: 15px 0 10px; font-weight: bold;">💬 תשובות מוכנות</div>')
        gr.HTML('<div style="font-size: 12px; color: rgba(255,255,255,0.5); margin-bottom: 15px;">לחץ על קטגוריה ואז על תשובה להוספה מהירה</div>')
        
        # Ready answer category selector
        ready_category_choices = list(READY_ANSWER_CATEGORIES.values())
        ready_category_dropdown = gr.Dropdown(
            choices=ready_category_choices,
            value=ready_category_choices[0] if ready_category_choices else None,
            label="בחר קטגוריה",
            show_label=True,
            container=True,
        )
        
        # Ready answers display grid
        ready_answer_btns = []
        with gr.Row():
            for i in range(3):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                ready_answer_btns.append(btn)
        
        with gr.Row():
            for i in range(3):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                ready_answer_btns.append(btn)
        
        with gr.Row():
            for i in range(3):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                ready_answer_btns.append(btn)
        
        with gr.Row():
            for i in range(3):
                btn = gr.Button("—", size="lg", elem_classes=["word-btn"])
                ready_answer_btns.append(btn)
        
        # Audio output (hidden)
        audio_output = gr.Audio(visible=False)
        
        # Status
        status_text = gr.Textbox(visible=False)
        
        # Functions
        def update_sentence_display(sentence: str) -> str:
            """Update the sentence display HTML."""
            if not sentence:
                return '<div class="sentence-display" id="sentence-display">הטקסט יופיע כאן...</div>'
            return f'<div class="sentence-display" id="sentence-display" style="font-size: 28px;">{sentence}</div>'
        
        def add_word_to_sentence(word: str, current_sentence: str) -> Tuple[str, str, List[str]]:
            """Add a word to the sentence and get new predictions."""
            if current_sentence:
                new_sentence = current_sentence + " " + word
            else:
                new_sentence = word
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            
            # Pad predictions to 8
            while len(predictions) < 8:
                predictions.append("—")
            
            return new_sentence, display, *predictions
        
        def clear_sentence() -> Tuple[str, str, List[str]]:
            """Clear the sentence."""
            predictions = get_predictions("")
            while len(predictions) < 8:
                predictions.append("—")
            return "", update_sentence_display(""), *predictions
        
        def backspace_sentence(current_sentence: str) -> Tuple[str, str, List[str]]:
            """Remove last word from sentence."""
            words = current_sentence.strip().split()
            if words:
                words.pop()
            new_sentence = " ".join(words)
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 8:
                predictions.append("—")
            
            return new_sentence, display, *predictions
        
        def get_category_words(category: str, current_sentence: str) -> List[str]:
            """Get words for a specific category."""
            category_map = {
                "הכל": None,
                "כינויים": "pronouns",
                "פעלים": "verbs",
                "שאלות": "questions",
                "בסיסי": "basic",
                "אוכל": "food",
                "רגשות": "feelings",
                "פעולות": "actions",
                "מקומות": "places",
                "זמן": "time",
                "אנשים": "people",
            }
            
            cat_key = category_map.get(category)
            if cat_key and cat_key in HEBREW_WORDS:
                words = HEBREW_WORDS[cat_key][:8]
            else:
                # Mix from all categories
                words = get_predictions(current_sentence)
            
            while len(words) < 8:
                words.append("—")
            
            return words[:8]
        
        def update_predictions_for_category(category: str, current_sentence: str) -> List[str]:
            """Update predictions when category changes."""
            return get_category_words(category, current_sentence)
        
        def add_typed_word(typed: str, current_sentence: str) -> Tuple[str, str, str, List[str]]:
            """Add typed word to sentence."""
            if not typed.strip():
                return current_sentence, update_sentence_display(current_sentence), "", *get_category_words("הכל", current_sentence)
            
            new_sentence = current_sentence + " " + typed.strip() if current_sentence else typed.strip()
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 8:
                predictions.append("—")
            
            return new_sentence, display, "", *predictions
        
        def speak_sentence(sentence: str):
            """Speak the sentence using TTS."""
            if not sentence.strip():
                return None, "הכנס משפט לפני דיבור"
            
            # Call the TTS API
            import asyncio
            import tempfile
            import base64
            from . import api
            
            try:
                result = asyncio.run(
                    api.generate_speech_base64(
                        text=sentence,
                        voice="piper_shaul",
                        engine="piper",
                        speed=1.0,
                        volume_factor=2.0,
                    )
                )
                
                # Decode base64 audio
                audio_data_uri = result["audio"]
                audio_base64 = audio_data_uri.split(",")[1]
                audio_bytes = base64.b64decode(audio_base64)
                
                # Save to temp file
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "phonikud_aac_output.wav")
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)
                
                return temp_path, ""
            except Exception as e:
                return None, f"שגיאה: {str(e)}"
        
        def save_current_phrase(sentence: str, name: str) -> str:
            """Save current sentence as a phrase."""
            if not sentence.strip() or not name.strip():
                return "הכנס משפט ושם לשמירה"
            
            data = load_saved_phrases()
            data.setdefault("saved", []).append({"name": name, "text": sentence})
            save_saved_phrases(data)
            
            return f'נשמר: "{name}"'
        
        def get_ready_answers_for_category(category_label: str) -> List[str]:
            """Get ready answers for a category by its label."""
            # Find the category key from the label
            cat_key = None
            for key, label in READY_ANSWER_CATEGORIES.items():
                if label == category_label:
                    cat_key = key
                    break
            
            if cat_key and cat_key in READY_ANSWERS:
                answers = READY_ANSWERS[cat_key][:12]
            else:
                # Default to greetings
                answers = READY_ANSWERS.get("greetings", [])[:12]
            
            # Pad to 12 buttons
            while len(answers) < 12:
                answers.append("—")
            
            return answers
        
        def update_ready_answers(category_label: str) -> List[str]:
            """Update ready answer buttons when category changes."""
            return get_ready_answers_for_category(category_label)
        
        def add_ready_answer(answer: str, current_sentence: str) -> Tuple[str, str, List[str]]:
            """Add a ready answer to the sentence."""
            if answer == "—":
                return current_sentence, update_sentence_display(current_sentence), *get_category_words("הכל", current_sentence)
            
            # For ready answers, replace the current sentence or append
            if current_sentence:
                new_sentence = current_sentence + " " + answer
            else:
                new_sentence = answer
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 8:
                predictions.append("—")
            
            return new_sentence, display, *predictions
        
        # Wire up events
        
        # Word buttons
        for i, btn in enumerate(prediction_btns):
            btn.click(
                fn=lambda word, s=sentence_state: add_word_to_sentence(word, s.value) if word != "—" else (s.value, update_sentence_display(s.value), *["—"]*8),
                inputs=[btn, sentence_state],
                outputs=[sentence_state, sentence_display] + prediction_btns,
            )
        
        # Quick phrase buttons
        for btn in quick_phrase_btns:
            btn.click(
                fn=lambda phrase, s=sentence_state: add_word_to_sentence(phrase, s.value),
                inputs=[btn, sentence_state],
                outputs=[sentence_state, sentence_display] + prediction_btns,
            )
        
        # Action buttons
        clear_btn.click(
            fn=clear_sentence,
            outputs=[sentence_state, sentence_display] + prediction_btns,
        )
        
        backspace_btn.click(
            fn=backspace_sentence,
            inputs=[sentence_state],
            outputs=[sentence_state, sentence_display] + prediction_btns,
        )
        
        # Category change
        category_dropdown.change(
            fn=update_predictions_for_category,
            inputs=[category_dropdown, sentence_state],
            outputs=prediction_btns,
        )
        
        # Add typed word
        add_typed_btn.click(
            fn=add_typed_word,
            inputs=[type_input, sentence_state],
            outputs=[sentence_state, sentence_display, type_input] + prediction_btns,
        )
        
        # Speak
        speak_btn.click(
            fn=speak_sentence,
            inputs=[sentence_state],
            outputs=[audio_output, status_text],
        )
        
        # Save phrase
        save_phrase_btn.click(
            fn=save_current_phrase,
            inputs=[sentence_state, save_phrase_name],
            outputs=[status_text],
        )
        
        # Ready answers category change
        ready_category_dropdown.change(
            fn=update_ready_answers,
            inputs=[ready_category_dropdown],
            outputs=ready_answer_btns,
        )
        
        # Ready answer button clicks
        for btn in ready_answer_btns:
            btn.click(
                fn=lambda answer, s=sentence_state: add_ready_answer(answer, s.value),
                inputs=[btn, sentence_state],
                outputs=[sentence_state, sentence_display] + prediction_btns,
            )
        
        # Initialize predictions
        initial_preds = get_predictions("")
        while len(initial_preds) < 8:
            initial_preds.append("—")
        
        # Initialize ready answers with first category
        initial_ready = get_ready_answers_for_category(ready_category_choices[0] if ready_category_choices else "👋 ברכות")
        
        return sentence_state, sentence_display, prediction_btns
