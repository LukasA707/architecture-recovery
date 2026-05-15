import ast
from pathlib import Path 
import matplotlib.pyplot as plt
import networkx as nx

CODE_ROOT_FOLDER="../zeeguu-api/"

def file_path(file_name):
    return CODE_ROOT_FOLDER+file_name

assert (file_path("zeeguu/core/model/user.py") == "../zeeguu-api/zeeguu/core/model/user.py")

def module_name_from_file_path(full_path):
    file_name = full_path[len(CODE_ROOT_FOLDER):]
    file_name = file_name.replace("/__init__.py","")
    file_name = file_name.replace("/",".")
    file_name = file_name.replace(".py","")
    return file_name

def is_relevant_module(module_name):
    if "test" in module_name:
        return False

    if module_name.startswith("zeeguu"):
        return True

    return False

def imports_from_file(file_name):

    imports = []

    source = open(file_name, encoding="utf-8").read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.append(node.module)


    return imports

imports_from_file(file_path(file_path('zeeguu/core/model/user.py')))

# test
bookmark_imports = imports_from_file(file_path('zeeguu/core/model/bookmark.py'))
unique_code_imports =  imports_from_file(file_path('zeeguu/core/model/unique_code.py'))
assert(unique_code_imports != bookmark_imports)

def abstracted_to_top_level(G, depth=1):
    aG = nx.DiGraph()
    for each in G.edges():
        src = top_level_package(each[0], depth)
        dst = top_level_package(each[1], depth)

        if src != dst:
          aG.add_edge(src, dst)

    return aG

def clean_module_name(module_name):
    return module_name.removeprefix("zeeguu.")

def dependencies_digraph(code_root_folder):
    files = Path(code_root_folder).rglob("*.py")

    G = nx.DiGraph()

    for file in files:
        file_path = str(file)

        source_module = module_name_from_file_path(file_path)

        if source_module not in G.nodes:
            G.add_node(source_module)

        for target_module in imports_from_file(file_path):

            G.add_edge(source_module, target_module)

    return G

def clean_graph_for_display(G):
    display_G = nx.relabel_nodes(
        G,
        lambda node: clean_module_name(node),
        copy=True
    )
    return display_G

# extracts the parent of depth X
def top_level_package(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[:depth])

assert (top_level_package("zeeguu.core.model.util", 1) == "zeeguu")
assert (top_level_package("zeeguu.core.model.util", 2) == "zeeguu.core")

def abstracted_to_top_level(G, depth=1):
    aG = nx.DiGraph()

    for src_full, dst_full in G.edges():
        src = top_level_package(src_full, depth)
        dst = top_level_package(dst_full, depth)

        if src == dst:
            continue

        if aG.has_edge(src, dst):
            aG[src][dst]["weight"] += 1
        else:
            aG.add_edge(src, dst, weight=1)

    return aG

def draw_graph(G, size, **args):
    plt.figure(figsize=size)

    pos = nx.kamada_kawai_layout(G)

    nx.draw(
        G,
        pos,
        with_labels=False,
        **args
    )

    # move labels slightly downward
    label_pos = {
        node: (x, y - 0.05)
        for node, (x, y) in pos.items()
    }

    nx.draw_networkx_labels(
        G,
        label_pos,
        font_size=8
    )

    plt.show()

def dependencies_digraph(code_root_folder):
    files = Path(code_root_folder).rglob("*.py")

    G = nx.DiGraph()

    for file in files:
        file_path = str(file)

        source_module = module_name_from_file_path(file_path)
        if not is_relevant_module(source_module):
          continue

        if source_module not in G.nodes:
            G.add_node(source_module)

        for target_module in imports_from_file(file_path):

            if is_relevant_module(target_module):
              G.add_edge(source_module, target_module)


    return G

DG = dependencies_digraph(CODE_ROOT_FOLDER)

ADG = abstracted_to_top_level(DG, 3)

edge_widths = [
    ADG[u][v]["weight"]
    for u, v in ADG.edges()
]

draw_graph(
    ADG,
    (8, 8),
    width=edge_widths
)

