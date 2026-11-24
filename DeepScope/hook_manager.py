import torch
import time

#Hooks are called internally (automatically) by pytorch, after a layer is being a executed
#Its like an internal logger

def create_pre_hook(start_times):
    def pre_hook(module, input):

        start_times[module] = time.perf_counter()

    return pre_hook

def get_layer_type(layer_name):

    if "attn" in layer_name:
        return "ATTENTION"

    if "mlp" in layer_name:
        return "MLP"

    if "ln" in layer_name:
        return "LAYER_NORM"

    if "embed" in layer_name or "wte" in layer_name or "wpe" in layer_name:
        return "EMBEDDING"

    if "lm_head" in layer_name:
        return "OUTPUT"

    return "OTHER"

def get_block_number(layer_name):

    parts = layer_name.split(".")

    for i in range(len(parts)):

        if parts[i] == "h" and i + 1 < len(parts):

            try:
                return int(parts[i + 1])
            except:
                break

    return -1

def create_hook(layer_name, collector,start_times):

    def hook(module, input, output):

        if isinstance(output, torch.Tensor):
            end_time = time.perf_counter()
            start_time = start_times[module]
            latency_ms = (end_time - start_time) * 1000
            device = str(output.device)
            dtype = str(output.dtype)
            SPARSITY_THRESHOLD = 0.05

            sparsity = (
                (output.abs() < SPARSITY_THRESHOLD)
                .float()
                .mean()
                .item()
            )

            event = {
                "timestamp": time.strftime("%H:%M:%S"),
                "layer": layer_name,
                "layer_type": get_layer_type(layer_name),
                "block": get_block_number(layer_name),
                "shape": list(output.shape),
                "mean": output.mean().item(),   #item is added to get float, 
                "std": output.std().item(),     #otherwise output is in tensor
                "min": output.min().item(),
                "max": output.max().item(),
                "latency_ms": latency_ms,
                "device": device,
                "dtype": dtype,
                "sparsity": sparsity
            }

            collector.add_event(event)

    return hook


def register_hooks(model, collector):

    handles = []
    start_times={}

    for name, module in model.named_modules():

        if len(list(module.children())) == 0:

            pre_handle = module.register_forward_pre_hook(create_pre_hook(start_times))

            post_handle = module.register_forward_hook(
                create_hook(name, collector,start_times)
            )

            handles.append(pre_handle)
            handles.append(post_handle)

    return handles