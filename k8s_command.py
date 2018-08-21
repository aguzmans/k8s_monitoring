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

    def strip_kubectl_output(self, kubectloutput):
        k8s_output_command = string.split(kubectloutput[1], '\n')
        header = filter(None,k8s_output_command[0].split(' '))
        position = list()
        # Create tuple with pod name and READY vs Running position as headers of the output
        position.append([index for index, s in enumerate(header) if s == 'NAME'][0])
        position.append([index for index, s in enumerate(header) if s == 'READY'][0])
        k8s_output_command = k8s_output_command[1:]
        # remove spaces and convert to list.
        for i, val in enumerate(k8s_output_command):
            k8s_output_command[i] = filter(None,k8s_output_command[i].split(' '))
        count = len(k8s_output_command)
        # Remove elements no to be used (Leave Name and READY vs Wanted
        for ikey in range(0, count):
            aux_list = list()
            for kkey, kval in enumerate(k8s_output_command[ikey]):
                if kkey == position[0] or kkey == position[1]:
                    aux_list.append(k8s_output_command[ikey][kkey])
            k8s_output_command[ikey] = aux_list
        return k8s_output_command[:-1]

    def split_ready_vs_ready(self, arefined_list, position):
        for i, ival in enumerate(arefined_list):
            ival[position].split('/')
            arefined_list[i][position] = ival[position].split('/')
        return arefined_list

    def k8s_vs_zabbix_output(self,zabbix_list, k8s_list):
        exist_in_k8s = False
        for key_zabbix, a_zabbix_service in enumerate(zabbix_list):
            print a_zabbix_service
            count = len(k8s_list)
            found = 0
            for i_k8s in range(0, count):
                if a_zabbix_service[0] in k8s_list[i_k8s][0]:
                    found += int(k8s_list[i_k8s][1][0])
                if count-1 == i_k8s and found > 0:
                    print 'last and found: ', found

                    if found >= int(a_zabbix_service[1]):
                        exist_in_k8s = True
            a_zabbix_service.append(exist_in_k8s)
            zabbix_list[key_zabbix] = a_zabbix_service
        return zabbix_list

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
            # Get the zabbix post in list format from a string
            zabbix_pods_to_check = atool.convert_string_to_list_bidimentional(key_chain, "&", "=")
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
            # remove not needed stuff from kubernetes output
            k8s_clean_ouput = kube_obj.strip_kubectl_output(k8s_command)
            # Change the 1/2 format to array to make processing easier.
            k8s_clean_list = kube_obj.split_ready_vs_ready(k8s_clean_ouput, 1)
            # ZABBIX should vs Actual running
            k8s_running_result = kube_obj.k8s_vs_zabbix_output(zabbix_pods_to_check, k8s_clean_list)
            print k8s_running_result

        #commented out for fixing the monitoring functions and classes, this is temporary
        #     if len(k8s_output_command) >= 1:
        #         kube_obj.lists_kube_vs_zabbix(k8s_output_command, pods_to_check)
        #     else:
        #         print 'No pods found in namespace'
        # else:
        #     print return_value


    # def lists_kube_vs_zabbix(self, k8s_output, zabbix_list):
    #     result_list = list()
    #     print k8s_output
    #     date = tuple()
    #     found = False
    #     for ikey, ival in enumerate(zabbix_list):
    #         count = len(k8s_output)
    #         for kkey in range(0, count-1):
    #             if ival[0] in k8s_output[kkey]:
    #                 kval_k8s_list = k8s_output[kkey].split(' ')
    #                 kval_k8s_list = filter(None, kval_k8s_list)
    #                 split_running = kval_k8s_list[1].split('/')
    #                 if split_running[0] == split_running[1]:
    #                    data = (ival[0], 'OK')
    #                    result_list.append(data)
    #                    found = True
    #                    break
    #             elif kkey == count-2:
    #                 data = (ival[0], 'Fail')
    #                 result_list.append(data)
    #     counter=list(collections.Counter(result_list).items())
    #     aux_result = list()
    #     for i, val in enumerate(zabbix_list):
    #         if int(counter[i][1] + 1) == int(val[1]):
    #            aux_result.append('OK')
    #         elif int(counter[i][1]) == int(val[1]):
    #         #if int(counter[i][1]) == int(val[1]):
    #            aux_result.append('OK')
    #         else:
    #            aux_result.append('Fail')
    #     if 'Fail' in aux_result:
    #         print 'Fail'
    #     else:
    #         print 'OK'