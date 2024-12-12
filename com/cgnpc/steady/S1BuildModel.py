import os
import pickle
import threading

import numpy as np
from flask import Flask, jsonify, request


def read_csv(file_ID, file_path, file_info, result_dict):
    try:  
        file_measurement_points = np.loadtxt(file_path, dtype=str, max_rows=1, delimiter=',')
        index_map = {char.replace(" ", ""): idx for idx, char in enumerate(file_measurement_points)}
        AV_point_cols = [index_map[char] if char in index_map else -1 for char in file_info['AvPoints']]
        DV_point_cols = [index_map[char] if char in index_map else -1 for char in file_info['DvPoints']]

        data = np.loadtxt(file_path, skiprows=1, delimiter=',', usecols=AV_point_cols+DV_point_cols)
        np.savetxt(file_info['modelPath']+f'trainDataSelected/trainDataSelected{file_ID}.csv', data, delimiter=',',fmt='%s')
        result_dict[file_ID] = data 

    except Exception as e:  
        print(f"Error reading {file_path}: {e}")  

app1 = Flask(__name__)

@app1.route('/BuildModel',methods = ['POST'])
def build_model(response_json=None):
    model_path = response_json["modelPath"]
    train_file_names = response_json["trainFileNames"]
    # 连续型测点
    AV_points = response_json["AvPoints"]
    # 离散型测点
    DV_points = response_json["DvPoints"]

    num_train_files = len(train_file_names)
    num_AV_points = len(AV_points)
    num_DV_points = len(DV_points)

    #parameters are loaded.
    if not os.path.exists(model_path + 'trainDataSelected/'):
        os.makedirs(model_path + 'trainDataSelected/')

    # 为每个文件创建一个线程  
    data_selected = {}
    threads = []
    for i in range(num_train_files):
        train_file_path = model_path + 'trainData/' + train_file_names[i]
        t = threading.Thread(target=read_csv, args=(f'{i:03}', train_file_path, response_json, data_selected))  
        t.start()
        threads.append(t)
    
    # 等待所有线程完成  
    for t in threads:  
        t.join() 

    data = np.zeros([0, num_AV_points+num_DV_points])
    for i in range(num_train_files):
        data = np.r_[data, data_selected[f'{i:03}']]
    
    maxs = data[:, :num_AV_points].max(axis=0)
    mins = data[:, :num_AV_points].min(axis=0)

    data[:, :num_AV_points] = (data[:, :num_AV_points]-mins)/(maxs-mins+1e-10)

    data_dict = {}
    num_dict = {}
    for i in range(data.shape[0]):
        code = ''
        for j in data[i, num_AV_points:]: code += f'{int(j)}'
        if code not in data_dict.keys():
            data_dict[code] = data[i, :]
            num_dict[code] = 1
        else:
            data_dict[code] = np.r_[data_dict[code], data[i, :]]
            num_dict[code] += 1
    
    num_codes = len(data_dict.keys())
    mat_D = data
    mat_DD = np.zeros([mat_D.shape[0], mat_D.shape[0]])
    for r in range(mat_D.shape[0]):
        for c in range(mat_D.shape[0]):
            mat_DD[r, c] =  np.linalg.norm(mat_D[r, :] - mat_D[c, :])
    mat_G = np.linalg.pinv(mat_DD) 

    model_info = {}
    model_info["numTrainFiles"] = num_train_files
    model_info["numAvPoints"] = num_AV_points
    model_info["numDvPoints"] = num_DV_points
    model_info["maxs"] = maxs
    model_info["mins"] = mins
    model_info["matD"] = mat_D
    model_info["matG"] = mat_G
    with open(model_path+'modelInfo.pkl', 'wb') as f:
        pickle.dump(model_info, f)

    returnJson = {"msg": 'Build model successful!'}
    return jsonify(returnJson)

if __name__ == '__main__':
    app1.run(port=5000,debug=True)

