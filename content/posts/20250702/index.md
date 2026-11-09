{
  "title": "My Blog: Automated, Simple & Easy to Maintain",
  "publishDate": "2025-07-02T09:00:00+09:00",
  "draft": false,
  "url": "/20250702/hostMyBlogWithGitHubPages.html",
  "params": {
    "legacy": true
  },
  "description": "Managing articles through linked is quite cumbersome, and even if it's better than posts, I still find them quickly lost in the noise of LinkedIn, not really simple to access for management."
}

## My Blog

Managing articles through linked is quite cumbersome, and even if it's better than posts, I still find them quickly lost in the noise of LinkedIn, not really simple to access for management.

So I have decided to build **my own blog**.

I didn’t wanted a complex solution that I’d have to heavily maintain, therefore I decided to use GitHub Pages to publish my articles.

In order to easily and efficiently publish those articles, I’m using GitHub Actions to build this simple static web page.

The workflow is quite simple yet efficient.

I’m writing my articles in **LibreOffice **writer****, which I save as ODT format.

Once my article is complete, I commit it and push it to my GitHub repository.

This triggers a GitHub Action which converts the ODT files to HTML, then updates *index.html* to add all the articles.

The blog ( Index.html ) is simple rebuilt at each push to my repository.

### Here’s my workflow in detail:

I couldn’t resist creating a Rust tool to enable more automation.

#### **Step 1:**

With my Rust tool, I create the architecture and a template ODT file.

It:

- Initializes a folder with the date of the first Wednesday of the following month.
- Asks for a file name.
- Opens **LibreOffice** with the new ODT file.

https://github.com/Vagrantin/odt-cli-creator

#### **Step 2:**

I’m writing my article in **LibreOffice **Writer.****

#### **Step 3:**

Once I’m happy with the article, saves it as LibreOffice standard format “odt” file, then commit everything and push it to my repository.

#### **Step 4: GitHub Action**

Once pushed to main:

- GitHub Action checks out the repository.
- Downloads and installs **Pandoc**.
- Triggers a script to build the blog.
- Commits and pushes back to publish the rebuilt HTML files.

### The script to build the blog:

- First step: delete all existing HTML files (they are going to be rebuilt afterwards).
- The index HTML main page is then recreated using **Pandoc**, adding all articles one by one by their publication date.
- Each folder is dated with its publication date. I’m just converting the folder’s name into a nicer format for the blog.

Then another GitHub Action is triggered a few minutes later to deploy the repository for **Github Pages**.

That’s it — simple and easy to maintain.

### Next steps:

I will improve the design and the conversion to make the articles easier fun to read. Will probably add some titles along side the date as well. Once I understand how it works link it to a dedicated domain name.

I hope you will enjoy reading them.

My blog is accessible here:

<https://vagrantin.github.io/blog/>

With kind regards,

Matthieu.
