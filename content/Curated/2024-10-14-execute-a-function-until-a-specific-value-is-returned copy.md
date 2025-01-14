Title: Execute a function until a specific value is returned
Tags: python, tips
Author: Rodrigo Girão Serrão
url: https://mathspp.com/blog/til/making-an-iterator-out-of-a-function

I had barely no idea that the `iter` function could do that in Python. You can call it with two arguments, a function and a stop value, and have your function being executed until the stop value is returned. It can have some interesting usages, as shown in the article. I would not use it all over the place because it looks like a bit dark magic but still a nice tool to keep in mind.
