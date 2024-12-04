import re
import strip_markdown

class TimestampFormatter:
    @staticmethod
    def validate_timestamp(timestamp):
        """
        Validate timestamp format (HH:MM:SS or MM:SS)
        Returns True if valid, False otherwise
        """
        # Regex for HH:MM:SS or MM:SS formats
        timestamp_pattern = r'^\d{1,2}:\d{2}(:\d{2})?$'
        return bool(re.match(timestamp_pattern, timestamp))

    @staticmethod
    def normalize_timestamp(timestamp):
        """
        Normalize timestamp to consistent HH:MM:SS format
        """
        # Split timestamp into components
        parts = timestamp.split(':')
        
        # Pad or truncate to ensure consistent format
        if len(parts) == 2:
            # MM:SS format - prepend 00 for hours
            parts.insert(0, '00')
        elif len(parts) == 3:
            # HH:MM:SS format - ensure each part is two digits
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
        # Remove markdown formatting
        clean_text = strip_markdown.strip_markdown(gentext)
        
        # Split the input into lines
        lines = clean_text.split('\n')
        
        # Format each line into "timestamp - description"
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to split line into timestamp and description
            match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*(.*)$', line)
            
            if match:
                timestamp, description = match.groups()
                
                # Validate timestamp
                if not TimestampFormatter.validate_timestamp(timestamp):
                    # If timestamp is invalid, add the whole line
                    formatted_lines.append(line)
                    continue
                
                # Normalize timestamp
                normalized_timestamp = TimestampFormatter.normalize_timestamp(timestamp)
                
                # Truncate description if too long
                if description and len(description) > max_description_length:
                    description = description[:max_description_length] + '...'
                
                # Format line
                formatted_line = f"{normalized_timestamp} - {description.strip()}"
                formatted_lines.append(formatted_line)
            else:
                # If no clear timestamp, add the line as-is
                formatted_lines.append(line)
        
        # Join the formatted lines into a single output
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
            
            # Convert timestamp to seconds
            time_parts = timestamp.split(':')
            if len(time_parts) == 2:
                seconds = int(time_parts[0]) * 60 + int(time_parts[1])
            elif len(time_parts) == 3:
                seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
            else:
                return match.group(0)
            
            # Create hyperlink
            hyperlink = f"[{timestamp}]({video_url}&t={seconds}s) - {description}"
            return hyperlink
        
        # Regex to match timestamp format
        timestamp_pattern = r'^(\d{2}:\d{2}(?::\d{2})?) - (.*)$'
        return re.sub(timestamp_pattern, create_youtube_timestamp_link, 
                      formatted_timestamps, flags=re.MULTILINE)

# Example usage demonstration
if __name__ == "__main__":
    # Test cases
    sample_text = """
    00:30 Introduction to the video topic
    03:45 First main point explained
    12:15 Second key concept
    25:50 Concluding remarks
    """
    
    # Basic formatting
    formatted = TimestampFormatter.format(sample_text)
    print("Basic Formatting:")
    print(formatted)
    
    # With hyperlinks (hypothetical video URL)
    video_url = "https://www.youtube.com/watch?v=example_video"
    hyperlinked = TimestampFormatter.hyperlink_timestamps(formatted, video_url)
    print("\nHyperlinked Timestamps:")
    print(hyperlinked)