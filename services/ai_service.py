import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """AI Service for smart event creation using OpenAI GPT-4"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o-mini"  # Use more affordable model
        
        # Try to import openai, but don't fail if not available
        try:
            import openai
            if self.api_key and self.api_key.startswith('sk-'):
                self.client = openai.OpenAI(api_key=self.api_key)
                self.available = True
                print("✅ OpenAI client initialized successfully")
            else:
                self.client = None
                self.available = False
                print("⚠️  No valid OpenAI API key found - using simple parsing")
        except ImportError:
            self.client = None
            self.available = False
            print("⚠️  OpenAI not available - install with: pip install openai")
        except Exception as e:
            self.client = None
            self.available = False
            print(f"⚠️  OpenAI initialization failed: {str(e)} - using simple parsing")
    
    def parse_natural_language_event(self, user_input):
        """
        Parse natural language input and extract event information
        """
        
        if not user_input or not user_input.strip():
            return {
                "success": False,
                "error": "Please provide event details",
                "needs_clarification": True,
                "clarification_message": "Please describe your event"
            }
        
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
            print(f"OpenAI API error: {str(e)}")
            # Fall back to simple parsing
            return self._simple_parse(user_input)
    
    def _simple_parse(self, user_input):
        """
        Simple parsing fallback when OpenAI is not available
        """
        if not user_input or not user_input.strip():
            return {
                "success": False,
                "error": "Please provide event details",
                "needs_clarification": True,
                "clarification_message": "Please describe your event"
            }
        
        # Basic keyword-based parsing
        input_lower = user_input.lower().strip()
        
        # Extract title (first part before time/date keywords)
        time_keywords = ['tomorrow', 'today', 'next', 'at', 'on', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        title = user_input.strip()
        date_mentioned = False
        
        # Check if any date keyword is mentioned
        for keyword in time_keywords:
            if keyword in input_lower:
                date_mentioned = True
                # Split at the keyword to get title
                parts = user_input.split(keyword, 1)
                if parts[0].strip():
                    title = parts[0].strip()
                break
        
        # Clean up title
        title = title.replace('  ', ' ').strip()
        if not title:
            title = user_input.strip()
        
        # Simple date parsing
        now = datetime.now()
        event_date = None
        
        # Check for specific date keywords
        if 'tomorrow' in input_lower:
            event_date = now + timedelta(days=1)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"Parsed 'tomorrow': {event_date}")
            
        elif 'today' in input_lower:
            event_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if event_date < now:  # If 9am has passed, set to current time + 1 hour
                event_date = now + timedelta(hours=1)
                event_date = event_date.replace(minute=0, second=0, microsecond=0)
            print(f"Parsed 'today': {event_date}")
            
        elif 'next week' in input_lower:
            event_date = now + timedelta(days=7)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"Parsed 'next week': {event_date}")
            
        elif 'monday' in input_lower:
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"Parsed 'monday': {event_date}")
            
        elif 'tuesday' in input_lower:
            days_ahead = 1 - now.weekday()  # Tuesday is 1
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'wednesday' in input_lower:
            days_ahead = 2 - now.weekday()  # Wednesday is 2
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'thursday' in input_lower:
            days_ahead = 3 - now.weekday()  # Thursday is 3
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'friday' in input_lower:
            days_ahead = 4 - now.weekday()  # Friday is 4
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'saturday' in input_lower:
            days_ahead = 5 - now.weekday()  # Saturday is 5
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'sunday' in input_lower:
            days_ahead = 6 - now.weekday()  # Sunday is 6
            if days_ahead <= 0:
                days_ahead += 7
            event_date = now + timedelta(days=days_ahead)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
        elif 'next' in input_lower:
            # Default "next" to next week if no specific day mentioned
            event_date = now + timedelta(days=7)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"Parsed 'next': {event_date}")
        
        # If no date keywords found, set default to tomorrow
        if not event_date and not date_mentioned:
            event_date = now + timedelta(days=1)
            event_date = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"No date mentioned, defaulting to tomorrow: {event_date}")
        
        # Extract time if mentioned
        if event_date and 'at' in input_lower:
            try:
                # Find the part after "at"
                at_parts = user_input.lower().split('at')
                if len(at_parts) > 1:
                    time_part = at_parts[1].strip().split()[0]
                    print(f"Trying to parse time: '{time_part}'")
                    
                    # Handle different time formats
                    if 'pm' in time_part:
                        hour_str = time_part.replace('pm', '').strip()
                        hour = int(hour_str)
                        if hour != 12:
                            hour += 12
                        event_date = event_date.replace(hour=hour, minute=0)
                        print(f"Parsed PM time: {hour}:00")
                        
                    elif 'am' in time_part:
                        hour_str = time_part.replace('am', '').strip()
                        hour = int(hour_str)
                        if hour == 12:
                            hour = 0
                        event_date = event_date.replace(hour=hour, minute=0)
                        print(f"Parsed AM time: {hour}:00")
                        
                    elif ':' in time_part:
                        time_obj = datetime.strptime(time_part, '%H:%M')
                        event_date = event_date.replace(hour=time_obj.hour, minute=time_obj.minute)
                        print(f"Parsed HH:MM time: {time_obj.hour}:{time_obj.minute}")
                        
                    elif time_part.isdigit():
                        hour = int(time_part)
                        # Assume afternoon if hour is reasonable
                        if 1 <= hour <= 11:
                            hour += 12  # Make it PM
                        event_date = event_date.replace(hour=hour, minute=0)
                        print(f"Parsed numeric time as PM: {hour}:00")
                        
            except Exception as e:
                print(f"Time parsing failed: {e}")
                # Keep default time if parsing fails
        
        # Extract location (look for prepositions)
        location = None
        location_preps = [' in ', ' at ']
        for prep in location_preps:
            if prep in input_lower:
                parts = user_input.lower().split(prep)
                if len(parts) > 1:
                    location_part = parts[-1].strip()
                    # Remove time references from location
                    location_words = []
                    for word in location_part.split():
                        if not any(time_word in word.lower() for time_word in ['am', 'pm', ':', 'tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                            location_words.append(word)
                    if location_words:
                        location = ' '.join(location_words)
                        print(f"Extracted location: '{location}'")
                break
        
        if not event_date:
            return {
                "success": False,
                "error": "Could not determine date",
                "needs_clarification": True,
                "clarification_message": "Please specify when this event should happen (e.g., 'tomorrow', 'today at 3pm', 'next Monday')"
            }
        
        print(f"Final parsed data - Title: '{title}', Date: {event_date}, Location: '{location}'")
        
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
        
        prompt = f"Create a brief, professional event description for: '{title}'"
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
            print(f"Description enhancement error: {str(e)}")
            return f"Event: {title}" + (f" at {location}" if location else "")