#
# Author: Jeff Matayoshi
#
# References:
#
# Eppstein, D., Falmagne, J.-C., & Uzun, H. (2009). On verifying and engineering 
#     the well-gradedness of a union-closed family. Journal of Mathematical 
#     Psychology, 53(1), 34 39.
# Falmagne, J.-C., & Doignon, J.-P. (2011). Learning spaces. In
#     Interdisciplinary applied mathematics. Heidelberg: Springer-Verlag.
# Koppen, M. (1998). On alternative representations for knowledge spaces.
#     Mathematical Social Sciences, 36(2), 127-143.
# Matayoshi, J. (2017).  On the properties of well-graded union-closed families.
#     Journal of Mathematical Psychology, 80, 15-21.

import copy
import argparse


def main():
    parser = argparse.ArgumentParser(description=
                                     'Well-graded union-closed family example.')
    parser.add_argument('filename', type=argparse.FileType('w'), nargs='?',
                        help='file to store family in')
    args = parser.parse_args()

    base = create_base_for_example()
    uc_fam = create_family_from_base(base)
    X = frozenset({1, 2, 3})
    if is_well_graded(uc_fam, base):
        print('The family is well-graded.\n')
    if is_X_closed(uc_fam, X):
        print('The family is X-closed.\n')
    print('Number of sets = ' + str(len(uc_fam)))
    print('Element counts = ' + str(count_elements(uc_fam, X)))
    if args.filename:
        write_family_to_file(uc_fam, args.filename)
                
def is_union_closed(sets):
    """
    Finite family of finite sets is union-closed iff it contains union of each 
    pair of sets
    """
    for A in sets:
        for B in sets.difference(set({A})):            
            if A.union(B) not in sets:
                return False
    return True

def is_intersection_closed(sets):
    """
    Finite family of finite sets is intersection-closed iff it contains 
    intersection of each pair of sets
    """
    for A in sets:
        for B in sets.difference(set({A})):            
            if A.intersection(B) not in sets:
                return False
    return True

def is_X_closed(sets, X):
    """
    Finite family of finite sets is X-closed iff every pair-wise intersection of 
    sets that contains X is in the family
    """
    for A in sets:
        for B in sets.difference(set({A})):
            inter = A.intersection(B)
            if X < inter and inter not in sets:
                return False
    return True
    
def project_family(sets, X):
    """
    For each set A in sets, add A\X to projected family
    """
    proj_family = set({})
    for A in sets:
        proj_family.update(set({frozenset(A.difference(X))}))
    return proj_family

def get_minimal_sets(sets):
    """
    Given a family of sets, find all the minimal sets
    """
    num_sets = len(sets)
    minimal_sets = {}
    for i in range(num_sets):
        is_minimal = True
        for j in range(num_sets):
            if i != j:
                if sets[j] < sets[i]:
                    is_minimal = False
                    break
        if is_minimal:
            minimal_sets[sets[i]] = sets[i].copy()
    return list(minimal_sets.values())

def get_surmise(sets):
    """
    Find surmise system for a family of sets (see Section 5.2 in Falmagne and 
    Doignon, 2011 for background)
    """    
    universe = set()
    for curr_set in sets:
        universe.update(curr_set)
    num_sets = len(sets)
    surmise = {}
    for q in universe:
        q_surmise = set({})
        for curr_set in sets:
            if q in curr_set:
                if len(q_surmise) > 0:
                    is_minimal = True
                    for sur_set in q_surmise.copy():
                        if curr_set < sur_set:
                            q_surmise.remove(sur_set)
                        elif  curr_set > sur_set:
                            is_minimal = False                        
                            break
                    if is_minimal:
                        q_surmise.update(set({curr_set}))
                else:
                    q_surmise.update(set({curr_set}))
        surmise[q] = q_surmise
    return surmise

def get_base(sets):
    """
    The base is composed of all the unique sets in the surmise system
    """
    surmise = get_surmise(sets)
    base = set({})
    for q in surmise:
        for curr_set in surmise[q]:
            base = base.union(set([curr_set]))
    return base

def has_unique_atoms(sets):
    """
    A union-closed family of sets containing the empty set is well-graded iff 
    each atom is an atom at only one element; this is equivalent to checking 
    that the surmise function has no repeated sets (see Theorem 4.5 in Koppen, 
    1998 or Theorem 5.4.1 in Falmagne and Doignon, 2011)
    """
    surmise = get_surmise(sets)
    surmise_sets = set({})
    surmise_count = 0
    for q in surmise.keys():
        for curr_set in surmise[q]:
            surmise_count += 1
            surmise_sets.update(set({curr_set}))
    if surmise_count == len(surmise_sets):
        return True
    else:
        return False

def is_well_graded(sets, base):
    """
    A union-closed family of sets F without the empty set is well-graded iff
    for each b in the base, the projected family F\b is well-graded; since 
    F\b contains the empty set, it can be checked for well-gradedness by 
    looking only at the atoms
    """
    print('Checking if each projection is well-graded...')
    for b in base:
        proj_sets = project_family(sets, b)
        curr_proj_str = 'F\\' + '{' + ','.join(str(n) for n in b) + '}'
        if not has_unique_atoms(proj_sets):
            print('ERROR: ' + curr_proj_str + ' is not well-graded')
            return False
        else:
            print(curr_proj_str + ' is well-graded')
    return True

def create_base_for_example():
    """
    Creates base for Example 2.1; this example shows that a three-set X
    in a well-graded family, where the family is also X-closed, does not
    necessarily contain an abundant element
    """        
    A_i = {}
    A_i[1] = set([frozenset({}),
                  frozenset({1}),
                  frozenset({2})])
    A_i[2] = set([frozenset({}),
                  frozenset({1}),
                  frozenset({3})])
    A_i[3] = set([frozenset({}),
                  frozenset({2}),
                  frozenset({3})])
    B_i = {}
    for i in range(1, 7):
        B_i[i] = frozenset(set({4, 5, 6}).union(set({i + 6})))
    base = set({frozenset({1, 2, 3, 4, 5, 6, 13})})
    curr_set = set({1, 2})
    for i in range(3, 7):
        curr_set = curr_set.union(set({i}))
        base.update(set({frozenset(curr_set)}))
    for i in range(1, 4):
        for curr_set in A_i[i]:
            base.update(set({frozenset(curr_set.union(B_i[i]))}))
            base.update(set({frozenset(curr_set.union(B_i[i + 3]))}))
    for i in range(1, 7):
        base.update(set({frozenset(B_i[i].union(set({13})))}))
    return base

def create_family_from_base(base):
    """
    Simple implementation that takes unions from the base until the family 
    no longer grows in size
    """
    uc_fam = copy.deepcopy(base)
    curr_size = len(uc_fam)
    prev_size = 0
    while curr_size > prev_size:
        prev_fam = copy.deepcopy(uc_fam)
        for a in prev_fam:
            for b in base:
                uc_fam.update(set({frozenset(a.union(b))}))
        prev_size = curr_size
        curr_size = len(uc_fam)
    return uc_fam

def count_elements(uc_fam, X):
    """
    Count the occurences of each element in X
    """
    count_dict = {}
    for b in X:
        count_dict[b] = 0
    for a in uc_fam:
        for b in X:
            if b in a:
                count_dict[b] += 1
    return count_dict

def write_family_to_file(uc_fam, filename):
    fam_list = list(uc_fam)
    fam_list.sort(key=len)
    with filename as f:
        for i in fam_list:
            i = list(i)
            i.sort()
            f.write(','.join(str(n) for n in i) + '\n')
            
if __name__ == "__main__":
    # execute only if run as a script
    main()                
