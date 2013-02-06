#$srv = $1
#$port1 = $2
#$port2 = $3
sh ./script_snd.sh &
sh ./script_rcv.sh &
./executables/assolo_run -S 184.169.155.37 -R localhost -t 100 -J 4
