class Prompt:
    @staticmethod
    def prompt1(ID=0):
        if ID == 0:
            prompt_text = """Your task: Create a captivating, detailed, and engaging summary of a video transcript that offers comprehensive insights into the content, while remaining concise and informative.

Guidelines:
    1. **Focus on Key Details**: Highlight the core messages, supporting arguments, and notable moments from the video in a structured format.
    2. **Organize into Sections**: Break down the summary into:
        - Introduction: Briefly introduce the video's context and main subject.
        - Key Points:
            - Subsection 1: Discuss the first major aspect with relevant details.
            - Subsection 2: Include the next significant point with clarity.
            - Continue organizing additional key points into subsections.
        - Conclusion: Wrap up with the video's primary takeaways, leaving a strong impression on the audience.
    3. **Word Count**: Aim for up to 300 words to provide depth without losing conciseness.
    4. **Tailor the Tone**: Adapt the tone to align with the intended audience (professional, casual, etc.).

Additional Recommendations:
    - Use storytelling elements to make the summary engaging.
    - Ensure the summary is free of grammatical issues or typos.
    - Include compelling language and vivid descriptions to maintain interest.

By following these guidelines, you can craft summaries that engage readers, encapsulate the video's essence, and invite further exploration."""

        elif ID == "timestamp":
            prompt_text = """Your task: Generate detailed and precise timestamps for the key topics discussed in a video, making navigation and content consumption effortless.

Instructions:
    1. Identify major chapters or topics from the video transcript and create clear, concise titles.
    2. Format timestamps as **hh:mm:ss** and provide clickable URLs using the video link.
    3. Present the output in Markdown format:
        - [hh:mm:ss](%VIDEO_URL?t=seconds) Topic Title
        - Example:
            1. [00:03:12](https://youtu.be/hCaXor?t=192) Introduction
            2. [00:12:45](https://youtu.be/hCaXor?t=765) Key Topic 1
            3. [00:25:30](https://youtu.be/hCaXor?t=1530) Key Topic 2

Enhancements:
    - Include subheadings for segments within the main chapters if necessary.
    - Ensure topics are concise but descriptive enough to summarize the segment effectively.
    - Highlight transitions or pivotal moments to help the audience navigate the content better.

**Markdown Output**:
1. hh:mm:ss %Topic Title%
2. hh:mm:ss %Topic Title%
3. hh:mm:ss %Topic Title% ..."""

        elif ID == "transcript":
            prompt_text = """Your task: Generate an expanded transcription with enhanced formatting and structure that is optimized for clarity and readability.

    Guidelines:
        1. **Maintain Accuracy**: Ensure the transcription accurately reflects the video's audio, including speaker identifiers, pauses, and contextually relevant sounds.
        2. **Segment by Topic**: Divide the transcription into clearly defined sections or paragraphs based on content flow.
        3. **Include Timestamps**: Add timestamps every 30 seconds or at the start of significant topics for easy navigation.
        4. **Use Visual Cues**:
        - Use **bold** for key terms, phrases, or names.
        - Italicize emphasis where needed.
        - Format speaker labels consistently (e.g., **[Speaker Name]**: Dialogue).
        5. **Add Context**: Include non-verbal cues or descriptions of significant visual actions (e.g., *[Audience applauds]*, *[Presenter writes on the board]*).

    By ensuring the transcript is clear, well-organized, and visually accessible, you can provide a detailed, reader-friendly representation of the video's content."""
        else:
            prompt_text = "NA"

        return prompt_text
