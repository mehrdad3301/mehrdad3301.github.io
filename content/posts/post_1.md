---
title: "Answering range queries efficiently using segment trees and lazy propogation"
date: 2023-08-29T02:01:58+05:30
description: " " 
tags: [algorithms, data structures, range queries, competitive programming]
---
 
### problem statement 

Given an initial sequence, we will be asking two types of queries
1. ask l r : this query asks for the sum of numbers from `l` to `r` in the interval
2. add l r : this query adds 1 to number at l, 2 to l + 1, 3 to l + 2 and so on

Our task is to design an algorithm that answers both this queries in \\( O(Log(n)) \\)

Let's go through the examples first 

- input 
```
6 10
3 5 2 6 8 2
ask 1 1
add 1 5
ask 1 3
ask 2 6
add 4 6
ask 2 5
add 2 5
add 2 5
add 5 6
ask 1 6
```
- output 
```
3
16
37
38
70
```

The problem statement is trivial And the naive solution is obvious. For `ask` queries, go through 
the array and calculate the sum. This takes \\( O(n) \\). For `add` queries, traverse the array and perform addition. This will also take \\( O(n) \\). As a result, the naive solution runs in \\( O(n^2) \\) for \\( n \\) queries !!

### segment tree to the rescue 

I won't be explaining what segment trees are. There are already plenty of material out there explaining the concept. 
I recommend reading [cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html) explanation of the subject 

After reading about segment trees and lazy propogation, I recommend that you think about the problem before moving on to the solution. 
Here are some hint 

***- what can be stored in each node every time we are being lazy, such that we can calculate each number that needs to be added to the leaf nodes ?***

***- we are only adding arithmatic sequences !!***

Take the following sequence as an example
$$
1, 0, -4, 9, 2 
$$
Let's say we want to add the following numbers to the sequence
$$ 
3, 4, 5, 6, 7
$$
It's enough to remeber \\( 3 \\) in the parent node, since it's an arithmatic progression with common difference equal to one. Let's add another set of numbers to see how this changes
$$ 
9, 10, 11, 12, 13
$$ 
Now we need to remeber that we want to add \\( 12, 14, 16, 18, 20 \\) to the aforementioned sequence. This is still an arithmatic progression. This time we will be saving the common difference at the parent node as well as the first number. And that's it ! 

This was the final assignment in a course on data structures, when I was beginning the second year of my studies at university. The code is available [here](https://github.com/mehrdad3301/segment-tree). I didn't change it, it's the same thing I handed in two years ago. Back then I had no idea what a segment tree was, and it took me about 1 week to solve this. It was fun going through this after almost two years ! 

