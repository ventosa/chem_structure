from penta_with_rotate import get_penta_points, find_section,\
    find_section_and_rotate, show_points,\
    rotate_by_basis, show_named_points, \
    get_reversed_section_and_basis
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import copy
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
count_bonds = {'H': 1, 'C': 4, 'O': 2}
eps_length = 0.001
pp = get_penta_points()


def chain1():
    return {1: [[[2, 4], [3, 5], [4, 10], [5, 7]], [0, 0]],
            2: [[[1, 3]], [0, 0]],
            3: [[[1, 3]], [1, 1]],
            4: [[[1, 6]], [0, 1]],
            5: [[[1, 11]], [2, 3]]}, {1: 'C', 2: 'H', 3: 'H', 4: 'H', 5: 'H'}


def chain2():
    return {1: [[[2, 4],[3, 5], [4, 10], [5, 7]], [0, 0]],
            2: [[[1, 4]], [0, 0]],
            3: [[[1, 5]], [0, 0]],
            4: [[[1, 10]], [0, 0]],
            5: [[[1, 7], [6, 2], [7, 6], [8, 8]], [0, 0]],
            6: [[[5, 2]], [0, 2]],
            7: [[[5, 6]], [0, 0]],
            8: [[[5, 8]], [0, 2]]}, {1: 'C', 2: 'H', 3: 'H', 4: 'H', 5: 'C', 6: 'H', 7: 'H', 8: 'H'}


###########################Release one way builder########################
def dimensional_corrected_structure(chain_v):
    '''
    :param chain_v: dictionary of atoms with bonds and atoms' basis properties
    :return: list of atoms with their center coordinates
    '''
    oriented = [1,]
    dim_structure = {1: [np.array([0, 0, 0]), np.array([0, 0])]}
    chain_copy = copy.deepcopy(chain_v)
    p = chain_copy.pop(1)
    p.insert(0, 1) #p[0] - current atom, p[1] - bonds, p[2] - basis of p[0] atom
    p = [p]
    while len(p) != 0:
        cur_key, bonds, basis = p.pop(0)
        for i in bonds: # build bonds for cur_key atom
            if i[0] in oriented: # if it's reverse information for correct
                # section, b0, b1 = find_section_and_rotate(dim_structure[i[0]][0], dim_structure[cur_key][0])
                # print(cur_key, i[0], section, b0, b1)
                section, b0, b1 = get_reversed_section_and_basis(i[1], basis)
                # find the section for cur_key and its basis
                index = 0 # find index of cur_key-i[0] bond: later do it by build-in function
                for num, j in enumerate(chain_v[cur_key][0]):
                    if j[0] == i[0]:
                        index = num
                        break
                chain_v[cur_key][0][index][1] = section #set section to i[0] bond
                chain_v[cur_key][1] = np.array([b0, b1]) # set basis for cur_key orientation
            else: #if it's new bond
                oriented.append(i[0])
                coord = rotate_by_basis(pp[i[1]], dim_structure[cur_key][1][0], dim_structure[cur_key][1][1])+dim_structure[cur_key][0]
                section, angle0, angle1 = find_section_and_rotate(dim_structure[cur_key][0], coord)
                dim_structure.update({i[0]: [coord, [angle0, angle1]]})
                index = 0
                for num, j in enumerate(chain_v[i[0]][0]):
                    if j[0] == cur_key:
                        index = num
                        break
                chain_v[i[0]][index][0][1] = section
                poper = chain_copy.pop(i[0])
                poper.insert(0, i[0])
                p.append(poper)
    return dim_structure, chain_v
##############################################################################################


def write_xyz_file(file_name, names, positions):
    '''
    :param file_name:
    :param names: chemical elements names
    :param positions: xyz - coordinates
    :return: None, void write function
    '''
    with open(file_name, 'w') as f1:
        for key, item in names.items():
            f1.write("{0}\t{1}\t{2}\t{3}\n".format(item, str(positions[key][0][0]),str(positions[key][0][1]),str(positions[key][0][2])))

############################ Show ######################################
def show_with_bonds(bounds, dpoints, dictionary=None):
    '''
    :param bounds: list of bounds
    :param dpoints: dictionary with coordinates
    :param dictionary: names
    :return: 3d picture
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in bounds:
        ax.plot([dpoints[i[0]][0], dpoints[i[1]][0]],
                [dpoints[i[0]][1], dpoints[i[1]][1]],
                [dpoints[i[0]][2], dpoints[i[1]][2]])
    if dictionary:
        for key, item in dpoints.items():
            ax.text(item[0]+0.05, item[1]+0.05, item[2]+0.05, dictionary[key])
    plt.show()


def bonds_shower(positions, bonds):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for key, item in bonds.items():
        for i in item[0]:
            ax.plot([positions[key][0][0], positions[i[0]][0][0]],
                    [positions[key][0][1], positions[i[0]][0][1]],
                    [positions[key][0][2], positions[i[0]][0][2]])
    plt.show()


def read_xyz_file(file):
    with open(file, 'r') as file:
        n = int(file.readline())
        names = {}
        positions = {}
        for i in range(n):
            line = file.readline().split()
            names.update({i: line[0]})
            x, y, z = [float(j) for j in line[1::]]
            positions.update({i: [x,y,z]})
    return positions, names


def show_dim_chain(dim_struct, names=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    if names:
        for key, item in dim_struct.items():
            ax.scatter(item[0][0], item[0][1], item[0][2])
            ax.text(item[0][0]+0.05, item[0][1]+0.05, item[0][2]+0.05, dict[key])
    # for i in bonds:
    #     ax.plot([dpoints[i[0]][0], dpoints[i[1]][0]],
    #             [dpoints[i[0]][1], dpoints[i[1]][1]],
    #             [dpoints[i[0]][2], dpoints[i[1]][2]])
    # if annotate:
    #     for key, item in dpoints.items():
    #         ax.text(item[0] + 0.05, item[1] + 0.05, item[2] + 0.05, dictionary[key])
    plt.show()


def to_list_bonds(structure):
    '''
    :param structure: dictionary of list bonds
    :return: list of bonds
    '''
    pass


if __name__ == '__main__':
    struct = chain2()[0]
    # coo = (dimentional_corrected_strcute(struct))[0]
    positions, bonds = dimensional_corrected_structure(struct)
    # show_points([item[0] for key, item in positions.items()])
    # show_named_points(positions)

    print(bonds)
    # bonds_shower(positions, bonds)
    # show_with_bonds(chain2()[0], positions)
    # write_xyz_file('input.txt', chain2()[1], dimensional_corrected_structure(struct)[0])
    # write_xyz_file('input.txt', chain2()[1], coo)
