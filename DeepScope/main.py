import torch
import os
os.environ["HF_HOME"] = r"D:\hf_cache"
from model_loader import load_model
from hook_manager import register_hooks
from telemetry_collector import TelemetryCollector
from telemetry_analyzer import TelemetryAnalyzer
from model_topology import ModelTopology
from anomaly_detector import AnomalyDetector
from attention_buffer import AttentionBuffer
from attention_renderer import AttentionRenderer
from telemetry_collector import latest_metrics
import transformers
import json
import time



model, tokenizer = load_model()
text = "DeepScope is monitoring GPT2"

inputs = tokenizer(
    text,
    return_tensors="pt"
)

outputs = model(
    **inputs
)

collector = TelemetryCollector()

handles = register_hooks(
    model,
    collector
)

text = """
Artificial intelligence is transforming
the way software is built and tested.
"""

inputs = tokenizer(
    text,
    return_tensors="pt"
)

tokens = tokenizer.convert_ids_to_tokens(
    inputs["input_ids"][0]
)

latest_metrics["token_labels"] = tokens

print("\nRunning inference...\n")

with torch.no_grad():

    outputs = model(
        **inputs,
        output_attentions=True
    )


print("Transformers:", transformers.__version__)

print(
    "Config output_attentions:",
    getattr(model.config, "output_attentions", None)
)

print(
    "Attention implementation:",
    getattr(model.config, "_attn_implementation", "not found")
)


attention_buffer = AttentionBuffer()
for layer_idx, attn in enumerate(outputs.attentions):

    
    attention_buffer.add(
        {
            "layer": layer_idx,
            "heads": attn.shape[1],
            "seq_len": attn.shape[2],
            "attention": attn.cpu()
        }
    )
    

renderer = AttentionRenderer()
records = attention_buffer.get_all()


latest_metrics["attention_layer"] = 0
latest_metrics["attention_head"] = 0

# Export all layers and all heads
attention_layers = []

for record in records:
    layer_heads = []

    for head_idx in range(record["heads"]):
        layer_heads.append(
            record["attention"][0, head_idx].tolist()
        )

    attention_layers.append(layer_heads)

latest_metrics["attention_layers"] = attention_layers

latest_metrics["available_attention_layers"] = len(attention_layers)

if attention_layers:
    latest_metrics["available_attention_heads"] = len(attention_layers[0])
    latest_metrics["attention_heads"] = attention_layers[0]
    latest_metrics["attention_matrix"] = attention_layers[0][0]
else:
    latest_metrics["available_attention_heads"] = 0
    latest_metrics["attention_heads"] = []
    latest_metrics["attention_matrix"] = []

latest_metrics["tokens"] = inputs["input_ids"].shape[1]
latest_metrics["attention_mean"] = records[0]["attention"].mean().item()
latest_metrics["status"] = "Inference completed"

num_heads = records[0]["attention"].shape[1]

for head in range(num_heads):

    print(f"\n===== HEAD {head} =====\n")

    matrix = records[0]["attention"][0, head]

    renderer.render(matrix)


events = collector.get_events()

#print("\nSample Events\n")

#for event in events[:10]:
#    print(event)

#print("\nGenerating Report...\n")

detector = AnomalyDetector()
for event in events:
    detector.analyze_event(event)

latest_metrics["alerts"] = detector.get_anomalies()

#for anomaly in detector.get_anomalies():
#    print(anomaly)

analyzer = TelemetryAnalyzer(events)

report = analyzer.latency_report()
latest_metrics["latency_layers"] = len(report)
latest_metrics["events"] = events[-20:]
latest_metrics["model"] = {
    "name": "gpt2",
    "layers": model.config.n_layer,
    "heads": model.config.n_head,
    "hidden_size": model.config.n_embd
}


#for layer, stats in report.items():

#    print(f"\nLayer: {layer}")

#    print(
#        f"Calls: {stats['calls']}"
#    )

#    print(
#        f"Avg Latency: {stats['avg_latency_ms']:.4f} ms"
#    )

#    print(
#        f"Max Latency: {stats['max_latency_ms']:.4f} ms"
#    )

#    print(
#        f"Min Latency: {stats['min_latency_ms']:.4f} ms"
#    )

topology = ModelTopology(model)
os.makedirs("runs", exist_ok=True)
tree = topology.build_tree()
latest_metrics["topology"] = tree
run_files = sorted(os.listdir("runs"))
latest_metrics["available_replays"] = run_files


with open("metrics.json", "w") as f:
    json.dump(latest_metrics, f, indent=4)


#os.makedirs("runs", exist_ok=True)


run_name = time.strftime("run_%Y%m%d_%H%M%S.json")
run_path = os.path.join("runs", run_name)

with open(run_path, "w") as f:
    json.dump(latest_metrics, f, indent=4)

print(f"Saved replay trace: {run_path}")
#print(tree) 

for handle in handles:
    handle.remove()