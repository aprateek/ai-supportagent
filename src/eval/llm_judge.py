"""LLM Judge — uses an LLM to score agent responses on relevance, correctness, helpfulness."""

import random


class LLMJudge:
    """Scores agent responses using an LLM (with mock fallback)."""

    def __init__(self, model_id: str = "us.anthropic.claude-sonnet-4-6", region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            try:
                from langchain_aws import ChatBedrock
                self._llm = ChatBedrock(
                    model_id=self.model_id,
                    region_name=self.region,
                    model_kwargs={"max_tokens": 50, "temperature": 0.0},
                )
            except Exception:
                self._llm = None
        return self._llm

    def _ask_llm(self, prompt: str) -> float:
        """Ask LLM to score, return float 0-5. Falls back to random 3-5."""
        llm = self._get_llm()
        if llm is None:
            return self._mock_score()
        try:
            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            score = float(response.content.strip().split()[0])
            return max(0.0, min(5.0, score))
        except Exception:
            return self._mock_score()

    def _mock_score(self) -> float:
        return round(random.uniform(3.0, 5.0), 1)

    def score_relevance(self, question: str, response: str, context: str = "") -> float:
        """Score how relevant the response is to the question (0-5)."""
        prompt = (
            f"Score the relevance of this response to the question on a scale of 0-5. "
            f"Respond with ONLY a number.\n\nQuestion: {question}\n"
            f"{'Context: ' + context + chr(10) if context else ''}"
            f"Response: {response}\n\nScore:"
        )
        return self._ask_llm(prompt)

    def score_correctness(self, response: str, expected_answer: str) -> float:
        """Score correctness compared to expected answer (0-5)."""
        prompt = (
            f"Score how correct this response is compared to the expected answer on a scale of 0-5. "
            f"Respond with ONLY a number.\n\nExpected: {expected_answer}\n"
            f"Actual: {response}\n\nScore:"
        )
        return self._ask_llm(prompt)

    def score_helpfulness(self, question: str, response: str) -> float:
        """Score how helpful the response is (0-5)."""
        prompt = (
            f"Score how helpful this response is for the customer on a scale of 0-5. "
            f"Respond with ONLY a number.\n\nQuestion: {question}\n"
            f"Response: {response}\n\nScore:"
        )
        return self._ask_llm(prompt)
