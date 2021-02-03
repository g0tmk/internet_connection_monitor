#!/usr/bin/env bash

make_all_graphs () {
	python3 summary.py --quiet --start_n_hours_ago 6 graph_6h.png
	python3 summary.py --quiet --start_n_hours_ago 24 graph_24h.png
	python3 summary.py --quiet graph_all.png
}

while true
do
	echo "generating..."
	make_all_graphs
	echo "done; pausing for 5 seconds"
	sleep 5
done

