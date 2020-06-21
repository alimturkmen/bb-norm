TOTAL_FILE=97
NUMBER_OF_PROCESS=10
for process in $(seq 0 $((NUMBER_OF_PROCESS))); do
    LENGTH=$((TOTAL_FILE / NUMBER_OF_PROCESS))
    START_INDEX=$((LENGTH * process))
    echo "$START_INDEX $((START_INDEX + LENGTH))"
    ./mainv2.py /mnt/lin/home/fmk/projects/tmp/cmpe493cache/ $START_INDEX $LENGTH &
done
