---
name: viral-article-writer
description: "Write, edit, and optimize viral, SEO/AEO-optimized, humanized articles formatted in Obsidian Flavored Markdown. Combines customer research (Voice of Customer), marketing psychology, copywriting, AI SEO (GEO/AEO), copy-editing, and Obsidian syntax (frontmatter, wikilinks, callouts, tags)."
---

# Viral Obsidian Article Writer

This skill defines the complete 5-step pipeline for writing, optimizing, humanizing, and formatting high-ranking, highly shareable articles in **Obsidian Flavored Markdown** for the `content/` vault.

---

## The 5-Phase Workflow

```
1. VOC Research  ──>  2. Viral Draft  ──>  3. AI SEO (GEO)  ──>  4. Obsidian Markdown  ──>  5. Humanizing Sweep
   (Real language)      (Hooks & Psych)      (LLM Citations)      (Wikilinks/Callouts)     (De-robotify)
```

---

### Phase 1: Research & Voice of Customer (VOC)

*Reference: [customer-research skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/customer-research/SKILL.md)*

- **Extract Real Phrasing**: Identify exact words, frustrations, and questions real people use in Reddit threads, forum discussions, G2/Capterra reviews, and customer calls.
- **Identify Core Pain & Desire**: What is the reader secretly afraid of? What exact outcome do they want to achieve immediately?
- **Avoid Corporate Speak**: Replace technical jargon with real reader vocabulary.

---

### Phase 2: Psychological Framing & Copywriting

*References: [marketing-psychology skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/marketing-psychology/SKILL.md) & [copywriting skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/copywriting/SKILL.md)*

- **Scroll-Stopping Hook (First 3 Lines)**: Use a pattern interrupt, curiosity gap, or surprising statistic. Avoid slow intros ("In today's fast-paced world...").
- **Leverage Core Psychology**:
  - **Zeigarnik Effect**: Open loops early in the article that get resolved in later sections.
  - **Mimetic Desire / Social Proof**: Show what top industry leaders or peers are doing.
  - **Loss Aversion**: Highlight what the reader risks losing by ignoring the advice.
- **Formatting for Skimmers**: Bold key concepts, keep paragraphs to 1-3 sentences, and use descriptive `##` and `###` subheadings.

---

### Phase 3: AI SEO (GEO) & Search Engine Optimization

*References: [ai-seo skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/ai-seo/SKILL.md) & [seo-audit skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/seo-audit/SKILL.md)*

- **40–60 Word Extractable Answer Blocks**: Place a concise, standalone definition/summary block right after main section headings so Google AI Overviews, ChatGPT, and Perplexity can easily extract and cite it.
- **Statistical & Citation Boost (+40%)**: Include specific data, dates, numbers, and author attributions. Original research and specific metrics earn 40%+ more LLM citations.
- **Query Fan-Out Coverage**: Cover 3–5 logical sub-questions the reader (or AI engine) will ask next.
- **Structured FAQ Section**: Add a dedicated Q&A section near the end with direct answers.

---

### Phase 4: Obsidian Flavored Markdown Formatting

*References: [obsidian-markdown skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/obsidian-skills/skills/obsidian-markdown/SKILL.md) & [content AGENTS.md](file:///c:/Users/super/Desktop/obsidian/content/.agents/AGENTS.md)*

1. **Standard Frontmatter (YAML Properties)**:
   ```yaml
   ---
   title: "Compelling Article Title"
   description: "A punchy 150-160 character meta description summarizing the key benefit."
   tags:
     - article
     - seo
     - marketing
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   author: Mohamad Masri
   layout: post
   status: published
   aliases:
     - "Alternative Title or Keyword"
   ---
   ```
2. **Internal Wikilinks**: Connect to existing vault notes using `[[Note Name]]` or `[[Note Name|Display Text]]`. Link to relevant Maps of Content (`[[MOC]]`) where appropriate.
3. **Obsidian Callouts**: Highlight key insights with Obsidian callout boxes:
   ```markdown
   > [!tip] Pro Tip
   > Standalone takeaway for the reader.

   > [!important] Key Warning
   > Crucial mistake to avoid.

   > [!faq] Frequently Asked Question
   > Direct 40-60 word answer for snippet extraction.
   ```
4. **Highlights & Footnotes**: Use `==highlight key text==` and footnotes `[^1]` for citations.

---

### Phase 5: Humanizing Sweep & De-robotifying

*Reference: [copy-editing skill](file:///c:/Users/super/Desktop/obsidian/.agents/skills/copy-editing/SKILL.md)*

- **Eliminate AI Clichés**: Scan and remove robotic filler words and clichés:
  - ❌ *In conclusion*, *Delve into*, *Furthermore*, *In the rapidly evolving landscape*, *Testament to*, *It is crucial to note*, *Beacon of hope*.
- **Vary Sentence Rhythm**: Alternate between short 3-word punchy sentences and longer, explanatory sentences.
- **Conversational Tone**: Write like you are advising a smart colleague over coffee.

---

## Article Creation Checklist

- [ ] Frontmatter complete with `title`, `description`, `tags`, `created`, `updated`, `author`, `layout`, and `status`.
- [ ] First paragraph contains a high-converting hook and opening loop.
- [ ] Main sections feature 40-60 word extractable answer blocks for LLM/AI SEO citations.
- [ ] Verified at least 2 statistics or authoritative quotes are cited.
- [ ] Internal vault connections established via `[[Wikilinks]]`.
- [ ] Obsidian callouts (`> [!tip]`, `> [!important]`, `> [!faq]`) used to emphasize key points.
- [ ] De-robotifying sweep completed (zero AI clichés).
