from collections import defaultdict


class TelemetryAnalyzer:

    def __init__(self, events):

        self.events = events

    def layer_summary(self):

        summary = defaultdict(list)

        for event in self.events:

            summary[event["layer"]].append(
                event["latency_ms"]
            )

        return summary

    def latency_report(self):

        summary = self.layer_summary()

        report = {}

        for layer, latencies in summary.items():

            report[layer] = {

                "calls": len(latencies),

                "avg_latency_ms":
                    sum(latencies) / len(latencies),

                "max_latency_ms":
                    max(latencies),

                "min_latency_ms":
                    min(latencies)
            }

        return report