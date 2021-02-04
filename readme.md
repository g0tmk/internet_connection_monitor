# Internet Connection Monitor

 - `python3 monitor.py`: run forever, saving internet status to output.csv
 - `./repeatedly_generate_graphs.sh`: run forever, saving graphs to `graph_*.png` every 5 seconds
 - `python3 -m http.server`: run a http server to make available at http://ip:8000/graph_6h.png

### TODO:

 - Make a SplitLogFile class which allows writing to a log file which is automatically split

        # example
        slf = splitlogfile.SplitIntoChunksByWriteDate(
                'output.csv',
                period=splitlogfile.DAILY,
                auto_delete_older_than_timedelta=datetime.timedelta(days=365),
                auto_compress_older_than_timedelta=datetime.timedelta(days=31))
        slf.write(line)
        slf.write(line)

 - Figure out how to start on boot
 - Add labels to graphs generated by summary.py

### REQUIREMENTS

 - python 3.6+

### extras

    python3 alive.py      # check if a service is pingable
    python3 bandwidth.py  # check download speed
    python3 latency.py    # check ping times to an address

