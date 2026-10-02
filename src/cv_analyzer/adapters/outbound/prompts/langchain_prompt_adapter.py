from __future__ import annotations

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from cv_analyzer.adapters.outbound.prompts.templates import (
    CV_EVALUATION_HUMAN_TEMPLATE,
    CV_EVALUATION_SYSTEM_TEMPLATE,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)


class LangChainPromptAdapter(PromptGeneratorPort):
    """Outbound adapter implementing prompt generation using langchain_core."""

    DEFAULT_SYSTEM_TEMPLATE = CV_EVALUATION_SYSTEM_TEMPLATE
    DEFAULT_HUMAN_TEMPLATE = CV_EVALUATION_HUMAN_TEMPLATE

    def generate_cv_analysis_prompt(
        self,
        system_template: str | None = None,
        human_template: str | None = None,
    ) -> ChatPromptTemplate:
        """Generate ChatPromptTemplate using SystemMessagePromptTemplate and HumanMessagePromptTemplate.

        Args:
            system_template: Optional system prompt template string.
            human_template: Optional human prompt template string.

        Returns:
            Constructed ChatPromptTemplate via ChatPromptTemplate.from_messages.
        """
        sys_tmpl = system_template or self.DEFAULT_SYSTEM_TEMPLATE
        human_tmpl = human_template or self.DEFAULT_HUMAN_TEMPLATE

        system_message = SystemMessagePromptTemplate.from_template(sys_tmpl)
        human_message = HumanMessagePromptTemplate.from_template(human_tmpl)

        return ChatPromptTemplate.from_messages([system_message, human_message])
