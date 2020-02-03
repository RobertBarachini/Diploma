import os
import graphviz
import json
import chess
import chess.svg

def load_json(filepath):
    json_string = ""
    with open(filepath, "r") as file:
        json_string = file.read()
    jobject = json.loads(json_string)
    return jobject

def generate_visualization(filepath):
    jobject = load_json(filepath)
    dot = generate_dot_from_json(jobject)
    dot.render('visualizations/visualization_test.gv', view=True)

def generate_dot_label(jobject):
    label = ""
    label += "id: " + str(jobject["id"]) + "\\n"
    label += "win ratio: " + str(jobject["wins"]) + "/" + str(jobject["playouts"]) + "\\n"
    label += "fen: " + jobject["fen"]
    # label = "*" # added for purposes of png generation
    return label

def generate_dot_from_json(jobject, parent = None, dot = None):
    if dot == None:
        # dot = graphviz.Digraph(comment="MCTS Visualization", format='png')
        dot = graphviz.Digraph(comment="MCTS Visualization")
        # dot.attr(size="400, 500")
        # dot.attr(ranksep="10.5", nodesep="0.25")
        dot.attr(ranksep="10.5", nodesep="0.25", size="400, 500")
    
    label = generate_dot_label(jobject)
    node_id = str(jobject["id"])
    b = chess.Board(jobject["fen"])
    
    # svg_string = chess.svg.board(b)
    # svg_filename = "temp\\" + node_id + ".svg"
    # with open(svg_filename, "w") as output_file:
    #     output_file.write(str(svg_string))

    # new_node = dot.node(node_id, label=label, shape="rectangle", color="red", fontcolor="red", fillcolor="red", style="filled")
    # new_node["fillcolor"] = "red"
    # svg_filename = "test_100_100.png"
    if jobject["turn"] == True:
        new_node = dot.node(node_id, label=label, shape="rectangle", fontcolor="white", fillcolor="black", style="filled")#, image=svg_filename)
    else:
        new_node = dot.node(node_id, label=label, shape="rectangle", fontcolor="black", fillcolor="white", style="filled")#, image=svg_filename)
    

    if jobject["parent"] == None: # Root
        None # dot.edge(jobject["id"], parent)
    else:
        dot.edge(parent, node_id, label=jobject["move"])

    for child in jobject["children"]:
        dot = generate_dot_from_json(child, parent=node_id, dot=dot)

    return dot

if __name__ == "__main__":
    filepath = "MCTS_X_single.json"
    generate_visualization(filepath)