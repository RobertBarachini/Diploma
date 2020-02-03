import os
import glob
import shutil


def get_filepaths(rootpath):
    filenames = []
    for directory in os.walk(rootpath):
        folder_match = os.path.join(directory[0], "*.pdf")
        files = glob.glob(folder_match)
        for file in files:
            filenames.append(file)
    return filenames

# def save_game(game, filename):
#     str_builder = []
#     for dtz_val in game[0]:
#         str_builder.append(str(dtz_val))
#         str_builder.append(" ")
#     str_builder.append("\n")
#     str_builder.append(game[1])
#     contents = ''.join(str_builder)
#     write_to_file(contents, filename)

def get_plot_stringOLD(plot_name):
    plot_name_2 = plot_name.replace("_", " ")
    res = """\\begin{figure}[htb]
    \\centering
    \\includegraphics[width=16cm]{img/plots/FILENAME.pdf}
    \\caption{PLOTNAME}
\\label{PLOTNAME}
\\end{figure}

"""
    res = res.replace("PLOTNAME", plot_name_2)
    res = res.replace("FILENAME", plot_name)
    return res

def get_plot_string(plot_name):
    # plot_name_2 = plot_name.replace("_", " ")
    res = """\\begin{subfigure}{0.52\\textwidth}
\\includegraphics[width=\linewidth]{img/plots/FILENAME.pdf}
\\caption{PLOTNAME} \label{fig:a}
\\end{subfigure}\hspace*{\\fill}
"""
    plot_name_2 = plot_name.replace("", "")
    plot_name_2 = plot_name_2.replace("plot_", "")
    plot_name_2 = plot_name_2.replace("_", "\\_")
    res = res.replace("PLOTNAME", plot_name_2)
    res = res.replace("FILENAME", plot_name)
    return res

def write_to_file(contents, filename):
    with open(filename, "w") as text_file:
        text_file.write(contents)

def generate_plots_codeOLD(rootpath):
    str_builder = []
    filepaths = get_filepaths(rootpath)
    counter = 0
    for filepath in filepaths:
        filename = os.path.basename(filepath).split(".")[0]
        plot_string = get_plot_string(filename)
        str_builder.append(plot_string)
    contents = ''.join(str_builder)
    write_to_file(contents, os.path.join(rootpath, "LaTeX_plots_code.txt"))
    return contents

def generate_plots_code(rootpath):
    str_builder = []
    filepaths = get_filepaths(rootpath)
    counter = 0
    rows = 2
    cols = 6
    for filepath in filepaths:
        if counter % cols == 0:
            str_add = """\n\\caption{Zbirka grafov za kompozicijo figur X, Y potez do konca} \label{fig:NUMNUMNUM}
\\end{figure}\n\n\n"""
            str_add = str_add.replace("NUMNUMNUM", str(int(counter / cols)))
            str_builder.append(str_add)
        if counter % cols == 0:
            str_builder.append("\\begin{figure}[t!]\n")
        filename = os.path.basename(filepath).split(".")[0]
        plot_string = get_plot_string(filename)
        if counter % rows == 0 and counter % cols != 0:
            str_builder.append("\n\\medskip\n")
        str_builder.append(plot_string)
        counter += 1
    str_add = """\n\\caption{Zbirka grafov za kompozicijo figur X, Y potez do konca} \label{fig:NUMNUMNUM}
\\end{figure}\n\n\n"""
    str_add = str_add.replace("NUMNUMNUM", str(int(counter / cols)))
    str_builder.append(str_add)
    contents = ''.join(str_builder)
    write_to_file(contents, os.path.join(rootpath, "LaTeX_plots_code.txt"))
    return contents

def gather_plots(rootpath):
    plots_dir = os.path.join(rootpath, "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    filepaths = get_filepaths(rootpath)
    for filepath in filepaths:
        shutil.copy(filepath, plots_dir)

if __name__ == "__main__":
    rootpath = "PGN\\MCTS_X_1"
    generate_plots_code(rootpath)
    gather_plots(rootpath)