#!/usr/bin/python
###########################################
# Zabbix agent kubectl monitoring script  #
###########################################

# Standard imports
import argparse
import os
import string

# Specific imports from standard libraries
from subprocess import check_output, CalledProcessError

# No personal imports

class Kubernetes_monitoring:
    def __init__(self):
        self.args_list = self.__get_parameters()

    def __get_parameters(self):
        """Get parameters from command line or in this case probably coming from zabbix server via the againt
        invocation"""
        parser_object = argparse.ArgumentParser()
        parser_object.add_argument('Parameter1', metavar='N', nargs='+',
                                   help='Parameter1 is the list of pods to check formated item=X&item2=Y. '
                                        'The secons space separated element is the path to kubectl config '
                                        'The third parameters is the namespace to search.')
        args = parser_object.parse_args()
        args_list, unknown = parser_object.parse_known_args()
        return args_list

    def strip_kubectl_output(self, kubectloutput, findlist=['NAME', 'READY', 'RESTARTS']):
        """Filter kubectl output to simplyfy it's usage leaving it in three columns NAME, READY and RESTARTS
        In the future need to add json output support as of now TXT is enough"""
        k8s_output_command = string.split(kubectloutput[1], '\n')
        header = filter(None, k8s_output_command[0].split(' '))
        position = list()
        # Create tuple with pod name and READY vs Running position as headers of the output
        for jkey, jval in enumerate(findlist):
            position.append([index for index, s in enumerate(header) if s == findlist[jkey]][0])
        k8s_output_command = k8s_output_command[1:]
        # remove spaces and convert to list.
        for i, val in enumerate(k8s_output_command):
            k8s_output_command[i] = filter(None, k8s_output_command[i].split(' '))
        count = len(k8s_output_command)
        # Remove elements no to be used (Leave Name and READY vs Wanted
        for ikey in range(0, count):
            aux_list = list()
            for kkey, kval in enumerate(k8s_output_command[ikey]):
                if kkey in position:
                    aux_list.append(k8s_output_command[ikey][kkey])
            k8s_output_command[ikey] = aux_list
        return k8s_output_command[:-1]

    def split_ready_vs_ready(self, a_refined_list, position):
        """Split the READY column intro an array with both values based on @a_refined_list and @position"""
        for i, ival in enumerate(a_refined_list):
            ival[position].split('/')
            a_refined_list[i][position] = ival[position].split('/')
        return a_refined_list

    def k8s_vs_zabbix_output(self, zabbix_list, k8s_list, a_tools, k8s_config_path, k8s_nemespace):
        """Function to compare the kubernetes output @k8s_list and the zabbix macro @zabbix_list this retusn the same
        Zabbix list with a third value set to True or False in @zabbix_list at return time"""
        # print zabbix_list
        for key_zabbix, a_zabbix_service in enumerate(zabbix_list):
            exist_in_k8s = False
            count = len(k8s_list)
            found = 0
            reason = ''
            for i_k8s in range(0, count):
                if a_zabbix_service[0] in k8s_list[i_k8s][0]:
                    found += int(k8s_list[i_k8s][1][0])
                #check if we found any at the last execution of the search.
                if count - 1 == i_k8s and found > 0:
                    # if found more or equal to sabbix config number then OK
                    if found >= int(a_zabbix_service[1]):
                        exist_in_k8s = True
                    # else is found but not as many
                    elif found > 0 and found < int(a_zabbix_service[1]):
                        reason = 'not enogu PODs for: ' + a_zabbix_service[0] + ', need: ' + a_zabbix_service[1] + \
                                 ', but found: ' + str(found)
                    # Asume other type of failure need to check error
                    else:
                        # Assume FAIL count is lower
                        reason = self.__k8s_fail_reason(k8s_list[i_k8s], a_zabbix_service[0], a_tools,
                                                             k8s_config_path, k8s_nemespace, 2)
                elif count - 1 == i_k8s:
                    reason = 'pod containing ' + a_zabbix_service[0] + ' NOT found'

            a_zabbix_service.append(exist_in_k8s)
            a_zabbix_service.append(reason)
            zabbix_list[key_zabbix] = a_zabbix_service
        return zabbix_list

    def __k8s_fail_reason(self, a_pod_output, a_zabbix_pod, a_tools,
                          k8s_config_path, k8s_nemespace, restarts_possition=2):
        a_pod_name = a_pod_output[0]
        fail_details = 'Fail: ' + a_pod_name
        print a_zabbix_pod
        print a_pod_name.find(a_zabbix_pod)
        if a_pod_name.find(a_zabbix_pod) >= 0:
            # 1- check restarts count of the pod
            # 2- if restarts greater than 0
            if int(a_pod_output[restarts_possition]) > 0:
                fail_details = fail_details + ', Restarts=' + a_pod_output[restarts_possition]
                # 3- then check the descriptiong and find error vs reason'
                shell_command = 'kubectl describe pods ' + a_pod_name + ' ' + k8s_config_path
                if k8s_nemespace is not None and k8s_namespace != '':
                    shell_command = shell_command + ' --namespace=' + k8s_nemespace
                k8s_describe_pod = a_tools.main_execution_function(shell_command)
                describe_output = ''
                if k8s_describe_pod[0] == 0:
                    describe_output = string.split(k8s_describe_pod[1], '\n')
                for h_key, h_value in enumerate(describe_output):
                    if 'Last State:' in h_value or 'Reason' in h_value:
                        fail_details = fail_details + ', ' + ' '.join(h_value.split())
        else:
            fail_details = fail_details + ' POD not found'

        return fail_details


