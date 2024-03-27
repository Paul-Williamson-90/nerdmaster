ADD_TO_LONG_TERM = """{background}

Based on this character's background, views and beliefs, what important details would they likely remember in the long-term from the following short-term memories?
{short_term}

Write the character's long-term memory below in first-person perspective, like a diary entry:
"""

SEARCH_SHORT_TERM = """Short Term Memories:
{short_term}

Based on the short-term memories, does the character remember anything related to the following query?
{query}

Recall:
"""

SEARCH_MEMORY = """**Short Term Memories**:
{short_term}

**Long Term Memories**:
{long_term}

**Query**:
{query}

**Write the character's recall in first-person perspective, like inner-thoughts:**
"""

SEARCH_MEMORY_SYSTEM = """Based on the character's memories, does the character remember anything related to the following query?"""