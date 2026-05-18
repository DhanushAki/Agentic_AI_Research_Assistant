from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

# Initialize the search runner
ddg_search = DuckDuckGoSearchRun()

@tool
def search_web(query: str):
    """
    Search the internet for real-time information, news, or general knowledge. 
    Use this for any questions that are NOT about the user's specific uploaded documents.
    """
    print(f"--- WEB SEARCH: Searching for '{query}' ---")
    try:
        results = ddg_search.invoke(query)
        return results
    except Exception as e:
        return f"Error searching the web: {str(e)}"

if __name__ == "__main__":
    # Test it
    print(search_web.invoke("Who won the Oscars 2026?"))
