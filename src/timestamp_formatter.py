import strip_markdown

class TimestampFormatter:

    @staticmethod
    def format(gentext):
        # Remove markdown formatting
        clean_text = strip_markdown.strip_markdown(gentext)
        
        # Split the input into lines based on timestamps
        lines = clean_text.split('\n')
        
        # Format each line into "timestamp - description"
        formatted_lines = []
        for line in lines:
            if line.strip():  # Ignore empty lines
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    timestamp, description = parts
                    formatted_lines.append(f"{timestamp} - {description}")
                else:
                    formatted_lines.append(line.strip())  # Handle cases without descriptions

        # Join the formatted lines into a single output
        return '\n'.join(formatted_lines)
