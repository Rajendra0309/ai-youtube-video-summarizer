class Prompt:
    @staticmethod
    def prompt1(ID=0, language="English"):
        lang_instruction = f"\n\nIMPORTANT: Provide your response in {language}. If the transcript is in a different language, still provide the output in {language}."

        if ID == 0:
            prompt_text = f"""Comprehensive Video Summary Generation Task

Objective: Create an engaging, insightful, and concise summary that captures the essence of the video while providing maximum value to the reader.

Detailed Guidelines:
    1. **Content Structure**
    - Craft a compelling introduction that sets the context
    - Systematically break down key points into clear subsections
    - Conclude with impactful takeaways and broader implications

    2. **Content Depth**
    - Extract core messages and critical insights
    - Balance technical details with accessible language
    - Highlight unique perspectives or novel information

    3. **Formatting Recommendations**
    - Use markdown for enhanced readability
    - Bold key terms and concepts
    - Create a logical flow between sections
    - Maintain a professional yet engaging tone

    4. **Analytical Approach**
    - Identify and explain the video's primary thesis
    - Provide context for complex ideas
    - Connect individual points to the overarching narrative

    5. **Audience Considerations**
    - Adapt complexity to target audience
    - Use clear, precise language
    - Avoid jargon unless explicitly explained

Specific Requirements:
    - Total Length: 250-350 words
    - Clarity: Crystal clear explanations
    - Objectivity: Balanced and neutral perspective
    - Engagement: Make the summary compelling and informative

Evaluation Criteria:
    - Accuracy of content representation
    - Clarity of explanation
    - Comprehensive coverage
    - Readability and flow{lang_instruction}"""

        elif ID == "timestamp":
            prompt_text = f"""Timestamp Generation Task

            Guidelines:
                1. Generate precise timestamps for key video segments
                2. Format: [HH:MM:SS] Concise Topic Description
                3. Limit each description to one clear, short line
                4. Focus on capturing the main point of each segment
                5. Ensure timestamps reflect significant content transitions

            Output Format Example:
                1. [00:02:15] Video Introduction
                2. [00:12:45] Main Argument Presentation
                3. [00:25:30] Key Findings and Insights
                4. [00:40:22] Conclusion and Takeaways

            Execution Principles:
                - Be precise
                - Use clear, succinct language
                - Capture the essence of each segment{lang_instruction}"""

        elif ID == "transcript":
            prompt_text = f"""Advanced Transcript Transformation Guidelines

Comprehensive Transcript Generation Objectives:
    1. **Structural Integrity**
    - Transform spoken word into readable text
    - Maintain original meaning and tone
    - Create a narrative-like reading experience

    2. **Formatting Excellence**
    Detailed Formatting Specifications:
    - Use markdown for enhanced readability
    - **Bold** key concepts and critical terms
    - *Italicize* for emotional emphasis
    - Insert [Contextual Annotations] for non-verbal cues

    3. **Speaker Dynamics**
    - **[Speaker Name]**: Clearly identify speakers
    - Preserve speaking style and nuance
    - Handle multi-speaker scenarios with clarity

    4. **Timestamp Integration**
    - Insert timestamps at section transitions
    - Format: **[00:05:30]** Section Heading
    - Provide seamless navigation references

    5. **Linguistic Refinement**
    - Remove filler words strategically
    - Correct minor grammatical inconsistencies
    - Maintain natural conversational flow

    6. **Contextual Enrichment**
    - Add explanatory notes for technical terms
    - Provide background information when necessary
    - Create a comprehensive reading experience

    7. **Accessibility Considerations**
    - Ensure clear, readable formatting
    - Break complex discussions into digestible paragraphs
    - Support multiple comprehension levels

Special Directives:
    - Prioritize comprehensive understanding
    - Balance technical accuracy with readability
    - Transform spoken content into an engaging document{lang_instruction}"""

        else:
            prompt_text = "Invalid prompt request"

        return prompt_text