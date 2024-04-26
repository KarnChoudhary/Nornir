import os, json, re
os.system("clear")                               # https://nornir.readthedocs.io/en/latest/api/nornir/core/task.html  (URGENT- VERY IMP)

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
command = "show inventory"
command1 = "show license all | include Start Date"
command2 = "show license all | include End Date"

results = nr.run(task=napalm_cli, commands=[command,command1,command2])
print("type of results - >", type(results))
print_result(results)
#It basically is a dict-like object class that aggregates the results for all devices. You can access each individual result by doing my_aggr_result["hostname_of_device"].
# we got results for all the devices here. which is called as "results"                     
if command1 == "show license all | include Start Date":        
    import csv
    filename = "abc.csv"

    lines = []
    lines.append(["Hostname", "Name", "Description", "Serial Number", "Start Date", "End Date"])

    for hostname, multiresult in results.items():
        host_result = multiresult[0]
        result= host_result.result
        inventory= result.get("show inventory")

        start_date = result.get("show license all | include Start Date")[len("Start Date: "):]
        print("start date - >",start_date)
        
        end_date = result.get("show license all | include End Date")[len("End Date: "):]
        print("end date - >",end_date)

        print("type of start/end date - >",type(start_date))
        print("type of inventory - >",type(inventory))
        print("inventory ->",inventory)

        print("----"*20)

        newstr = inventory.split("NAME")                               
        for n in newstr:
                    text1 = "NAME" + n
                            # going to check name and desc using regex patterns
                    matches1 = re.search(r'NAME: "(.*?)",\sDESCR: "(.*?)"', text1)                        
                            
                    if matches1:
                        name = matches1.group(1)
                        descr = matches1.group(2)
                        sn = text1.split("SN:")[1]    # since we know that SN is in last of text1

                        if descr.startswith("C93") or descr.startswith("C95"):
                            lines.append([hostname, name,descr,sn.strip(), start_date.split("UTC")[0].strip(),end_date.split("UTC")[0].strip()])

        #lines.append([hostname, start_date,end_date])  # Unpack license info for CSV

    with open(filename, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(lines)

        print(f"information written to '{filename}'.")

    '''
    for node,multiresult in results.items():  #we cant use .items() on class type ? , used in dict-type objects only.
        # now we are choosing a particular device / hostname to dive deep
        print("results.items - >", results.items())
        #It basically is a dict-like object class that aggregates the results for all devices. You can access each individual result by doing my_aggr_result["hostname_of_device"].

        print("node", node)
        print("type of multiresult - >", type(multiresult))
        #print("multiresult - >", multiresult.items())           - AttributeError: 'Result' object has no attribute 'items'
        print("multiresult - >", multiresult)
        #It is basically is a list-like object that gives you access to the results of all subtasks for a particular device/task.
        for results in multiresult:
            print("type of result ->", type(results))
            #result <class 'nornir.core.task.Result'>
            print("results -- >", results)
            #print("results.items -- >",results.items())         - AttributeError: 'Result' object has no attribute 'items'
            print("---" *20)
            for b in results.items():
                print("b -- >",b)         
            '''
    
           
            
        
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

                        