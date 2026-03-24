from prometheus_client import Counter, Histogram

incidents_processed_total = Counter(
    "incidents_processed_total",
    "Total number of incidents fully processed by the worker",
)

analysis_duration_seconds = Histogram(
    "analysis_duration_seconds",
    "Time spent running LLM analysis per incident",
    buckets=(1, 2, 5, 10, 30, 60, 120, float("inf")),
)
