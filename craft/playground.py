'''
Given a time represented in the format "HH:MM", form the next closest time by reusing the current digits. 
There is no limit on how many times a digit can be reused.

You may assume the given input string is always valid. For example, "01:34", "12:09" are all valid. 
"1:34", "12:9" are all invalid.

Example 1:
Input: time = "19:34"
Output: "19:39"
Explanation: The next closest time choosing from digits 1, 9, 3, 4, is 19:39, which occurs 5 minutes later.
It is not 19:33, because this occurs 23 hours and 59 minutes later.

current_time_hours = 19
current_time_min = 34
input_digits = [1,9,3,4]

T:O(1)
S:O(1)

Example 2:
Input: time = "23:59"
Output: "22:22"
Explanation: The next closest time choosing from digits 2, 3, 5, 9, is 22:22.
It may be assumed that the returned time is next day's time since it is smaller than the input time numerically.
 

Constraints:
time.length == 5
time is a valid time in the form "HH:MM".
0 <= HH < 24
0 <= MM < 60
'''

import itertools

def find_next_time(input_time):
    input_time = input_time.split(":")
    input_hour = input_time[0]
    input_min = input_time[1]
    
    input_digits = [input_hour[0],input_hour[1],input_min[0],input_min[1]]
    possible_output = list(itertools.product(input_digits,repeat=len(input_digits)))
    
    
    input = "".join(str(element) for element in input_digits)

    outputs = []
    for each_possible_output in possible_output:
        output = list(each_possible_output)
        hours = str(output[0])+str(output[1])
        minutes = str(output[2])+str(output[3])
        if int(hours) < 24 and int(minutes) < 60:
            output = "".join(str(element) for element in each_possible_output)
            outputs.append(output)
    
    outputs.sort()
    #print(outputs)
    for i in range(len(outputs)):
        if outputs[i] == input:
            if i+1<len(outputs):
                return outputs[i+1]
            else:
                return outputs[0]
        
        
print(find_next_time("19:34"))
print(find_next_time("23:59"))
