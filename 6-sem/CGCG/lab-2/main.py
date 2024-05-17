from matplotlib import pyplot as plt

from consts import MIN_X, MAX_X, MIN_Y, MAX_Y
from node import gen_points, plot_points, make_lr_node, search_region

points = gen_points(20)
plot_points(points)
tree = make_lr_node(points, left_bound=MIN_X, right_bound=MAX_X, lower_bound=MIN_Y, upper_bound=MAX_Y)
print(tree.display("\t"))
right_x = 4
left_x = 1
up_y = 4
down_y = 1
search_region(tree=tree, right=right_x, left=left_x, up=up_y, down=down_y)
plt.show()