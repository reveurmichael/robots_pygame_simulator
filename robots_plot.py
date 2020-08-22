__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
from matplotlib import pylab
import robots_utils as utils
from robots_direction import D
import random as rd

def get_cmap(NUM_ROBOTS):
    list_color = [(1, 1, 1),(0, 0, 1),(0, 1, 0), (1, 0, 0), (0.2, 0.8, 0.9),
                  (0.7, 0.3, 0.8), (0.5, 0.2, 0),(0, 0, 0)]
    j = NUM_ROBOTS - 7
    while j >= -1:
        r, g, b = rd.random(), rd.random(), rd.random()
        if 0.1 < r + g + b < 1.3:
            list_color.append((r, g, b))
            j -= 1
    cmap = mcolors.ListedColormap(list_color)
    return cmap

def plot_matrix(pos, cmap):
    NUM_ROBOTS = len(pos)
    mat, pos_relative = utils.pos_to_mat_0230(pos)
    plt.matshow(mat.T, cmap=cmap, origin="lower")
    for i in range(NUM_ROBOTS):
        plt.text(pos_relative[i][0], pos_relative[i][1], "" + str(i), va="center", ha="center", color="white")
    plt.gca().set_xticks([x - 0.5 for x in plt.gca().get_xticks()][1:], minor='true')
    plt.gca().set_yticks([y - 0.5 for y in plt.gca().get_yticks()][1:], minor='true')
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.grid(which='minor')
    plt.show()

def draw_and_save_relative(pos, result_dir, file_number, cmap, file_extension=".pdf"):
    NUM_ROBOTS = len(pos)
    mat, pos_relative = utils.pos_to_mat_0230(pos)  # TO CHANGE PLOT, CHANGE HERE
    plt.figure(num=None, figsize=(NUM_ROBOTS * 2, NUM_ROBOTS * 2), dpi=80)
    fig = plt.figure(1)
    cut = 1.00
    xmax = cut * NUM_ROBOTS # or: len(mat)
    ymax = cut * NUM_ROBOTS
    plt.xlim(-1, xmax + 1)
    plt.ylim(-1, ymax + 1)
    plt.matshow(mat.T, cmap=cmap, origin="lower")
    for i in range(NUM_ROBOTS):
        plt.text(pos_relative[i][0], pos_relative[i][1], "" + str(i), va="center", ha="center", color="white")
    plt.gca().set_xticks([x - 0.5 for x in plt.gca().get_xticks()][1:], minor='true')
    plt.gca().set_yticks([y - 0.5 for y in plt.gca().get_yticks()][1:], minor='true')
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.grid(which='minor')
    file_name = os.path.join(result_dir, str(file_number).zfill(4) + file_extension)
    plt.savefig(file_name, bbox_inches="tight")
    pylab.close()
    del fig

def draw_and_save_hist_relative(pos_original, hist, result_dir, cmap, file_extension=".png"):
    pos = pos_original[:]
    file_number = 0
    draw_and_save_relative(pos, result_dir, file_number, cmap, file_extension=file_extension)
    for h in hist:
        file_number += 1
        for i in range(len(h) / 2):
            w = h[2 * i]
            direction = h[2 * i + 1]
            (x, y) = pos[w]
            if direction == D.LEFT:
                x -= 1
            elif direction == D.RIGHT:
                x += 1
            elif direction == D.UP:
                y += 1
            elif direction == D.DOWN:
                y -= 1
            pos = pos[:w] + [(x, y)] + pos[w + 1:]
        draw_and_save_relative(pos, result_dir, file_number, cmap, file_extension=file_extension)

def draw_and_save_mat_fixed(mat, pos, result_dir, file_number, cmap, file_extension=".png"):
    NUM_ROBOTS = len(pos)
    size = len(mat)
    plt.figure(num=None, figsize=(size * 2, size * 2), dpi=80)
    fig = plt.figure(1)
    cut = 1.00
    xmax = cut * size
    ymax = cut * size
    plt.xlim(-1, xmax + 1)
    plt.ylim(-1, ymax + 1)
    plt.matshow(mat.T, cmap=cmap, origin="lower")
    for i in range(NUM_ROBOTS):
        plt.text(pos[i][0], pos[i][1], "" + str(i), va="center", ha="center", color="white")
    plt.gca().set_xticks([x - 0.5 for x in plt.gca().get_xticks()][1:], minor='true')
    plt.gca().set_yticks([y - 0.5 for y in plt.gca().get_yticks()][1:], minor='true')
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.grid(which='minor')
    file_name = os.path.join(result_dir, str(file_number).zfill(4) + file_extension)
    plt.savefig(file_name, bbox_inches="tight")
    plt.close(fig)
    plt.close("all")
    pylab.close()
    del fig

def draw_and_save_hist_fixed(pos_original, hist, result_dir, cmap, file_extension=".png"):
    arr_pos = [pos_original]
    pos = pos_original[:]
    for h in hist:
        for i in range(len(h) / 2):
            w = h[2 * i]
            direction = h[2 * i + 1]
            (x, y) = pos[w]
            if direction == D.LEFT:
                x -= 1
            elif direction == D.RIGHT:
                x += 1
            elif direction == D.UP:
                y += 1
            elif direction == D.DOWN:
                y -= 1
            pos = pos[:w] + [(x, y)] + pos[w + 1:]
        arr_pos.append(pos)
    NUM_ROBOTS = len(pos_original)
    file_number = 0
    min_x = 10000000
    max_x = -10000000
    min_y = 10000000
    max_y = -10000000
    for pos in arr_pos:
        for p in pos:
            min_x = min(p[0], min_x)
            max_x = max(p[0], max_x)
            min_y = min(p[1], min_y)
            max_y = max(p[1], max_y)
    NUM_GRID = max(max_x - min_x, max_y - min_y) + 3
    for pos in arr_pos:
        mat = np.zeros((NUM_GRID, NUM_GRID))
        pos_fixed = []
        for i in range(NUM_ROBOTS):
            (x, y) = pos[i]
            mat[(x - min_x + 1, y - min_y + 1)] = (i + 1)
            pos_fixed.append((x - min_x + 1, y - min_y + 1))
            draw_and_save_mat_fixed(mat, pos_fixed, result_dir, file_number, cmap, file_extension=file_extension)
        file_number += 1