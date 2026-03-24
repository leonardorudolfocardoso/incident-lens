import os

from openai import OpenAI
from pydantic import BaseModel

from incident_lens.logging_config import get_logger

logger = get_logger(__name__)


class _Analysis(BaseModel):
    summary: str
    suspected_service: str
    confidence: float
    recommendations: list[str]


def analyze(logs: list[str], service_name: str, alert_type: str) -> _Analysis:
    logger.debug(
        "calling_openai",
        service_name=service_name,
        alert_type=alert_type,
        log_count=len(logs),
    )
    response = OpenAI(api_key=os.environ["OPENAI_API_KEY"]).beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an incident analyst. Given the logs, service name, and alert type, "
                    "provide a concise summary, identify the suspected service, your confidence "
                    "level (0.0-1.0), and actionable recommendations."
                ),
            },
            {
                "role": "user",
                "content": f"Service: {service_name}\nAlert: {alert_type}\nLogs:\n"
                + "\n".join(logs),
            },
        ],
        response_format=_Analysis,
    )
    return response.choices[0].message.parsed
