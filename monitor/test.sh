#!/bin/bash



i=0
success=0
cd tests
programs="$(find -name "test-*.py")"
cd ..
echo "Running tests..."
echo "============================="
for p in $programs; do
    i=$((i + 1))
    
    echo -e "\e[33mTest $i:\e[0m \c"
    python3 tests/$p > /dev/null
    # get status
    if [ $? == 0 ] ; then
        echo -e "\e[1;32mSUCCESS\e[0m"
        success=$((success + 1))
    else
        echo -e "\e[1;31mFAIL\e[0m"
    fi

done

echo "============================="
echo "$success/$i tests successful."


