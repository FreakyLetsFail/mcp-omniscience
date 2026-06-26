# 🤖 Prompt Library for Omniscience

Omniscience provides your AI Assistant (Claude, Cursor, Antigravity) with surgical tools to navigate your codebase. However, sometimes the AI needs a little "nudge" to know *how* to use these tools effectively.

Here are battle-tested prompts you can copy & paste to your AI to get the most out of Omniscience.

---

## 🧹 1. The "Fearless Refactor & Cleanup"
Normally, AIs are terrified of deleting code because they don't know if a function is used elsewhere. With Omniscience's `graph_query`, you give them the mathematical certainty to delete dead code safely.

**Copy & Paste:**
> "Your goal is to thoroughly clean up this repository. We want to remove dead code, unused components, and structural chaos to create a clean base for new features.
> 
> **Instructions (Use the Omniscience MCP Server):**
> 1. Use your standard file listing tools to get an overview of the directory structure.
> 2. When you find files, components, or helper functions that seem unused or obsolete, **you MUST use the `graph_query` tool** from the Omniscience server.
> 3. If the Call-Graph confirms that a function has 0 callers (and it's not an obvious entry point like a UI Route/Page), consider it dead code.
> 4. Use your file editing tools (or `apply_surgical_patch`) to remove this dead code, unused imports, or entire files safely.
> 5. Work iteratively folder by folder until the project is significantly cleaned up."

---

## 🕵️ 2. The "Surgical Bug Hunt"
When you have a specific bug but no idea where the code is located in a massive repository.

**Copy & Paste:**
> "I have a bug related to how user passwords are hashed before saving. 
> 1. Use the `semantic_search` tool from Omniscience to find the core function responsible for password hashing (try queries like 'hash password' or 'save user').
> 2. Once you find the correct symbol ID in the results, use the `surgical_read` tool to extract ONLY that specific function, without reading the entire file.
> 3. Explain to me what the algorithm is doing wrong, and use `apply_surgical_patch` to fix it."

---

## 🕸️ 3. The "Blast Radius Analysis"
Before changing a core utility function, you want the AI to understand the consequences of the change.

**Copy & Paste:**
> "I want to change the signature of the `calculateTax()` function to include a new `discount` parameter.
> 
> Before making any changes, use the `graph_query` tool to find the exact 'blast radius' of `calculateTax`. 
> List all functions and files that currently call it. Then, systematically go through each dependent function using `surgical_read`, and update their calls to accommodate the new parameter."

---

## 🚀 Tips for the User
- **Always remind the AI to use `surgical_read`:** LLMs tend to fall back to reading entire files (`cat` or `read_file`). Remind them that `surgical_read` is much faster and saves massive amounts of context window tokens.
- **Enforce the Graph:** If your AI hesitates to change an architecture, explicitly tell it: *"Trust the `graph_query` tool. It uses a concrete AST parsed graph, no hallucinations."*
