#!/bin/bash



i=0
success=0
cd tests
programs="$(find -name "test-*.py")"
cd ..
for p in $programs; do
    i=$((i + 1))
    
    printf "Test $i: "
    python3 tests/$p
    # get status
    if [ $? == 0 ] ; then
        echo "SUCCESS"
        success=$((success + 1))
    else
        echo "FAIL"
    fi

done

echo "$success/$i tests successful."


