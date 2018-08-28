Development phase. This is tested in Linux:

1- This is and agent sript for Zabbix. 
You should put it on the agent_bin folder.
this file should be accesible by the Zabbix user.

2- Edit the configuration file of the agent to have a line like this.<br />
<code>
UserParameter=kubernetes.pods_count[*],                    python /var/lib/nc_zabbix/agent_bin/k8s_command.py $1 $2 $3 $4 $5 $6 <br />
UserParameter=kubernetes.pods_count_broken[*],             python /var/lib/nc_zabbix/agent_bin/k8s_command.py $1 $2 $3 $4 $5 $6 <br />
</code>

3- Restart agent. 
<code>
systemctl restart zabbix_agent
</code>

4- You can test it with a command like this:
<code>
sudo -u zabbix_user zabbix_agentd -t kubernetes.pods_count[activity_1.attendance_1.auth_1.billing_1.cash_1.cashier_1.customer_1.designer_1.eureka_1.lottery_1.message_1.order_1.plastic_1.report_1.reserve_1.s3connect_1.shop_1.user_1.wallet_1.websocket_1.yoga_1,2f7661722f6c69622f6e635f7a61626269782f2e6b7562652f636f6e666967,626f6b612d70726f64] -c /etc/nc_zabbix/nc_zabbix_agentd.conf
</code>