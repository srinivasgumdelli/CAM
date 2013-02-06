$port = $1
$host = $2
sh ./executables/wbest_rcv -h $host &
sh ./executables/wbest_snd &
