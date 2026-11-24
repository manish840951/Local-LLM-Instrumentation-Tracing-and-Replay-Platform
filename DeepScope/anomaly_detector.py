class AnomalyDetector:

    def __init__(self):
        self.anomalies = []
        self.seen = set()

    def get_anomalies(self):
        return self.anomalies

    def add_anomaly(self, severity, layer, message, value=None):

        key = (severity, layer, message)

        if key in self.seen:
            return

        self.seen.add(key)

        anomaly = {
            "severity": severity,
            "layer": layer,
            "message": message
        }

        if value is not None:
            anomaly["value"] = round(value, 4)

        self.anomalies.append(anomaly)

    def analyze_event(self, event):

        std = event.get("std", 0)
        max_value = abs(event.get("max", 0))
        latency = event.get("latency_ms", 0)
        sparsity = event.get("sparsity", 0)

        if std > 8:
            self.add_anomaly(
                "WARN",
                event["layer"],
                "Very high activation variance",
                std
            )

        if max_value > 20:
            self.add_anomaly(
                "WARN",
                event["layer"],
                "Very large activation detected",
                max_value
            )

        if latency > 20:
            self.add_anomaly(
                "INFO",
                event["layer"],
                "Slow layer execution",
                latency
            )

        if sparsity > 0.80:
            self.add_anomaly(
                "INFO",
                event["layer"],
                "High sparsity detected",
                sparsity
            )
# class AnomalyDetector:

#     def __init__(self):
#         self.anomalies = []

#     def get_anomalies(self):
#         return self.anomalies
    
#     def analyze_event(self, event):

#         if event["std"] > 5:

#             self.anomalies.append(
#                 {
#                     "severity": "WARN",
#                     "layer": event["layer"],
#                     "message": "High activation variance"
#                 }
#             )

#         if abs(event["max"]) > 10:

#             self.anomalies.append(
#                 {
#                     "severity": "WARN",
#                     "layer": event["layer"],
#                     "message": "Large activation detected"
#                 }
#             )

#         if event["latency_ms"] > 5:

#             self.anomalies.append(
#                 {
#                     "severity": "INFO",
#                     "layer": event["layer"],
#                     "message": "Slow layer execution"
#                 }
#             )