from sys import argv
import json
def usage():
    print("python judge.py [testdata_file_path] [output_file_path]")

if len(argv) < 2:
    usage()
    exit(1)

with open(argv[1], 'r', encoding='UTF-8') as f:
    dic = json.load(f)
    dic = dic["StandingsData"]
    dic = [s for s in dic if not s["IsRated"]]
with open(argv[1], 'w', encoding='UTF-8') as f:
    json.dump(dic, f)