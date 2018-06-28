import sys, getopt
import csv
import json

def main(argv):

    input_file = '/Applications/CELLTK/df.csv'
    output_file = '/Applications/CELLTK/output.json'
    read_csv(input_file, output_file)

csv_rows = []
def read_csv(file, json_file):
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
                #celldiv.extend([{title[i]: row[title[i]] for i in range(len(title))}])
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

        # Find all parents and put together into one list
        csv_copy = csv_rows[0].copy()
        del csv_copy['object']
        del csv_copy['ch']
        del csv_copy['frame']
        del csv_copy['prop']
        for key in csv_copy.keys():
            temp = all_parents(csv_copy, key, [])
            if temp != []:
                temp.remove(key)
                if temp != []:
                    curr_csvrow = csv_rows[0][key].split('Child: ')
                    curr_csvrow.remove(curr_csvrow[0])
                    if curr_csvrow != []:
                        curr_csvrow.insert(0, 'Parent: ' + ', '.join(temp) + '; Child: ')
                    else:
                        curr_csvrow.insert(0, 'Parent: ' + ', '.join(temp) + ';')
                    csv_rows[0][key] = ''.join(curr_csvrow)

        for (parent, frame) in celldiv:
            if 'Frame: ' + frame not in csv_rows[0][parent]:
                csv_rows[0][parent] += '; Frame: ' + frame

        write_json(csv_rows, json_file, initcells, finalcells, totalcells)
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

# Recursively find all parents across generations
def all_parents(csv_child, childkey, oldlst=[]):
    alllst = oldlst
    alllst.append(childkey)
    if 'Child' not in csv_child[childkey] and 'Parent' not in csv_child[childkey]:
        return []
    elif 'Parent' not in csv_child[childkey]:
        return alllst
    else:
        strlst = csv_child[childkey].split('Child: ')
        strlst = strlst[0]
        strlst = strlst.split('Parent: ')
        strlst.remove(strlst[0])
        strlst = ''.join(strlst[0])
        strlst = strlst.replace(';', '')
        strlst = strlst.split(', ')
        for term in strlst:
            all_parents(csv_child, str(int(float(term))), alllst)

    return alllst


def write_json(data, json_file, initcells, finalcells, totalcells):
    with open(json_file, "w") as f:
        f.write('Parents and children are listed in order of immediacy.\n')
        f.write('Frame describes what frame the parent divided. Note: two frames indicate \n' +
                        'a possible labeling error from CellTK.\n')
        f.write('To convert nested list string back to a list, import ast and call \n' +
                        'ast.literal_eval() to turn string back to list\n\n')
        f.write('No. of cells at start: ' + str(initcells) + '\n')
        f.write('No. of cells at end: ' + str(finalcells) + '\n')
        f.write('Total no. of cells labeled: ' + str(totalcells) + '\n')
        f.write(json.dumps(data, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
   main(sys.argv[1:])
