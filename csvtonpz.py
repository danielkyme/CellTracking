import sys, getopt
import csv
import numpy as np

def main(argv):

    input_file = '/Applications/CELLTK/dftest2.csv'
    output_file = '/Applications/CELLTK/output.npz'
    read_csv(input_file, output_file)

csv_rows = []
def read_csv(file, npz_file):
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        numcellsstart = []
        numcellsend = []
        celldiv = []
        numframe = 0

        for row in reader:
            numframe = row['frame']
            if row['prop'] == 'parent':
                csv_rows.extend([{title[i]: row[title[i]] for i in range(len(title))}])
            elif row['prop'] == 'cell_id' and row['frame'] == '0':
                numcellsstart.extend(([{title[i]: row[title[i]] for i in range(len(title))}]))
            elif row['prop'] == 'cell_id' and row['frame'] == numframe:
                numcellsend = []
                numcellsend.extend(([{title[i]: row[title[i]] for i in range(len(title))}]))

        initcells = 0
        for key in numcellsstart[0].keys():
            if numcellsstart[0][key] != '':
                initcells += 1
        initcells -= 3

        finalcells = 0
        for key in numcellsend[0].keys():
            if numcellsend[0][key] != '':
                finalcells += 1
        finalcells -= 3

        framecopy = csv_rows[0].copy()
        for key in framecopy.keys():
            if key == 'object' or key == 'ch' or key == 'frame' or key == 'prop':
                continue
            elif framecopy[key] != '':
                celldiv.append((framecopy[key], '0'))

        # Find immediate Parents
        ind = 1
        while len(csv_rows) >= 2:
            final_dict = csv_rows[0]
            curr_dict = csv_rows[ind]
            for key in curr_dict.keys():
                if curr_dict[key] == "":
                    continue
                else:
                    if final_dict[key] == '':
                        final_dict[key] = curr_dict[key]
                    else:
                        final_dict[key] = final_dict[key] + ', ' + curr_dict[key]
                    if key == 'object' or key == 'ch' or key == 'frame' or key == 'prop':
                        continue
                    else:
                        celldiv.append((str(int(float(curr_dict[key]))), curr_dict['frame']))
            csv_rows.remove(curr_dict)
        csv_copy = csv_rows[0].copy()
        for keys in csv_rows[0].keys():
            if keys == 'object' or keys == 'ch' or keys == 'prop' or keys == 'frame':
                continue
            dic = csv_rows[0]
            if dic[keys] != '':
                dic[keys] = 'Parent: ' + dic[keys] + '; '


        # Find immediate Children and put together into one list
        child = find_child(csv_copy)
        csvchild = child.copy()
        totalcells = 0
        for key in csv_copy.keys():
            if 'Child' in child[key]:
                csv_rows[0][key] += child[key]
            totalcells = key

        # Find all children and put together into one list
        for key in csv_copy.keys():
            temp = str(all_children(csvchild, key, []))
            if temp != '':
                curr_csvrow = csv_rows[0][key].split('Child: ')
                curr_csvrow.remove(curr_csvrow[1])
                curr_csvrow.append('Child: ' + temp)
                csv_rows[0][key] = ''.join(curr_csvrow)

        del csv_rows[0]['object']
        del csv_rows[0]['ch']
        del csv_rows[0]['frame']
        del csv_rows[0]['prop']

        npz_arr = [[]]
        for key in csv_rows[0].keys():
            if 'Child' in csv_rows[0][key]:
                curr_csvrow = csv_rows[0][key].split('Child: ')
                curr_csvrow.remove(curr_csvrow[0])
                npz_arr.append(curr_csvrow)
            else:
                npz_arr.append([])

        np.savez(npz_file, npz_arr)
        
        print('To get array of all children of a cell, access by using the following commands: ')
        print('data = np.load(FILE LOCATION)')
        print("data['arr_0'][num cell]")
        print("For example, cell 1: data['arr_0'][1] \n")
        print('No. of cells at start: ' + str(initcells))
        print('No. of cells at end: ' + str(finalcells))
        print('Total no. of cells labeled: ' + str(totalcells))

        print('Success!')


# Find immediate children
def find_child(csv_copy):
    del csv_copy['object']
    del csv_copy['ch']
    del csv_copy['frame']
    del csv_copy['prop']
    for key in csv_copy.keys():
        if csv_copy[key] == '' or 'Child' in csv_copy[key]:
            continue
        else:

            temp = str(int(float(csv_copy[key])))
            if str(float(key)) in csv_copy[temp]:
                continue
            elif 'Child' in csv_copy[temp]:
                csv_copy[temp] += ', ' + str(float(key))
            else:
                csv_copy[temp] = 'Child: ' + str(float(key))

    return csv_copy

# Recursively find all children across generations
def all_children(csv_child, parentkey, oldlst=[]):
    oldlst = []
    if 'Child' not in csv_child[parentkey] and 'Parent' not in csv_child[parentkey]:
        return ''
    elif 'Child' not in csv_child[parentkey]:
        return ''
    else:
        strlst = csv_child[parentkey].split('Child: ')
        strlst.remove(strlst[0])
        strlst = ''.join(strlst[0])
        strlst = strlst.split(', ')
        ind = 0
        for term in strlst:
            term_temp = []
            term_temp.append(term)
            oldlst.append(term_temp)
            alllst_temp = (all_children(csv_child, str(int(float(term)))))
            if alllst_temp != '':
                oldlst[ind].append(alllst_temp)
            ind += 1

    return oldlst


if __name__ == "__main__":
   main(sys.argv[1:])
