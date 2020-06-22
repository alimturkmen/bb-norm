TOTAL_FILE=97
NUMBER_OF_PROCESS=10
for process in $(seq 0 $((NUMBER_OF_PROCESS + 1))); do
    LENGTH=$((TOTAL_FILE / NUMBER_OF_PROCESS))
    START_INDEX=$((LENGTH * process))
    echo "$START_INDEX $((START_INDEX + LENGTH))"
    ./main.py ../cache/ $START_INDEX $LENGTH &
done
