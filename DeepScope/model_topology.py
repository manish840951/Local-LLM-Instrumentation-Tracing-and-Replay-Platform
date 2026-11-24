class ModelTopology:

    def __init__(self, model):

        self.model = model

    def build_tree(self):

        tree = {}

        for name, module in self.model.named_modules():

            if name == "":
                continue

            parts = name.split(".")

            current = tree

            for part in parts:

                if part not in current:
                    current[part] = {}

                current = current[part]

        return tree