class Tools:
    def main_execution_function(self, shell_command, wait_cmd=True):
        """Execute external command and return output"""
        return_code = 0
        stdout = stderr = ''
        try:
            stdout = check_output(shell_command, shell=True)
        except CalledProcessError as e:
            return_code = e.returncode
            stderr = e.output
        return return_code, stdout, 'stderr: ' + str(stderr)

    def convert_string_to_list_bidimentional(self, string, first_dimesion, second_dimesion):
        """Filter a zabbix macro in string fromat into a python list to be used further
        Args:
            string (str): The Zabbix string coming from macro something like; nginx=2&mysql=3&...
            first_dimension (character): In this case & as my own standard
            second_dimension (character): In this case the = symbol

        Returns:
            two_dimantion_array  (list of List): A list containing the same strign fromthe begining divided in different
             pod names to check
            """
        first_dimention_array = string.split(first_dimesion)
        two_dimantion_array = list()
        for key, value in enumerate(first_dimention_array):
            aux = first_dimention_array[key]
            two_dimantion_array.append(aux.split(second_dimesion))
        return two_dimantion_array

    def hex_to_test(self, hex_string):
        """Convert text from zabbix HEX string"""
        try:
            key_chain = hex_string.decode("hex")
        except Exception, e:
            key_chain = 'Fail ' + str(e)
        return key_chain


try:
    if __name__ == '__main__':
        # declare main monitoring script
        kube_obj = Kubernetes_monitoring()
        atool = Tools()
        # Gep HEX param and attempt to convert to normal string
        parameters = kube_obj.args_list.Parameter1
        key_chain = ''
        return_value = 'OK'
        if len(parameters) >= 1:
            key_chain = parameters[0]
        else:
            key_chain = 'nginx=2'
        if len(parameters) >= 2:
            kubectlp_config_path = atool.hex_to_test(parameters[1])
        else:
            kubectlp_config_path = '/var/lib/nc_zabbix/.kube/config'
        if len(parameters) >= 3:
            k8s_namespace = atool.hex_to_test(parameters[2])
        else:
            k8s_namespace = ''

        if key_chain == '' or key_chain == None:
            # should never happen is a test value
            print "4444"
        else:
            if return_value == 'OK':
                # Get the zabbix post in list format from a string
                zabbix_pods_to_check = atool.convert_string_to_list_bidimentional(key_chain, ".", "_")
                # Check if path to kubectl config was given.
                k8s_config_path = ''
                if kubectlp_config_path:
                    if os.path.exists(kubectlp_config_path):
                        k8s_config_path = '--kubeconfig=' + kubectlp_config_path
                # Check if namespace parameter was passed
                k8s_nemespace = ''
                if k8s_namespace:
                    if k8s_namespace != '':
                        k8s_nemespace = '--namespace=' + k8s_namespace
                k8s_command = atool.main_execution_function('kubectl ' + k8s_config_path + ' get pods ' + k8s_nemespace)
                # remove not needed stuff from kubernetes output
                k8s_clean_ouput = kube_obj.strip_kubectl_output(k8s_command)
                # Change the 1/2 format to array to make processing easier.
                k8s_clean_list = kube_obj.split_ready_vs_ready(k8s_clean_ouput, 1)
                # ZABBIX should vs Actual running
                k8s_running_result = kube_obj.k8s_vs_zabbix_output(zabbix_pods_to_check, k8s_clean_list, atool,
                                                                   k8s_config_path, k8s_nemespace)
                # Check if all is OK or some are Failed
                counter_final = len(k8s_running_result)
                global_success = False
                for key_result, a_k8s_running_result in enumerate(k8s_running_result):  # type: (int, object)
                    if not k8s_running_result[key_result][2]:
                        # CALL NEW function to add output!!!! pass it: k8s_running_result[key_result][2], k8s_clean_list
                        #kube_obj.k8s_fail_reason(k8s_running_result[key_result], k8s_clean_list)
                        print k8s_running_result[key_result][3]
                        break
                    elif k8s_running_result[key_result][2] == True and counter_final - 1 == key_result:
                            print 'OK'
except Exception, e:
    print 'Fail ' + str(e)
