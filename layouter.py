import copy
import numpy as np
from numpy import arctan2, pi
from mol2_chain_q import atoms_and_bonds,  bonds_of_paired, xyz_names_bonds, Notation
from quadro_with_rotate import scube, find_section, anti_scube, spherical_cube
from mol2_worker import xyz_names_bonds


def cartesian_to_spherical(vector):
    r_xy = vector[0] ** 2 + vector[1] ** 2
    theta = arctan2(vector[1], vector[0])
    phi = arctan2(vector[2], r_xy ** 0.5)
    return theta, phi


def write_mol2_file(file_name, atoms, positions, bonds):
    '''
    :param file_name:
    :param names: chemical elements names
    :param positions: xyz - coordinates
    :param bonds: one way bonds
    :return: None, void write function
    '''
    with open(file_name, 'w') as f1:
        f1.write('@<TRIPOS>MOLECULE\n')
        f1.write('some info\n')
        f1.write(str(len(atoms))+'\t'+str(len(bonds))+'\n\n')
        f1.write('@<TRIPOS>ATOM\n')
        for num, key in atoms.items():
            f1.write("\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n".format(num, key.name, str(positions[num][0]),
                                                                            str(positions[num][1]), str(positions[num][2]),
                                                                            key.name_i, key.i1, key.i2, key.i3))
        f1.write('@<TRIPOS>BOND\n')

        for k, num in enumerate(bonds.items()):
            num, i = num
            # print(i, 't',attrs.get(tuple([i[0], i[1]])), attrs.get(tuple([i[1], i[0]])))
            f1.write("\t{0}\t{1}\t{2}\t{3}\n".format(str(k+1), str(num[0]), str(num[1]), str(i[1])))


def check(notation, dim_structure_reduced, eps=0.01):
    forces = 1
    forces_next = 0
    notation_l = notation.notation

    while abs(forces_next - forces) > eps**3:
        forces_next, forces = 0, forces_next
        lengths = bonds_of_paired(notation.bonds)
        for atom in dim_structure_reduced:
            force = np.array([0, 0, 0])
            for bond in notation_l[atom][0]:
                if bond[0] in dim_structure_reduced:
                    length = lengths.get(tuple(sorted([atom, bond[0]])))[0]
                    force = force + dim_structure_reduced[bond[0]]-notation.divider.scube[bond[1]]*length-dim_structure_reduced[atom]
            n_f = np.linalg.norm(force)
            forces_next += n_f
            # if n_f > 0.1:
            dim_structure_reduced[atom] = dim_structure_reduced[atom] + eps*force
        # print(atom, forces_next)
    return dim_structure_reduced

def dimensional_structure(notation, relax=True):
    '''
    :param notation: Notation with first atom with unique basis for every bond
    with length
    :return: xyz-info
    '''
    div = notation.divider.scube
    lengths = bonds_of_paired(notation.bonds)
    bonds_l = copy.deepcopy(notation.notation) # warning - it was error in other dim_structure builders
    first_atom = min(bonds_l.keys())
    dim_structure = {first_atom: np.array([0, 0, 0])}
    p = bonds_l[first_atom]
    bonds_copy = copy.deepcopy(bonds_l)
    p.insert(0, first_atom)  # p[0] - current atom, p[1] - bonds, p[2] - basis of p[0] atom
    p = [p]
    while len(p) != 0:
        cur_key, bonds = p.pop(0)
        for i in bonds:  # build bonds f    or cur_key atom
            if not (i[0] in dim_structure):  # if we don't have position:
                coord = div[i[1]]*(lengths.get(tuple([cur_key, i[0]]), lengths.get(tuple([i[0], cur_key])))[0]) + dim_structure[cur_key]
                dim_structure.update({i[0]: coord})
                if relax: dim_structure = check(notation, dim_structure)

                poper = bonds_copy.pop(i[0])
                poper.insert(0, i[0])
                ix = -1
                while ix < len(poper[1])-1:
                    ix += 1
                    if poper[1][ix][0] == cur_key:
                        poper[1].pop(ix)
                        break
                p.append(poper)
            else:
                print('cycle:', cur_key, i[0])
    return dim_structure

def relaxing(notation, lengths, dim_structure):
    # print(notation)
    # print(dim_structure)
    # forces = {}
    scube = notation.divider.scube
    # print(ln.notation)
    for i, j in ln.notation.items():
        for k in j[0]:#i, k[0] elements considered
            delta_length = np.linalg.norm(dim_structure[k[0]]-(dim_structure[i]+scube[k[1]]*(lengths.get(tuple([i, k[0]]), lengths.get(tuple([k[0], i])))[0])))
            if (delta_length) > 0.09:# and i < k[0]:
                print(i, k[0], delta_length, lengths.get(tuple([i, k[0]]), lengths.get(tuple([k[0], i])))[1])

    return 0



if __name__ == '__main__':
    # name_sh = 'Caffein'
    # name_sh = 'Naphthalene'
    # name_sh = 'Phenol'
    name_sh = '4c-Mn-OMe'
    names = ['Caffein', 'Naphthalene', 'Phenol', '4c-Mn-OMe', '3-MnH2', '2-Mn-OtBu']
    for name_sh in names:
        file_name = './tmp/'+name_sh+'_opt'
        name = name_sh+'_opt'
        n_param = 5
        # print(anti_scube(n=n_param))

        # bs, ass = xyz_names_bonds(name + '.mol2')

        atoms_info = atoms_and_bonds(file_name + '.mol2')
        ln = Notation(n=n_param, info_from_file=xyz_names_bonds(file_name + '.mol2'))
        # print(ln.notation)
        paired = bonds_of_paired(ln.bonds)
        dim_structure = dimensional_structure(ln, relax=True)
        relaxing(ln, paired, dim_structure)
        # print(dim_structure)
        write_mol2_file('My_' + name + '_' + 'q.mol2', atoms_info, dim_structure, bonds=paired)