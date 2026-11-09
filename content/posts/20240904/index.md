{
  "title": "Head-to-Head: Rust's Head vs GNU Head",
  "publishDate": "2024-09-04T09:00:00+09:00",
  "draft": false,
  "url": "/20240904/Rust20240904.html",
  "params": {
    "legacy": true
  },
  "description": "Since this training book has been built in TDD ( Test driven development ) way I had to do some back and for between the expected result and what result I had."
}

## My head is done !

I finally made it, a cut down version of GNU head

This was fun, a bit of headache some times…

Since this training book has been built in TDD ( Test driven development ) way I had to do some back and for between the expected result and what result I had.

So this was not at all programming issues but purely achieving what the tests case where expecting.

And for couple of use case I have even changed the test scenario to match my output :D

I know this sounds crazy but I would like to show you the both case where I did so.

Let’s first have a look at a diff between the two tests script, the original one and mine.

![](/20240904/Pictures/100000000000070E000001484212000633DE2178.png)

I have colored all 3 differences for ease of read.

The first one this is purely cosmetic and for my personal convenience I have a different project name and consequently different binary name.

1st Case:

In this case we are testing the program to make sure it reports an error if we use both parameters “-n” and “-c” at the same time which is not supported.

We are using clap v2 branch ( exactly v2.34 ) to build this cli tool.

Also, with clap to manage the incompatibility between two parameters there is a dedicated method for that which is [conflict_with](https://docs.rs/clap/2.34.0/clap/struct.ArgGroup.html#method.conflicts_with).

As far as I know, this method provide it’s dedicated and builtin output, you probably see where I’m going with it.

The output of the clap create that I’m using is not the same as the one expected by the test case.

This is the output expected by the test case:

![](/20240904/Pictures/10000000000002520000011962F86465BAFD1046.png)

This is the output of my program:

![](/20240904/Pictures/100000000000033400000094152FA9FE89D9CF35.png)

So unless, I rewrite clap to change the output behavior in this condition, which was clearly not an option for me, I decided to modify the expected output of the test case to match mine since it is perfectly reasonable and as expected.

2nd Case:

In this case found the expected result a bit weird for me, even more it is expected a totally different behavior than GNU head.

In this test case, the goal is to skip bad files / files that don’t exist and through an error message for those files.

This is the original tests scenario

![](/20240904/Pictures/100000000000025B0000010F5801355EE89FF4A1.png)

This is my version:

![](/20240904/Pictures/100000000000025700000108D1D81EF22687C8D8.png)

Let me show you the different output.

This is the output of my head:

![](/20240904/Pictures/100000000000041100000083915605ABA4D4B1AA.png)

This the output of GNU head:

![](/20240904/Pictures/10000000000004EA000000853C2BB07F379F83E6.png)

This is interesting because we have the same structure and output expect or for the format of the error message.

This is where I found strange that the expected output must be the error message only instead of matching more closely to what is output by GNU head.

Consequently I consider this test to pass as soon as the expected error message is ***contained*** in the output and ***not is the all**** ***output.

## Fixing bugs:

In the previous article I spent some time talking about end line characters and specially the return carrier.

I have manage to fix this issue by refactoring my code.

Effectively in the previous version I was using the [lines()](https://doc.rust-lang.org/stable/std/io/trait.BufRead.html#method.lines) method which is consuming the return carrier or line return when iterating on each lines.

Consequently I have moved to the [read_line()](https://doc.rust-lang.org/stable/std/io/trait.BufRead.html#method.read_line) method which is outputting everything including the return carrier or line return that are in the string.

At the same time, I have discovered the [loop{}](https://doc.rust-lang.org/stable/std/keyword.loop.html) keyword which is very useful to do very simple loop then break out on specified condition.

This what looks like the piece of code now using read_line(), this is a much concise code, I have to appreciate that !

![](/20240904/Pictures/10000000000002FB000000D11462222FF3F5D441.png)

Here is the latest and final version of header on [github](https://github.com/Vagrantin/headers/releases/tag/0.1.1)

https://github.com/Vagrantin/headers/releases/tag/0.1.1
