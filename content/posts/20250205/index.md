{
  "title": "Mastering Ratatui's Canvas: Draw ASCII Art on Terminal UI",
  "publishDate": "2025-02-05T09:00:00+09:00",
  "draft": false,
  "url": "/20250205/Rust20250205.html",
  "params": {
    "legacy": true
  },
  "description": "I’m always looking for solutions to improve my personal workflow, on top of that, really dislike blotted operating system and Microsoft is more and more a blotted operating system."
}

## Let’s do a bit of Cuisine with Ratatui.rs

I’m always looking for solutions to improve my personal workflow, on top of that, really dislike blotted operating system and Microsoft is more and more a blotted operating system.

We are forced to upgrade hardware an very regular basis even if PCs are becoming more and more realible.

My current laptop is 7 years old, and when runing Windows 10, I could feel it suffering, hearing the fans at 100% all the time. Seeing tons of processes eating the RAM and the CPU.

Once I move to PopOS with i3 windows Manager this has been a new life for my laptop.

It is blazzing fast !

The perspective of migrating to Windows 11 is very painfull to me, with all those AI engine force to you on the machine will add even more hardware requirements to be able to continue be supported by Microsoft even with security patches ( Windows 10 support is finished on October 2025 ).

Don’t get me wrong, I see AI engines as tools and I still plan to use AI tools as you will see in this article. But I would like to choose when to use it and control what data I’m sending over.

With built in AI engines in the OS, I’m very concern of the privacy for me and my company.

I’m sure we will pay the price at some point, and this will be very expensive.

To finish on this at some point I will probably setup my own local LLM using open source solution.

Recently DeepSeek R1 is a good contenter and has reshuffled the card on the AI landscape !

Ratutui.rs

For those would don’t know Ratatui.rs (<https://ratatui.rs/>), I would like to do a short introduction about it.

This is a Rust Library for creating Terminal User Interfaces (TUIs). It has an API to build terminal based application, it supports realtime updates, user interaction and it supports Linux, macOS, Windows.

With Ratatui you build your app using widgets ( tables, charts, list, paragraphes, gauges), you have also blocks and borders to organize your layout and then style it. What we will be using today is canvas to build custom drawing on your terminal. As said above it support user interaction with the mouse or keyboard to have an interactive UI.

Let’s get to the cooking.

As usual, since the beginning of this series of article, I have been using a generative AI to build the original version then I have fixed it.

I used claude.ai for this exercise.

The goal of this exercises was to get more familiar with Ratatui and the possiblities of this library as well as continue to use Rust for the programing language.

I wanted to draw in kind of “ASCII” style the text “HAPPY NEW YEAR 2025!” on the screen leveraging this library.

As usual the first proposition was not at all what I have expected.

So, after correcting the requested it gave me somewhat what I was expecting but

all letters where flipped and some words where missing!

I could probably asked the generative AI to fix it but this is where I took back the control and fix it so I can have an understanding on the way the library works and then improve it because it was messing some words, looks like generative AI are getting lazy…

And with this I end up with almost what I wanted, need to investigate more how I can improve the styling but overall I’m pretty happy of the result and this gives way too much ideas of what can be done with this library.
