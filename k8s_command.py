#!/usr/bin/python
#####################################
# Zabbix kubectl monitoring script  #
#####################################
# Standard imports
import argparse
import os
import subprocess
import string
import collections

from subprocess import check_output, CalledProcessError

class Kubernetes_monitoring:
    def __init__(self):
        self.args_list = self.__get_parameters()

    def __get_parameters(self):
        parser_object = argparse.ArgumentParser()
        parser_object.add_argument('Parameter1', metavar='N', nargs='+',
                   help='Parameter1 is the list of pods to check formated item=X&item2=Y. '
                        'The secons space separated element is the path to kubectl config '
                        'The third parameters is the namespace to search.')
        args = parser_object.parse_args()
        args_list, unknown = parser_object.parse_known_args()
        return args_list

    def stip_kubectl_output(self, kubectloutput):
        k8s_output_command = string.split(kubectloutput[1], '\n')
        header = filter(None,k8s_output_command[0].split(' '))
        position_name = [index for index, s in enumerate(header) if s == 'NAME']
        position_ready = [index for index, s in enumerate(header) if s == 'READY']
        print position_name, position_ready


    def lists_kube_vs_zabbix(self, k8s_output, zabbix_list):
        result_list = list()
        print k8s_output
        date = tuple()
        found = False
        for ikey, ival in enumerate(zabbix_list):
            count = len(k8s_output)
            for kkey in range(0, count-1):
                if ival[0] in k8s_output[kkey]:
                    kval_k8s_list = k8s_output[kkey].split(' ')
                    kval_k8s_list = filter(None, kval_k8s_list)
                    split_running = kval_k8s_list[1].split('/')
                    if split_running[0] == split_running[1]:
                       data = (ival[0], 'OK')
                       result_list.append(data)
                       found = True
                       break
                elif kkey == count-2:
                    data = (ival[0], 'Fail')
                    result_list.append(data)
        counter=list(collections.Counter(result_list).items())
        aux_result = list()
        for i, val in enumerate(zabbix_list):
            if int(counter[i][1] + 1) == int(val[1]):
               aux_result.append('OK')
            elif int(counter[i][1]) == int(val[1]):
            #if int(counter[i][1]) == int(val[1]):
               aux_result.append('OK')
            else:
               aux_result.append('Fail')
        if 'Fail' in aux_result:
            print 'Fail'
        else:
            print 'OK'


    def __times_so_far(self, ls):
        out = [0]*len(ls)
        for i in xrange(len(ls)):
            out[i] = ls[:i].count(ls[i])
        return out


class Tools:
    def convert_string_to_list_bidimentional(self, string, first_dimention, second_dimention):
        first_dimention_array = string.split(first_dimention)
        two_dimantion_array = list()
        for key,value in enumerate(first_dimention_array):
            aux = first_dimention_array[key]
            two_dimantion_array.append(aux.split(second_dimention))
        return two_dimantion_array

    def main_execution_function(self, shell_command, wait_cmd=True):
        return_code = 0
        stdout = stderr = ''
        try:
            stdout = check_output(shell_command, shell=True)
            #stdout = stdout.splitlines()
        except CalledProcessError as e:
            return_code = e.returncode
            stderr = e.output
        return return_code, stdout, 'stderr: ' + str(stderr)


if __name__ == '__main__':
    #declare main monitoring script
    kube_obj = Kubernetes_monitoring()
    # Gep HEX param and attempt to convert to normal string
    parameters = kube_obj.args_list.Parameter1
    #print hex_chain
    key_chain = ''
    return_value = 'OK'
    try:
        key_chain = parameters[0].decode("hex")
    except Exception, e:
        return_value = str(e)
        return_value = 'FAIL'
        exit()


    if key_chain == '' or  key_chain == None:
        #should never happen is a test value
        print "4444"
    else:
        if return_value == 'OK':
            atool = Tools()
            pods_to_check = atool.convert_string_to_list_bidimentional(key_chain, "&", "=")
            # k8s_command = atool.main_execution_function("kubectl --kubeconfig=/var/lib/nc_zabbix/.kube/config_boka get pods --namespace=boka-prod")
            # Check if path to kubectl config was given.
            k8s_config_path = ''
            if len(parameters) >= 2:
                if os.path.exists(parameters[1]):
                    k8s_config_path = '--kubeconfig=' + parameters[1]
            # Check if namespace parameter was passed
            k8s_nemespace = ''
            if len(parameters) >= 3:
                if parameters[2] != '':
                    k8s_nemespace = '--namespace=' + parameters[2]
            k8s_command = atool.main_execution_function('kubectl ' + k8s_config_path +' get pods ' + k8s_nemespace)
            kube_obj.stip_kubectl_output(k8s_command)
        #     if len(k8s_output_command) >= 1:
        #         kube_obj.lists_kube_vs_zabbix(k8s_output_command, pods_to_check)
        #     else:
        #         print 'No pods found in namespace'
        # else:
        #     print return_value