import re
import sys
import os

try:
    from . import strip_markdown
except ImportError:
    def strip_markdown(text):
        if not text:
            return ""
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  
        text = re.sub(r'\*(.+?)\*', r'\1', text)  
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  
        text = re.sub(r'^#+\s+(.+)$', r'\1', text, flags=re.MULTILINE)  
        return text

class TimestampFormatter:
    @staticmethod
    def validate_timestamp(timestamp):
        """
        Validate timestamp format (HH:MM:SS or MM:SS)
        Returns True if valid, False otherwise
        """
        timestamp_pattern = r'^\d{1,2}:\d{2}(:\d{2})?$'
        return bool(re.match(timestamp_pattern, timestamp))

    @staticmethod
    def normalize_timestamp(timestamp):
        """
        Normalize timestamp to consistent HH:MM:SS format
        """
        parts = timestamp.split(':')
        
        if len(parts) == 2:
            parts.insert(0, '00')
        elif len(parts) == 3:
            parts = [part.zfill(2) for part in parts]
        
        return ':'.join(parts)

    @staticmethod
    def format(gentext, max_description_length=100):
        """
        Advanced timestamp formatting with multiple improvements
        
        Args:
            gentext (str): Generated text with timestamps
            max_description_length (int): Maximum length for description
        
        Returns:
            str: Formatted timestamps
        """
        if not gentext:
            return "No timestamps available"
            
        try:
            if 'strip_markdown' in sys.modules:
                clean_text = sys.modules['strip_markdown'].strip_markdown(gentext)
            else:
                clean_text = strip_markdown(gentext)
        except Exception:
            clean_text = gentext
        
        lines = clean_text.split('\n')
        
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            timestamp_match = re.search(r'(\d{1,2}:\d{1,2}(?::\d{2})?)', line)
            
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                
                description_match = re.search(fr'{re.escape(timestamp)}\s*[-:]?\s*(.*)', line)
                description = description_match.group(1) if description_match else ""
                
                if not TimestampFormatter.validate_timestamp(timestamp):
                    formatted_lines.append(line)
                    continue
                
                normalized_timestamp = TimestampFormatter.normalize_timestamp(timestamp)
                
                if description and len(description) > max_description_length:
                    description = description[:max_description_length] + '...'
                
                formatted_line = f"{normalized_timestamp} - {description.strip()}"
                formatted_lines.append(formatted_line)
            else:
                if re.search(r'\d+', line):
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    @staticmethod
    def hyperlink_timestamps(formatted_timestamps, video_url):
        """
        Convert timestamps to clickable YouTube links
        
        Args:
            formatted_timestamps (str): Formatted timestamps string
            video_url (str): Original YouTube video URL
        
        Returns:
            str: Timestamps with hyperlinked timestamps
        """
        def create_youtube_timestamp_link(match):
            timestamp = match.group(1)
            description = match.group(2)
            
            time_parts = timestamp.split(':')
            if len(time_parts) == 2:
                seconds = int(time_parts[0]) * 60 + int(time_parts[1])
            elif len(time_parts) == 3:
                seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
            else:
                return match.group(0)
            
            hyperlink = f"[{timestamp}]({video_url}&t={seconds}s) - {description}"
            return hyperlink
        
        timestamp_pattern = r'^(\d{2}:\d{2}(?::\d{2})?) - (.*)$'
        return re.sub(timestamp_pattern, create_youtube_timestamp_link, 
                      formatted_timestamps, flags=re.MULTILINE)

if __name__ == "__main__":
    sample_text = """
    00:30 Introduction to the video topic
    03:45 First main point explained
    12:15 Second key concept
    25:50 Concluding remarks
    """
    
    formatted = TimestampFormatter.format(sample_text)
    print("Basic Formatting:")
    print(formatted)
    
    video_url = "https://www.youtube.com/watch?v=example_video"
    hyperlinked = TimestampFormatter.hyperlink_timestamps(formatted, video_url)
    print("\nHyperlinked Timestamps:")
    print(hyperlinked)