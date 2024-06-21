short_book_generator_prompt = """
You are an AI writing assistant tasked with creating a short book on a specific subtopic from a larger book. The input you will receive includes:

1. A brief summary of the subtopic (1-2 sentences)
2. The context around the subtopic from the original book (a few paragraphs)

Your task is to use the provided summary and context to generate a well-formatted and comprehensive short book on the subtopic, following the given structure and guidelines.

Subtopic Summary: {subtopic_summary}

Context from the Book: {context}

Your short book should include the following sections:

1. Introduction (1-2 paragraphs): Provide an overview of the subtopic and its relevance or importance, deriving information from the provided context.

2. Background (2-4 paragraphs): Give necessary background information, historical context, or foundational concepts related to the subtopic, based on the provided context.

3. Key Points (3-5 sections, each with 2-4 paragraphs): Elaborate on the main ideas, theories, or components of the subtopic, using the provided context as a starting point, and expanding on it with your own knowledge and understanding.

4. Examples (1-2 paragraphs per key point): Provide real-world examples, case studies, or practical applications to illustrate each key point, drawing from the context and your own knowledge.

5. Conclusion (1-2 paragraphs): Summarize the main takeaways and potential future developments or research directions related to the subtopic, based on the information in the context and your own understanding.

Additionally, your short book should:

- Use appropriate section headings and subheadings for better organization.
- Include in-text citations or references to the original book when using direct quotes or paraphrasing from the provided context.
- Maintain a consistent and easy-to-follow writing style suitable for a general audience.
- Be around 2,000-3,000 words in length.
- Keep the content focused on the provided subtopic summary and context, while expanding on it with your own knowledge and understanding.

Please let me know if you need any clarification or have additional requirements for the short book.
"""

SHORT_BOOk_GENERATOR = """
You are an AI tasked with creating a short book on a subtopic from a larger book. 
Generate a short book with the following sections:

1. Introduction (1-2 paragraphs)
2. Background (2-4 paragraphs)  
3. Key Points (3-5 sections, 2-4 paragraphs each)
4. Examples (1-2 paragraphs per key point)
5. Conclusion (1-2 paragraphs)

Guidelines:
- Use section headings/subheadings
- Cite original book when quoting/paraphrasing
- 1000-2000 words

Output: A formatted short book on the subtopic.

Input:
1. Subtopic Summary: {subtopic_summary}
2. Context from Book: {context}

Output:

"""

BOOK_GENERATOR = """
Support the prompt using provided context.

Prompt : {subtopic_summary}
Context: {context}

Output:
"""

# Performance Requirements: The requirements cover various aspects like color rendering, illumination, spatial frequency response, resolution, mechanical interface, safety measures, and noise levels.
# |
# Functional Requirements: The system should have functions like brightness, gamma, sharpness, color adjustment, white balance, screen freeze, image magnification, endoscopic mode switching, language selection, shortcut buttons, video/photo capture, data storage, reset, and soft lens interface.
