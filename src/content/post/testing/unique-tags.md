---
title: "Unique tags validation"
publishDate: "30 January 2000"
description: "This post is used for validating if duplicate tags are removed, regardless of the string case"
tags: ["food", "Food", "FOOD", "fooD"]
draft: true
---

## This post is to test zod transform

If you open the file `src/content/post/unique-tags.md`, the tags array has a number of duplicate blog strings of various cases.

These are removed as part of the removeDupsAndLowercase function found in `src/content/config.ts`.
