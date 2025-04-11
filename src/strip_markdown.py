import re

def strip_markdown(text):
    """
    Strip markdown formatting from text

    Args:
        text (str): Text containing markdown formatting

    Returns:
        str: Plain text with markdown formatting removed
    """
    if not text:
        return ""
        
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
   
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    text = re.sub(r'^\>\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    
    text = re.sub(r'```.*?\n(.*?)```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    text = re.sub(r'^\-{3,}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)
    
    return text
