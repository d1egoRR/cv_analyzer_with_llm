from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from cv_analyzer.adapters.outbound.prompts.langchain_prompt_adapter import (
    LangChainPromptAdapter,
)


def test_generate_cv_analysis_prompt_default_structure() -> None:
    """Test that generate_cv_analysis_prompt returns ChatPromptTemplate with expected message types."""
    adapter = LangChainPromptAdapter()
    chat_prompt = adapter.generate_cv_analysis_prompt()

    assert isinstance(chat_prompt, ChatPromptTemplate)
    assert len(chat_prompt.messages) == 2
    assert isinstance(chat_prompt.messages[0], SystemMessagePromptTemplate)
    assert isinstance(chat_prompt.messages[1], HumanMessagePromptTemplate)


def test_generate_cv_analysis_prompt_default_content_formatting() -> None:
    """Test formatting the default ChatPromptTemplate with job description and CV text."""
    adapter = LangChainPromptAdapter()
    chat_prompt = adapter.generate_cv_analysis_prompt()

    job_desc = "Senior Backend Developer - Python/FastAPI"
    cv_text = "Experienced Developer with 6 years in Python"

    messages = chat_prompt.format_messages(
        job_description=job_desc,
        cv_text=cv_text,
    )

    assert len(messages) == 2
    system_msg, human_msg = messages[0], messages[1]

    assert "Eres un evaluador técnico exigente y riguroso" in system_msg.content
    assert job_desc in human_msg.content
    assert cv_text in human_msg.content


def test_generate_cv_analysis_prompt_custom_templates() -> None:
    """Test creating a prompt template with custom system and human templates."""
    adapter = LangChainPromptAdapter()
    custom_system = "Custom System: {sys_val}"
    custom_human = "Custom Human: {human_val}"

    chat_prompt = adapter.generate_cv_analysis_prompt(
        system_template=custom_system,
        human_template=custom_human,
    )

    messages = chat_prompt.format_messages(
        sys_val="System Context",
        human_val="Human Query",
    )

    assert messages[0].content == "Custom System: System Context"
    assert messages[1].content == "Custom Human: Human Query"
