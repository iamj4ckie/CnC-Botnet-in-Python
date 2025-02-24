#!/bin/bash

# Define values for experiments
INTERVALS=(10 5 1 0)
THREADS=(1 2 5)
REPETITIONS=(50 100 300)
LOG_DIR="attack_logs"
FABFILE_PATH="fabfile.py"  # Adjust this path if needed

# Ensure the log directory exists
mkdir -p $LOG_DIR

# Function to update NUM_THREADS_PER_COWRIE in fabfile.py
update_threads() {
    local new_threads=$1
    sed -i "s/^NUM_THREADS_PER_COWRIE = [0-9]\+/NUM_THREADS_PER_COWRIE = $new_threads/" "$FABFILE_PATH"
}

# Iterate over different threads per Cowrie
for threads in "${THREADS[@]}"; do
    echo "Updating threads to $threads..."
    update_threads $threads

    # Iterate over different interval values
    for interval in "${INTERVALS[@]}"; do
        for repetitions in "${REPETITIONS[@]}"; do
            echo "Running tests with NUM_THREADS_PER_COWRIE=$threads, interval=$interval, repetitions=$repetitions..."

            # Run the curl attack
            fab run-command "curl http://reverse-proxy/dynamic" --repetitions $repetitions --interval $interval
            mv attack_log.csv "$LOG_DIR/curl_threads${threads}_interval${interval}_repetitions${repetitions}.csv"

            # Run the wget attack
            fab run-command "wget http://reverse-proxy/dynamic" --repetitions $repetitions --interval $interval
            mv attack_log.csv "$LOG_DIR/wget_threads${threads}_interval${interval}_repetitions${repetitions}.csv"

            echo "Finished test for NUM_THREADS_PER_COWRIE=$threads, interval=$interval, repetitions=$repetitions."
        done
    done
done

echo "All tests completed. Logs are stored in $LOG_DIR/"
