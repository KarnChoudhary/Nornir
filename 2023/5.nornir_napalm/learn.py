import os, json, re
os.system("clear")

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
command = "show inventory"
command1 = "show license all | include Start Date"
command2 = "show license all | include End Date"

results = nr.run(task=napalm_cli, commands=[command,command1,command2])

print_result(results)
# we got results for all the devices here. which is called as "results"                     
if command == "show inventory":        
    import csv
    filename = "abc.csv"

    lines = []
    lines.append(["Hostname", "Name", "Description", "Serial Number", "Start Date", "End Date"])

    
    for node,multiresult in results.items():
        # now we are choosing a particular device / hostname to dive deep
        print("node", node)
        print("multiresult - >", multiresult)
        for result in multiresult:
            print("result", type(result))
            print(result)

            # https://nornir.readthedocs.io/en/latest/api/nornir/core/task.html
            
        
    #     for b in results[node]:
    #         # now we are checking all the sub-tasks / results (cell unit of single host -> single device -> single tasks dictionary)
    #         print(b)
    #         print("---b--" *20)
    #         print(results[node])
    #         print("---RN--" *20)
            
    #         if b.result:               
    #             for key,t in b.result.items():   
    #                 print(t)
    #                 print("---t--" *20)             
    #                 if t:
    #                     # now we got the result from terminal but it has a simple string like output.
    #                     # hence we need to split all the names of parts of machine
    #                     newstr = t.split("NAME")                    
    #                     print(newstr)
    #                     print("----new str-----")
    #                     for n in newstr:
    #                         text1 = "NAME" + n
    #                         # going to check name and desc using regex patterns
    #                         matches1 = re.search(r'NAME: "(.*?)",\sDESCR: "(.*?)"', text1)                        
                            
    #                         if matches1:
    #                             name = matches1.group(1)
    #                             descr = matches1.group(2)
    #                             sn = text1.split("SN:")[1]    # since we know that SN is in last of text1

    #                             if descr.startswith("C93") or descr.startswith("C95"):
    #                                 lines.append([node, name,descr,sn.strip()])


    #                 if "Date" in str(t).strip():
    #                     for l in lines[1:]:
    #                         bbb = t.strip().split(":")[1]
    #                         print(l, bbb)
    #                         l.append(bbb)

    # with open(filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(lines)

    # print("Done. Check abc.csv")

                        