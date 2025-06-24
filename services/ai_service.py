import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """AI Service for smart event creation using OpenAI GPT-4"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"
        
        # Try to import openai, but don't fail if not available
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            self.available = bool(self.api_key)
        except ImportError:
            self.client = None
            self.available = False
            print("OpenAI not available - install with: pip install openai")
    
    def parse_natural_language_event(self, user_input):
        """
        Parse natural language input and extract event information
        """
        
        # If OpenAI is not available, use simple parsing
        if not self.available or not self.client:
            return self._simple_parse(user_input)
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        system_prompt = f"""
        You are an intelligent event parser. Extract event information from natural language input and return structured JSON data.
        
        Current date and time: {current_date}
        
        Parse the user input and extract:
        - title: Event title (required)
        - description: Brief description (optional, can be inferred)
        - date: ISO format datetime (YYYY-MM-DD HH:MM) - interpret relative dates like "tomorrow", "next week"
        - location: Location if mentioned (optional)
        - status: Always set to "upcoming"
        
        Rules:
        - If no specific time is mentioned, default to 09:00
        - If relative dates like "tomorrow", "next week" are used, calculate from current date
        - If no date is mentioned, ask for clarification
        - Be intelligent about inferring context
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "string",
            "description": "string or null",
            "date": "YYYY-MM-DD HH:MM",
            "location": "string or null",
            "status": "upcoming",
            "needs_clarification": false,
            "clarification_message": "string or null"
        }}
        
        If you cannot determine a date, set needs_clarification to true and provide a helpful message.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                event_data = json.loads(result_text)
                
                # Validate required fields
                if not event_data.get('title'):
                    return {
                        "success": False,
                        "error": "Could not extract event title from input",
                        "needs_clarification": True,
                        "clarification_message": "Please provide a clear event title"
                    }
                
                # Convert date string to datetime object if provided
                if event_data.get('date') and not event_data.get('needs_clarification'):
                    try:
                        # Parse the date string
                        date_str = event_data['date']
                        event_data['date'] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        return {
                            "success": False,
                            "error": "Invalid date format",
                            "needs_clarification": True,
                            "clarification_message": "Please provide a valid date and time"
                        }
                
                return {
                    "success": True,
                    "event_data": event_data
                }
                
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse AI response",
                    "raw_response": result_text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI service error: {str(e)}"
            }
    
    def _simple_parse(self, user_input):
        """
        Simple parsing fallback when OpenAI is not available
        """
        # Basic keyword-based parsing
        input_lower = user_input.lower()
        
        # Extract title (first part before time/date keywords)
        time_keywords = ['tomorrow', 'today', 'next', 'at', 'on', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        title = user_input
        for keyword in time_keywords:
            if keyword in input_lower:
                parts = user_input.split(keyword, 1)
                if parts[0].strip():
                    title = parts[0].strip()
                break
        
        # Simple date parsing
        now = datetime.now()
        event_date = None
        
        if 'tomorrow' in input_lower:
            event_date = now + timedelta(days=1)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
        elif 'today' in input_lower:
            event_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
        elif 'next week' in input_lower:
            event_date = now + timedelta(days=7)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Extract time if mentioned
        if 'at' in input_lower:
            try:
                parts = user_input.lower().split('at')
                if len(parts) > 1:
                    time_part = parts[1].strip().split()[0]
                    if 'pm' in time_part or 'am' in time_part:
                        time_obj = datetime.strptime(time_part, '%I%p')
                    elif ':' in time_part:
                        time_obj = datetime.strptime(time_part, '%H:%M')
                    else:
                        time_obj = datetime.strptime(time_part + ':00', '%H:%M')
                    
                    if event_date:
                        event_date = event_date.replace(hour=time_obj.hour, minute=time_obj.minute)
            except:
                pass
        
        # Extract location (after 'at' or 'in')
        location = None
        for prep in ['at', 'in']:
            if prep in input_lower:
                parts = user_input.lower().split(prep)
                if len(parts) > 1:
                    location_part = parts[-1].strip()
                    # Remove time if it's there
                    location_words = location_part.split()
                    if location_words and not any(char.isdigit() for char in location_words[0]):
                        location = location_part
                break
        
        if not event_date:
            return {
                "success": False,
                "error": "Could not determine date",
                "needs_clarification": True,
                "clarification_message": "Please specify when this event should happen"
            }
        
        return {
            "success": True,
            "event_data": {
                "title": title,
                "description": f"Event: {title}",
                "date": event_date,
                "location": location,
                "status": "upcoming",
                "needs_clarification": False,
                "clarification_message": None
            }
        }
    
    def enhance_event_description(self, title, location=None):
        """
        Generate or enhance event description
        """
        if not self.available or not self.client:
            # Simple fallback
            description = f"Event: {title}"
            if location:
                description += f" at {location}"
            return description
        
        prompt = f"Create a nice and add to it words, professional event description for: '{title}'"
        if location:
            prompt += f" at {location}"
        prompt += ". Keep it under 100 words and make it helpful."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates brief, professional event descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Event: {title}" + (f" at {location}" if location else "")