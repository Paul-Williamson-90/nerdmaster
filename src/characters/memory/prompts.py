ADD_TO_LONG_TERM = """{background}

Based on this character's background, views and beliefs, what important details would they likely remember in the long-term from the following short-term memories?
{short_term}

Write the character's long-term memory below in first-person perspective, like a diary entry:
"""

SEARCH_SHORT_TERM = """Short Term Memories:
{short_term}

Based on the short-term memories, does the character remember anything related to the following query?
"""

SEARCH_MEMORY_SYSTEM = """Here are some memories for a character you are playing called {name} in a text-based game.

**Memories**:
{short_term}
{long_term}

Based on the character's memories, does the character remember anything related to the following query?
Your output should be in first-person perspective as if the character is recalling the memory.
Be concise and do not make up any facts or perceptions that are not in the provided memories.

For example, starting with:
"I seem to remember..."
"""

SEARCH_MEMORY = """**Query**:
{query}

**Answer**:
"""