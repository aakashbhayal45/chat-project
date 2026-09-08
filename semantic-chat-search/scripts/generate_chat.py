import json
import random
import os
from datetime import datetime, timedelta

def generate_dataset():
    random.seed(42)
    
    participants = ["Aman", "Priya", "Rahul", "Neha", "Ravi", "Ankit", "Simran", "Karan"]
    
    start_date = datetime(2023, 11, 1, 9, 0, 0)
    num_messages = 4250

    hinglish_casual = [
        "kya chal raha hai guys?",
        "kisi ne kal ka match dekha?",
        "bhai bohot kaam hai aaj office me",
        "scrum call end ho gayi, finally free",
        "coffee break anyone?",
        "aaj mausam bohot sahi hai",
        "kahan ho sab?",
        "good morning all!",
        "bhai ye bug solve hi nahi ho raha",
        "kal raat ko late tak jagg raha tha",
        "chai pine chalein?",
        "haan bro 5 mins me aata hu",
        "kya scene hai aaj evening ka?",
        "bhai party kab de raha hai?",
        "congrats bhai!!",
        "sahi hai yaar 😃",
        "hahaha true af",
        "lol 😆",
        "omg no way!",
        "arre waah super cool",
        "okay noted",
        "cool cool",
        "let me check and confirm",
        "wait a sec",
        "haan ji",
        "naa bhai mood nahi hai",
        "subah se baarish ho rahi hai",
        "khana khaya sabne?",
        "biryani order karein aaj?",
        "swiggy par coupon code mil raha hai",
        "zomato gold standard service late delivery again 😤",
        "bhai kya meme banaya hai 🤣🤣",
        "forwarded as received: important update regarding traffic rules",
        "reminder: team meeting at 4 PM",
        "file download nahi ho rahi server error 500",
        "net speed kaafi slow hai aaj",
        "weekend plans kya hain?",
        "kuch nahi bas sleep reset cycle",
        "movies dekhne chalein?",
        "Dune Part 2 ka ticket book kar liya?",
        "bhai spoilers mat dena please",
        "arrey bilkul nahi",
        "haha okay okay",
        "bhai link bhejna zara",
        "instagram reel ka link view karo",
        "spotless performance by Rohit Sharma yesterday!",
        "IPL tickets ka price ridiculously high hai",
        "gym workout done for the day 💪",
        "diet plan follow karna mushkil hai",
        "pizza night tonight! 🍕",
        "bhai laptop charger bhool gaya office me",
        "kab tak aoge home?",
        "bus stand par hu traffic jam hai heavy",
        "metro ride is so peaceful right now",
        "uber ride cancel ho gayi 3 times"
    ]

    food_discussions = [
        "aaj lunch me kya laya hai?",
        "ghar ka khana best hota hai",
        "momos khane chalein shaam ko?",
        "CP me naya cafe khula hai, review accha hai",
        "south indian food try karte hain aaj",
        "cold coffee with ice cream mandatory hai 🥤",
        "bhai fast food kam karo, health pe dhyan do",
        "smoothie bowl recipe try ki thi kal"
    ]

    tech_work_discussions = [
        "FastAPI version upgraded to latest release",
        "Python 3.11 pattern matching feature is clean",
        "FAISS vector index building takes minimal RAM",
        "sentence transformers model paraphrase multilingual loaded",
        "Docker container build complete",
        "git push main forced update caution",
        "code review comments resolve kar diye hain",
        "deployment succeeded on AWS staging environment"
    ]

    messages = []
    curr_time = start_date

    def advance_time():
        nonlocal curr_time
        gap = random.randint(1, 45)
        curr_time += timedelta(minutes=gap)
        return curr_time.isoformat()

    trip_decision_id = None
    budget_decision_id = None
    date_decision_id = None
    eval_targets = {}

    msg_id = 1

    while msg_id <= num_messages:
        # Thread 1: Trip Decision (~Nov/Dec)
        if msg_id == 500:
            thread_1_msgs = [
                ("Aman", "guys group holiday vacation trip ke liye location finalize karein? kaafi time se plan pending hai"),
                ("Priya", "haan please, Goa ka budget kaafi high ja raha hai air tickets 3x hain"),
                ("Rahul", "Shimla bhi excessive costly padega peak season me room tariff doubled hai"),
                ("Neha", "Rishikesh ka kya thought hai? rafting & camping?"),
                ("Ravi", "Rishikesh me summer noon me bohot garmi hogi, hill station prefer karte hain"),
                ("Ankit", "Manali ka kya scene hai? temperature pleasant rahega and bus options readily available hain"),
                ("Simran", "Manali sounds lovely! budget view me fit hoga and snow points bhi cover honge"),
                ("Karan", "Manali is super cool, hotel rates bhi reasonable mil rahe hain online"),
                ("Priya", "Goa plan drop karte hain fir, Manali manageable hai for everyone"),
                ("Rahul", "merko to Manali bilkul approved hai, scenic views bhi awesome hain"),
                ("Aman", "haan bhai chalo Manali fix hai") # Decision message ID
            ]
            for sender, text in thread_1_msgs:
                ts = advance_time()
                m_obj = {"id": msg_id, "timestamp": ts, "sender": sender, "message": text}
                messages.append(m_obj)
                if text == "haan bhai chalo Manali fix hai":
                    trip_decision_id = msg_id
                    eval_targets["trip_decision"] = m_obj
                msg_id += 1
            continue

        # Thread 2: Budget Decision (~Feb)
        if msg_id == 1500:
            thread_2_msgs = [
                ("Priya", "Manali trip ki total cost estimate calculate karein per head?"),
                ("Ravi", "Volvo bus round trip around 2500 padega per person"),
                ("Ankit", "Hotel stay for 4 nights stay total 3000 per head sharing basis pe"),
                ("Neha", "Food and local cab sightseeing extra kitna aayega?"),
                ("Karan", "Around 2500 food & activities ke liye max safety buffer rakhna chahiye"),
                ("Simran", "so total around 8000 per person me complete ho jayega comfortably"),
                ("Aman", "8000 per head looks completely reasonable and affordable for everyone"),
                ("Rahul", "agree, ziada budget exceed nahi hona chahiye"),
                ("Priya", "so per person 8000 budget lock karte hain final") # Decision message ID
            ]
            for sender, text in thread_2_msgs:
                ts = advance_time()
                m_obj = {"id": msg_id, "timestamp": ts, "sender": sender, "message": text}
                messages.append(m_obj)
                if text == "so per person 8000 budget lock karte hain final":
                    budget_decision_id = msg_id
                    eval_targets["budget_decision"] = m_obj
                msg_id += 1
            continue

        # Thread 3: Date Decision (~March)
        if msg_id == 2800:
            thread_3_msgs = [
                ("Neha", "trip dates finalize karte hain, office leaves sanction karwani hain"),
                ("Karan", "April 10-14 long weekend me log keh rahe the"),
                ("Simran", "April 10-14 mere office me release cycle is tight, leave grant nahi hogi"),
                ("Aman", "April 18-22 slot kaisa rahega? Thursday night departure & Monday return"),
                ("Priya", "mere dates 18 to 22 April completely free hain, no overlap"),
                ("Rahul", "me too, 18-22 April works perfectly fine for me"),
                ("Ravi", "18-22 April is ideal, long weekend crowd bhi thoda clear hoga"),
                ("Ankit", "perfect, sabka consensus ban gaya dates pe"),
                ("Neha", "18 to 22 April confirmed dates guys mark it down") # Decision message ID
            ]
            for sender, text in thread_3_msgs:
                ts = advance_time()
                m_obj = {"id": msg_id, "timestamp": ts, "sender": sender, "message": text}
                messages.append(m_obj)
                if text == "18 to 22 April confirmed dates guys mark it down":
                    date_decision_id = msg_id
                    eval_targets["date_decision"] = m_obj
                msg_id += 1
            continue

        # Target messages for specific evaluation queries
        if msg_id == 800:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Priya", "message": "Maine momos wale bhaiya se Google Pay kar diya tha 350 rupees"}
            eval_targets["priya_gpay"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 1100:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Rahul", "message": "Train tickets tatkal booking windows open at 10 AM sharp tomorrow morning"}
            eval_targets["rahul_tickets"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 2000:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Aman", "message": "Spotify Premium family plan subscription renew ho gaya hai 299 rupees monthly"}
            eval_targets["aman_spotify"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 2300:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Simran", "message": "Gym membership annual package per 40 percent discount offer chal raha hai Cult fit pass pe"}
            eval_targets["simran_gym"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 2500:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Karan", "message": "MacBook M2 charger original Apple store se 4500 ka kharida laptop power cable"}
            eval_targets["karan_charger"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 3200:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Neha", "message": "Python automation script running successfully on server log parser backend"}
            eval_targets["neha_python"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 3600:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Ravi", "message": "IPL final cricket match screening house party arranged at flat 302"}
            eval_targets["ravi_ipl"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        if msg_id == 4000:
            m_obj = {"id": msg_id, "timestamp": advance_time(), "sender": "Ankit", "message": "Airbnb luxury villa reservation with private swimming pool near Solang valley view"}
            eval_targets["ankit_airbnb"] = m_obj
            messages.append(m_obj)
            msg_id += 1
            continue

        # General messages
        sender = random.choice(participants)
        category = random.choices(
            [hinglish_casual, food_discussions, tech_work_discussions],
            weights=[0.75, 0.15, 0.10]
        )[0]
        text = random.choice(category)
        
        if random.random() < 0.15:
            text += " " + random.choice(["👍", "🙌", "🔥", "😂", "💯", "😴", "🎉", "👌"])
        
        ts = advance_time()
        m_obj = {"id": msg_id, "timestamp": ts, "sender": sender, "message": text}
        messages.append(m_obj)
        msg_id += 1

    os.makedirs("dataset", exist_ok=True)
    
    chat_path = os.path.join("dataset", "chat.json")
    with open(chat_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

    print(f"Generated dataset with {len(messages)} messages successfully.")
    print(f"Trip Decision Message ID: {trip_decision_id}")
    print(f"Budget Decision Message ID: {budget_decision_id}")
    print(f"Date Decision Message ID: {date_decision_id}")

    # Build 40 evaluation queries
    eval_queries = [
        # 8 Zero Lexical Overlap Queries
        {
            "query": "When did everyone finally settle on the destination?",
            "correct_message_id": trip_decision_id,
            "type": "semantic"
        },
        {
            "query": "Which vacation spot got approved by the group?",
            "correct_message_id": trip_decision_id,
            "type": "semantic"
        },
        {
            "query": "Where are we traveling for our group holiday?",
            "correct_message_id": trip_decision_id,
            "type": "semantic"
        },
        {
            "query": "What is the finalized contribution amount per person?",
            "correct_message_id": budget_decision_id,
            "type": "semantic"
        },
        {
            "query": "How much expenditure was fixed for the outing?",
            "correct_message_id": budget_decision_id,
            "type": "semantic"
        },
        {
            "query": "What time window was selected for the vacation?",
            "correct_message_id": date_decision_id,
            "type": "semantic"
        },
        {
            "query": "Which days did the group lock in for the journey?",
            "correct_message_id": date_decision_id,
            "type": "semantic"
        },
        {
            "query": "When did we decide on the trip?",
            "correct_message_id": trip_decision_id,
            "type": "semantic"
        },

        # Semantic Queries
        {
            "query": "What happened with the Goa plan?",
            "correct_message_id": messages[499]["id"], # Priya: Goa ka budget kaafi high ja raha hai
            "type": "semantic"
        },
        {
            "query": "Why was Shimla rejected as a destination?",
            "correct_message_id": messages[500]["id"], # Rahul: Shimla bhi excessive costly padega
            "type": "semantic"
        },
        {
            "query": "Which place did everyone finally agree on?",
            "correct_message_id": trip_decision_id,
            "type": "semantic"
        },
        {
            "query": "What is the final budget per person?",
            "correct_message_id": budget_decision_id,
            "type": "semantic"
        },
        {
            "query": "What dates were locked for the trip?",
            "correct_message_id": date_decision_id,
            "type": "semantic"
        },
        {
            "query": "Who suggested Manali first?",
            "correct_message_id": messages[503]["id"], # Ankit: Manali ka kya scene hai
            "type": "semantic"
        },
        {
            "query": "What was discussed about Rishikesh?",
            "correct_message_id": messages[501]["id"], # Neha: Rishikesh ka kya thought hai
            "type": "semantic"
        },
        {
            "query": "Who mentioned bus ticket prices for the trip?",
            "correct_message_id": messages[1492]["id"], # Ravi: Volvo bus round trip around 2500
            "type": "semantic"
        },

        # Attributed Queries (Sender specific)
        {
            "query": "What did Priya say about the budget?",
            "correct_message_id": budget_decision_id,
            "type": "attributed"
        },
        {
            "query": "What did Rahul mention about tickets?",
            "correct_message_id": eval_targets["rahul_tickets"]["id"],
            "type": "attributed"
        },
        {
            "query": "Show me what Aman said about the trip.",
            "correct_message_id": trip_decision_id,
            "type": "attributed"
        },
        {
            "query": "What did Priya pay using Google Pay?",
            "correct_message_id": eval_targets["priya_gpay"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Simran say about gym discount?",
            "correct_message_id": eval_targets["simran_gym"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Karan buy for his MacBook?",
            "correct_message_id": eval_targets["karan_charger"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Neha say about Python automation?",
            "correct_message_id": eval_targets["neha_python"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Ravi arrange at his flat?",
            "correct_message_id": eval_targets["ravi_ipl"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Ankit reserve in Solang valley?",
            "correct_message_id": eval_targets["ankit_airbnb"]["id"],
            "type": "attributed"
        },
        {
            "query": "What did Aman say about Spotify Premium?",
            "correct_message_id": eval_targets["aman_spotify"]["id"],
            "type": "attributed"
        },

        # Temporal Queries
        {
            "query": "What did we discuss in November 2023?",
            "correct_message_id": 50,
            "type": "temporal"
        },
        {
            "query": "What happened in November 2023?",
            "correct_message_id": trip_decision_id,
            "type": "temporal"
        },
        {
            "query": "What was discussed around March 2024?",
            "correct_message_id": date_decision_id,
            "type": "temporal"
        },
        {
            "query": "What did Priya say in February 2024?",
            "correct_message_id": budget_decision_id,
            "type": "temporal"
        },
        {
            "query": "What happened in the first week of April 2024?",
            "correct_message_id": eval_targets["ankit_airbnb"]["id"],
            "type": "temporal"
        },
        {
            "query": "What did Rahul say last month?",
            "correct_message_id": messages[2797]["id"],
            "type": "temporal"
        },
        {
            "query": "What was discussed in December 2023?",
            "correct_message_id": eval_targets["priya_gpay"]["id"],
            "type": "temporal"
        },
        {
            "query": "Show messages from February 2024",
            "correct_message_id": budget_decision_id,
            "type": "temporal"
        },

        # Mixed Queries
        {
            "query": "What did Neha confirm about leaves and dates?",
            "correct_message_id": date_decision_id,
            "type": "attributed"
        },
        {
            "query": "What accommodation was booked for the stay?",
            "correct_message_id": eval_targets["ankit_airbnb"]["id"],
            "type": "semantic"
        },
        {
            "query": "How much does the Spotify family plan cost per month?",
            "correct_message_id": eval_targets["aman_spotify"]["id"],
            "type": "semantic"
        },
        {
            "query": "Who is hosting the IPL match screening?",
            "correct_message_id": eval_targets["ravi_ipl"]["id"],
            "type": "semantic"
        },
        {
            "query": "What is the discount rate on Cult fit gym membership?",
            "correct_message_id": eval_targets["simran_gym"]["id"],
            "type": "semantic"
        },
        {
            "query": "What time does tatkal train booking start?",
            "correct_message_id": eval_targets["rahul_tickets"]["id"],
            "type": "semantic"
        }
    ]

    assert len(eval_queries) == 40, f"Expected 40 queries, got {len(eval_queries)}"

    eval_path = os.path.join("dataset", "evaluation.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_queries, f, indent=2, ensure_ascii=False)

    print(f"Saved evaluation.json with exactly {len(eval_queries)} queries.")

if __name__ == "__main__":
    generate_dataset()
