import os
import config as cf
import csv


def write_csv(file: str, data):
    with open(os.path.join(file), 'w') as f:
        writer = csv.writer(f)
        for i in data:
            writer.writerow(i)
    f.close()


def read_csv(file: str, flag: bool, category_dic: dict):

    with open(file, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for line in reader:
            if i == 0:
                i += 1
                continue
            else:
                category = line[0]
                vtype = line[1]
                if category not in category_dic.keys():
                    category_dic[category] = {}
                    category_dic[category][vtype] = [0, 0]
                    if flag:
                        category_dic[category][vtype][1] += 1
                    else:
                        category_dic[category][vtype][0] += 1
                else:
                    if vtype not in category_dic[category]:
                        category_dic[category][vtype] = [0, 0]
                        if flag:
                            category_dic[category][vtype][1] += 1
                        else:
                            category_dic[category][vtype][0] += 1
                    else:
                        if flag:
                            category_dic[category][vtype][1] += 1
                        else:
                            category_dic[category][vtype][0] += 1
    f.close()


def read_csv_from_mark(file: str):
    category_dic = {}

    with open(file, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for line in reader:
            if i == 0:
                i += 1
                continue
            else:
                category = line[0]
                vtype = line[1]
                mark_all_tag = line[18]
                if category not in category_dic.keys():
                    category_dic[category] = {}
                    category_dic[category][vtype] = [mark_all_tag]
                else:
                    if vtype not in category_dic[category]:
                        category_dic[category][vtype] = [mark_all_tag]
                    else:
                        category_dic[category][vtype].append(mark_all_tag)
    f.close()

    return category_dic


def get_info_from_mark(project):
    project_dir = os.path.join(cf.data_dir, project)

    mark_file = 'marked datas.csv'

    mark_path = os.path.join(project_dir, mark_file)
    mark_res = read_csv_from_mark(mark_path)

    category_list = mark_res.keys()
    vtype_res = []
    category_res = []
    for i in category_list:
        vtypes = mark_res[i].keys()
        c_tp = 0
        c_fp = 0
        for j in vtypes:
            label_list = mark_res[i][j]
            v_tp = 0
            v_fp = 0
            for k in label_list:
                if k == 'TP':
                    v_tp += 1
                elif k == 'FP':
                    v_fp += 1
                else:
                    continue
            vtype_density = -1
            if v_tp + v_fp != 0:
                vtype_density = v_fp / (v_tp + v_fp)
            vtype_res.append([i, j, v_tp, v_fp, vtype_density])
            c_tp += v_tp
            c_fp += v_fp
        category_density = -1
        if c_tp + c_fp != 0:
            category_density = c_fp / (c_tp + c_fp)
        category_res.append([i, c_tp, c_fp, category_density])
    vtype_list = sorted(vtype_res, key=lambda x: (x[4], x[3]), reverse=True)
    category_list = sorted(category_res, key=lambda x: (x[3], x[2]), reverse=True)

    vtype_list.insert(0, ['category', 'vtype', 'tp', 'fp', 'fp_density'])
    category_list.insert(0, ['category', 'tp', 'fp', 'fp_density'])

    write_csv(os.path.join(project, project + '_mark_all_category_density.csv'), category_list)
    write_csv(os.path.join(project, project + '_mark_all_vtype_density.csv'), vtype_list)


def get_info(project):
    project_dir = os.path.join(cf.data_dir, project)

    unfixed_file_name = 'unfixed-' + project + '.csv'
    fixed_file_name = 'fixed-' + project + '.csv'

    unfixed_path = os.path.join(project_dir, unfixed_file_name)
    fixed_path = os.path.join(project_dir, fixed_file_name)

    # 按警告类别和类型出现数量排序
    category_dic = {}
    read_csv(unfixed_path, True, category_dic)
    read_csv(fixed_path, False, category_dic)


    # 计算误报密度
    category_list = category_dic.keys()
    vtype_res = []
    category_res = []
    for i in category_list:
        vtypes = category_dic[i].keys()
        c_tp = 0
        c_fp = 0
        for j in vtypes:
            label_list = category_dic[i][j]
            v_tp = label_list[0]
            v_fp = label_list[1]
            vtype_density = v_fp / (v_tp + v_fp)
            vtype_res.append([i, j, v_tp, v_fp, vtype_density])
            c_tp += v_tp
            c_fp += v_fp
        category_density = c_fp / (c_tp + c_fp)
        category_res.append([i, c_tp, c_fp, category_density])
    vtype_list = sorted(vtype_res, key=lambda x: (x[4], x[3]), reverse=True)
    category_list = sorted(category_res, key=lambda x: (x[3], x[2]), reverse=True)

    vtype_list.insert(0, ['category', 'vtype', 'tp', 'fp', 'fp_density'])
    category_list.insert(0, ['category', 'tp', 'fp', 'fp_density'])

    write_csv(os.path.join(project, project + '_category_density.csv'), category_list)
    write_csv(os.path.join(project, project + '_vtype_density.csv'), vtype_list)


def get_type_info(project: str):
    project_dir = os.path.join(cf.data_dir, project)
    if os.path.isdir(project_dir) and not project.startswith('.'):
        if not os.path.exists(project):
            os.mkdir(project)
        get_info(project)
        get_info_from_mark(project)


if __name__ == '__main__':

    # 遍历文件夹
    projects = os.listdir(cf.data_dir)
    res = list(map(get_type_info, projects))