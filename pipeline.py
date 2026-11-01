from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def get_tool_outputs(result):
    """Extract actual tool responses from agent messages."""

    outputs = []

    for message in result.get("messages", []):
        if getattr(message, "type", None) == "tool":
            outputs.append(str(message.content))

    return "\n\n".join(outputs)


def get_scraped_sources(result):
    """[NEW] Pair each scrape_url call's URL with the text it returned."""

    urls = {}
    sources = []

    for message in result.get("messages", []):
        for call in getattr(message, "tool_calls", None) or []:
            urls[call.get("id")] = (call.get("args") or {}).get("url", "")

        if getattr(message, "type", None) == "tool":
            sources.append({
                "url": urls.get(getattr(message, "tool_call_id", None), ""),
                "content": str(message.content),
            })

    return sources


def run_research_pipeline(topic: str, on_progress=None) -> dict:
    """
    on_progress (optional): callable(stage, status)
      stage  in {"search", "reader", "writer", "critic"}
      status in {"running", "completed", "failed"}
    """

    def emit(stage, status):
        if on_progress:
            on_progress(stage, status)

    state = {}

    # STEP 1: SEARCH AGENT
    print("\n" + " =" * 50)
    print("STEP 1 - Search Agent is working...")
    print("=" * 50)

    emit("search", "running")
    try:
        search_agent = build_search_agent()

        search_result = search_agent.invoke({
            "messages": [
                ("user", f"Find recent and reliable information about: {topic}")
            ]
        })

        # Extract actual Tavily tool response
        state["search_results"] = get_tool_outputs(search_result)
    except Exception:
        emit("search", "failed")
        raise

    if not state["search_results"]:
        print("\nSearch Agent did not call the search tool.")
        print("Agent response:",
              search_result["messages"][-1].content)
        emit("search", "failed")
        return {"error": "No actual search results retrieved."}

    emit("search", "completed")
    print("\nSearch Results:\n", state["search_results"])

    # STEP 2: READER AGENT
    print("\n" + " =" * 50)
    print("STEP 2 - Reader Agent is scraping resources...")
    print("=" * 50)

    emit("reader", "running")
    try:
        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke({
            "messages": [
                ("user",
                 f"""
                 Research Topic: {topic}

                 Below are the actual search results:

                 {state['search_results']}

                 Extract the URLs from these results.
                 Select up to 3 relevant URLs.
                 Use scrape_url on each URL.
                 Return the extracted website content with source URLs.
                 Do not invent any content.
                 """)
            ]
        })

        # Extract actual scraping tool responses
        state["scraped_content"] = get_tool_outputs(reader_result)
        state["scraped_sources"] = get_scraped_sources(reader_result)  # [NEW]
    except Exception:
        emit("reader", "failed")
        raise

    if not state["scraped_content"]:
        print("\nReader Agent did not call the scraping tool.")
        print("Agent response:",
              reader_result["messages"][-1].content)
        emit("reader", "failed")
        return {
            "error": "No website content scraped.",
            "search_results": state["search_results"]
        }

    emit("reader", "completed")
    print("\nScraped Content:\n", state["scraped_content"])

    # STEP 3: WRITER CHAIN
    print("\n" + " =" * 50)
    print("STEP 3 - Writer is drafting the report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    emit("writer", "running")
    try:
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
    except Exception:
        emit("writer", "failed")
        raise
    emit("writer", "completed")

    print("\nFinal Report:\n", state["report"])

    # STEP 4: CRITIC CHAIN
    print("\n" + " =" * 50)
    print("STEP 4 - Critic is reviewing the report...")
    print("=" * 50)

    emit("critic", "running")
    try:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"],
            "research": research_combined
        })
    except Exception:
        emit("critic", "failed")
        raise
    emit("critic", "completed")

    print("\nCritic Report:\n", state["feedback"])

    return state


if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    result = run_research_pipeline(topic)