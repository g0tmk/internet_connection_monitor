#!/usr/bin/env bash

make_all_graphs () {
	nice python3 summary.py --csv_input_filename output.csv --graph_filename graph_6h.png  --quiet --start_n_hours_ago 6
	nice python3 summary.py --csv_input_filename output.csv --graph_filename graph_24h.png --quiet --start_n_hours_ago 24
	nice python3 summary.py --csv_input_filename output.csv --graph_filename graph_all.png --quiet
}

while true
do
	echo "generating..."
	make_all_graphs
	echo "done; pausing for 5 seconds"
	sleep 5
done

