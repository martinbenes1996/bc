#!/bin/bash


alarm() {
   ( \speaker-test --frequency $1 --test sine )&
   pid=$!

   \sleep ${2}s
   \kill -9 $pid 
}


alarm $1 $2
