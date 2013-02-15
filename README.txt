Cloud Accessibility Measurement (CAM)
Computer Science Department, Montana State University
Srinivas Gumdelli (gumdelli@cs.montana.edu) and Mike Wittie (mwittie@cs.montana.edu)


OVERVIEW

We are developing a tool for passive measurement of network performance between cloud datacenters and arbitrary Internet hosts. Currently we would like to evaluate the accuracy of existing network path measurement tools representative of a breadth of measurement techniques, packet pairs, self-induced congestion, etc.. 


MEASUREMENT AND DATA COLLECTION

The included scripts will invoke several tools to measure network performance between your this machine and several cloud datacenters. The tools included in this package are:

Iperf - http://iperf.sourceforge.net/
Assolo - http://netlab-mn.unipv.it/assolo/
Pathload - http://www.cc.gatech.edu/fac/Constantinos.Dovrolis/bw-est/pathload.html
WBest - http://web.cs.wpi.edu/~claypool/papers/wbest/
MultiQ - http://pdos.csail.mit.edu/papers/multiq:imc04.pdf
Actual TCP and UDP transfers of bulk data

The scripts will run these tools sequentially and save their output (TCP throughput, available bandwdith, path capacity) in our database. We will also save your IP address, network type (WiFi/Ethernet), and time of individual measurements. In the case of MultiQ, we will save pcap files only of files transfered between your machine and our datacenters - no private traffic will be collected.


EXECUTION OF SCRIPTS

We would like to measure residential networks, so if you are able, please run the measurements from home. To start the scripts please invoke the following commands:

python start.py

We are assuming you are running Linux have Python 2.6 installed on your machine. 
If you have any questions, please contact us via email.
