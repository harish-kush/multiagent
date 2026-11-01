from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url
from dotenv import load_dotenv
import os
load_dotenv()

gemini = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=gemini)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt="""
        You are a web research agent.
        Always call web_search for every research request.
        Do not ask the user for clarification.
        Interpret broad topics intelligently.
        Preserve all returned URLs and search results.
        Never invent search results.
        """
    )


def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt="""
        You are a web scraping research agent.
        Extract URLs from the provided search results.
        Always call scrape_url for relevant URLs.
        Scrape up to 3 relevant URLs.
        Preserve the source URLs.
        Never invent scraped content.
        """
    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert research writer.

    Your job is to create accurate and well-structured
    research reports using only the provided research data.

    STRICT RULES:
    1. Never invent facts, statistics, dates or events.
    2. Never assume an event has happened just because
       it is mentioned as upcoming.
    3. Clearly distinguish between past, ongoing and
       upcoming events.
    4. Do not convert predictions into confirmed results.
    5. Every factual claim must be supported by research.
    6. If sources contradict each other, mention it.
    7. If information is insufficient, explicitly say so.
    8. Include source URLs alongside relevant findings.
    9. Never fabricate publication dates.
    """),

    ("human", """
    Write a detailed research report.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure:
    - Introduction
    - Key Findings (minimum 3 points, if evidence permits)
    - Conclusion
    - Sources

    Use only verified information from the research.
    """)
])


writer_chain = writer_prompt | llm | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a strict research fact-checker.

    Compare the report against the original research data.

    Check:
    1. Whether claims are supported by sources.
    2. Whether dates and timelines are accurate.
    3. Whether predictions are presented as facts.
    4. Whether any information is fabricated.
    5. Whether source URLs support the claims.

    Penalize unsupported claims heavily.
    """),

    ("human", """
    Original Research:
    {research}

    Research Report:
    {report}

    Provide:
    Score: X/10
    Strengths:
    Areas to Improve:
    One line verdict:
    """)
])

critic_chain = critic_prompt | llm | StrOutputParser()