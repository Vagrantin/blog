{
  "title": "Vibe Coding in Rust: A Reality Check",
  "publishDate": "2025-04-02T09:00:00+09:00",
  "draft": false,
  "url": "/20250402/Rust20250402.html",
  "params": {
    "legacy": true
  },
  "description": "In February 2025, ex-OpenAI co-founder Andrej Karpathy coined the term \"vibe coding\" - a seemingly utopian approach where developers \"fully give in to the vibes, embrace exponentials, and forget that the…"
}

## The Reality of "Vibe Coding": A Rust non-Developer's journey

### Introduction to the Phenomenon

In February 2025, ex-OpenAI co-founder Andrej Karpathy coined the term "vibe coding" - a seemingly utopian approach where developers "fully give in to the vibes, embrace exponentials, and forget that the code even exists." This methodology has sparked controversy in developer circles, being criticized as "programming without programming knowledge." As a Rust enthusiast, I decided to put this approach to the test.

### The Promise vs. The Reality

#### The Promise:

*claude.ai → Magic → Working Tool → Productivity Nirvana*

#### The Reality:

*fn actual_vibe_coding() -\> Result\<Tool, VibingError\> {*

* loop {*

* let prompt = craft_extremely_precise_prompt()?;*

* let generated_code = claude_ai.generate(prompt)?;*

* *

* // Required step that vibe coding evangelists never mention*

* if !human_actually_reads_code(&generated_code) {*

* return Err(VibingError::UnreviewedCodeDisaster);*

* }*

* *

* match fix_inevitable_mistakes(&generated_code) {*

* Ok(fixed_code) =\> {*

* if test_on_sample_data(&fixed_code).is_ok() {*

* return Ok(fixed_code);*

* }*

* },*

* Err(\_) =\> continue, // Back to square one*

* }*

* }*

*}*

### The 8-Step "Vibe Coding" Protocol

1.  **Prompt Engineering**: Craft a request with the precision of a neurosurgeon (I recommend using Rust – see in step 4).
2.  **Code Review**: Actually read the generated code. Yes, shocking, I know.
3.  **Enter Panic Mode**: Yes, you will be shocked, the 'AI' has written spaghetti code.
4.  **Error Correction**: Fix all stupid mistake, as the AI tool doesn’t have any understanding what it through at you, this is where Rust is very nice becaues Rust compiler will help you a lot in memory related issues, for the rest you are on your own :D.
5.  **Testing**: Apply the shocking concept of validating functionality on sample data.
6.  **Troubleshooting**: When (not if) it fails, return to step 1 with increasingly precise prompts if you can’t/don’t want to fix it yourself. This should be done at the very precise point where you have identified the issue.
7.  **Perseverance**: Loop from step 1 to 6 until you are happy with the result.
8.  **Production Caution**: Never deploy to production unless you understand every line of code - a principle that apparently needs stating in the age of "vibe coding."

### My Personal Use Case

I've limited my "vibe coding" adventures to creating small utility tools that enhance my daily workflow. This approach works for me because:

1.  I practice what I call "Vibe QA" - a methodology built on having crystal-clear requirements
2.  My tools are small enough to be reviewed before implementation
3.  I maintain a healthy skepticism about the generated code's quality

### Tools Created This Month

[*https://github.com/Vagrantin/findinfiles*](https://github.com/Vagrantin/findinfiles)

*A Rust utility that searches files for specific terms and automatically copies matching files to a designated directory.*

[*https://github.com/Vagrantin/grabpdf*](https://github.com/Vagrantin/grabpdf)*\

A Rust tool to download all PDFs from a website url.*

[*https://github.com/Vagrantin/file_merger_tool*](https://github.com/Vagrantin/file_merger_tool)

*A Rust-based command-line tool for merging or processing two input files and saving the output*

[*https://github.com/Vagrantin/stripehtmltags*](https://github.com/Vagrantin/stripehtmltags)

*A Rust-based command-line utility that strips HTML tags from files, outputting only the clean text content with one item per line.*

[*https://github.com/Vagrantin/recursefilecreator*](https://github.com/Vagrantin/recursefilecreator)

*\
A Rust tool that recursively creates files in all directories within a given path.*

[*https://github.com/Vagrantin/buildstatus*](https://github.com/Vagrantin/buildstatus)

*A Rust CLI tool that parses XML files from a directory and exports structured data to a CSV file.*

### Conclusion

While "vibe coding" might not revolutionize software development as its proponents suggest, it can serve as a productivity multiplier for small, well-defined tasks when combined with proper review processes and a solid understanding of programming fundamentals. Just remember - the "vibe" in "vibe coding" should stand for "Verify, Inspect, Bug-hunt, and Evaluate."

PS: Article re-written by claude.ai from my original though, then I fixed it to look the way I wanted.
