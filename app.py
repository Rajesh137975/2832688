# from flask import Flask, request, render_template, send_from_directory
from telnetlib import STATUS
from flask import Flask, request
# from werkzeug.utils import secure_filename
from itertools import chain, combinations
import os
import time
import io
import csv

app = Flask(__name__)

apriori_dict = {
    "error": None, "result": "", "File": None, "Total": None
}

@app.route('/')
def form():
    return """
       <html>
        <head>
        <body>
            <div style="
            width: 100%;
            margin: auto;
            margin-top: auto;
            max-width: 438px;
            font-size: 24px;
            font-family: serif;
            box-shadow: blue 0px 0px 0px 2px inset, rgb(255 255 255) 10px -10px 0px -3px, rgb(31 193 27) 10px -10px, rgb(255 255 255) 20px -20px 0px -3px, rgb(255 217 19) 20px -20px, rgb(255 255 255) 30px -30px 0px -3px, rgb(255 156 85) 30px -30px, rgb(255 255 255) 40px -40px 0px -3px, rgb(255 85 85) 40px -40px;
            padding: 26px;
            margin-top: 66px;
            ">
            <h1>CIS550 Apriori Algorithm</h1>
            <div>
                <div
                class="row justify-content-center align-items-center"
                >
                <div >
                    <div >
                    <form
                        method="post" enctype="multipart/form-data"
                        action="/algorithm"
                    >
                        <h2>Apriori Algoritm</h2>
                        <p>Rajesh Pasumarthi</p>
                        <input type="file" name="input_csv" />
                        <input placeholder="Minimum support" type="text" name="mim_sup" />

                        <input type="submit" />
                    </form>
                    
                    </div>
                </div>
                </div>
            </div>
            </div>
        </body>
        </html>
    """

def add_to_sets(items):
    add_to_set = set()
    for item in items:
        add_to_set.add(item)
    return add_to_set

def subset_freq(candidate, data_set, mim_sup):
    re_formatted_candidate = set()
    list_of_items = list(candidate)
    for item in range(len(list_of_items)):
        i = 0
        for data in data_set:
            if list_of_items[item].issubset(data):
                i += 1
        if i >= mim_sup:
            re_formatted_candidate.add(list_of_items[item])
    return re_formatted_candidate

def candidate_item(array_frequent , itr):
    list_ = []
    for i in array_frequent:
        for j in array_frequent:
            if len(i.union(j)) == itr:
                list_.append(i.union(j))
    return set(list_)


def algorithm_apriori(read_lines, mim_sup):
    re_formatted_data = []
    item_sets = set()
    iterator = 2
    for row in read_lines:
        tex_split = str(row.strip()).split(", ")
        line_no = tex_split.pop(0)
        item_sets = item_sets.union(tex_split)
        data = set(transform_arr(tex_split))
        data.add(line_no + 'key')
        re_formatted_data.append(frozenset(data))

    set_format = set(frozenset([int(j)]) for j in item_sets)
    freq_i = subset_freq(set_format, re_formatted_data, mim_sup)
    freq_set = add_to_sets(freq_i)
    while True:
        candidate_items = candidate_item(freq_i, iterator)
        temp_candidate_items = set()
        for candidate in candidate_items:
            subsets = subset(candidate, iterator)
            count = 0
            for item in subsets:
                if item in freq_i:
                    count += 1
            if count == len(subsets):
                temp_candidate_items.add(candidate)
        candidate_items = temp_candidate_items
        freq_i = subset_freq(candidate_items, re_formatted_data, mim_sup)
        if len(freq_i) != 0:
            for candidate in freq_i:
                subsets = subset(candidate, iterator)
                freq_set.add(candidate)
                freq_set = freq_set - subsets

            iterator += 1
        else:
            break
    apriori_dict["total"] = len(freq_set)
    return [set(z) for z in freq_set]



def subset(array_frequent, itr):
    return set([frozenset(list(z)) for z in
                list(chain.from_iterable(combinations(array_frequent, j) for j in range(itr - 1, itr)))])

def transform_arr(items):
    list_ = []
    for i in items:
        list_.append(int((i)))
    return list_



@app.route('/algorithm', methods=["POST"])
def transform_view():
    time1 = time.time()
    file_input = request.files['input_csv']
    mim_sup = request.form.get('mim_sup')
    filename = file_input.filename
    if not file_input:
        return "No file"
    stream = io.StringIO(file_input.stream.read().decode("UTF8"), newline=None)
    csv_file = csv.reader(stream)
    #print("file contents: ", file_contents)
    #print(type(file_contents))
    input_arr = []
    for index,value in enumerate(csv_file):
        text = ""
        for i in value:
            text = text+i+","
        input_arr.append(text[:-1])
    apriori_dict["result"] = algorithm_apriori(input_arr, int(mim_sup))
    return str(  str(apriori_dict['result'])+''+" Number of sets: "+str(len(apriori_dict['result']))+' file name is :'+filename+' Execution time:'+str(time.time() - time1  ) )