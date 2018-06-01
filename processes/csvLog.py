"""
a) First took all the keys of dictionary and sorted it, which is not necessary.
b) Created a result list which appends value related the headers which is key of our input dict and if key is not available then .get() will return None. 
   So result list will contain lists for rows data.
c) Wrote header and each row from result list in csv file
"""

data_dict = [{ "Header_1":"data_1", "Header_2":"data_2", "Header_3":"data_3"},
             { "Header_1":"data_4", "Header_2":"data_5", "Header_3":"data_6"},
             { "Header_1":"data_7", "Header_2":"data_8", "Header_3":"data_9", "Header_4":"data_10"},
             { "Header_1":"data_11", "Header_3":"data_12"},
             { "Header_1":"data_13", "Header_2":"data_14", "Header_3":"data_15"}]

"""
   In the third dict we have extra key, value.
   In forth we dont have have header_2 were we aspect blank value in our csv file.
"""
process_data = [ [k,v] for _dict in data_dict for k,v in _dict.items() ]

headers = [ i[0] for i in process_data ]
headers = sorted(list(set(headers)))

result = []
for _dict in data_dict:
    row = []
    for header in headers:
        row.append(_dict.get(header, None))
    result.append(row)


import csv
with open('demo.csv', 'a') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';')
    spamwriter.writerow(headers)    
    for r in result:
        spamwriter.writerow(r)
