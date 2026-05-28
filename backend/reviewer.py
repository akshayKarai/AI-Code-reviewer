"""
Code Reviewer Engine
Uses Claude AI to analyse code and return structured feedback.
"""

import os
import json
import re
import anthropic


class CodeReviewer:

    model = "claude-sonnet-4-20250514"

    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", "c", "c++", "c#",
        "go", "rust", "ruby", "php", "swift", "kotlin", "sql", "bash",
        "html", "css", "react", "vue", "auto"
    ]

    SEVERITY_EMOJI = {
        "critical": "🔴",
        "major": "🟠",
        "minor": "🟡",
        "suggestion": "🔵",
    }

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # ── Public API ─────────────────────────────────────────────────────────────

    def review(self, code: str, language: str, focus: list[str], severity_filter: str) -> dict:
        """Full code review — returns structured JSON parsed into a dict."""
        prompt = self._build_review_prompt(code, language, focus)
        raw = self._call_claude(prompt, max_tokens=2048)
        parsed = self._parse_json_response(raw)
        result = self._normalise_review(parsed, code)

        if severity_filter != "all":
            order = ["critical", "major", "minor", "suggestion"]
            cutoff = order.index(severity_filter) + 1
            result["issues"] = [
                i for i in result["issues"]
                if order.index(i.get("severity", "suggestion")) < cutoff
            ]

        return result

    def explain(self, code: str, language: str) -> dict:
        """Plain-English explanation of what the code does."""
        prompt = self._build_explain_prompt(code, language)
        explanation = self._call_claude(prompt, max_tokens=800)
        detected_lang = self._detect_language_from_code(code) if language == "auto" else language
        return {"explanation": explanation.strip(), "language": detected_lang}

    # ── Prompt builders ────────────────────────────────────────────────────────

    def _build_review_prompt(self, code: str, language: str, focus: list[str]) -> str:
        focus_str = ", ".join(focus)
        lang_hint = "" if language == "auto" else f"The language is {language}."

        return f"""You are an expert code reviewer. Analyse the code below and return ONLY a valid JSON object — no markdown, no explanation outside the JSON.

{lang_hint}
Focus areas: {focus_str}

Return this exact JSON structure:
{{
  "language": "<detected or specified language>",
  "overall_score": <integer 0-100>,
  "summary": "<2-3 sentence executive summary>",
  "issues": [
    {{
      "severity": "<critical|major|minor|suggestion>",
      "category": "<bug|security|performance|style|best_practice>",
      "line": "<line number or range, e.g. '12' or '10-15', or null>",
      "title": "<short title>",
      "description": "<what the problem is>",
      "suggestion": "<how to fix it>"
    }}
  ],
  "positive_aspects": ["<thing done well>", ...],
  "refactored_snippet": "<optional improved version of the most problematic section, or null>"
}}

Scoring guide:
- 90-100: Excellent, production-ready
- 70-89: Good with minor issues
- 50-69: Needs work, several issues
- 30-49: Significant problems
- 0-29: Critical issues, major rework needed

CODE TO REVIEW:
```
{code}
```"""

    def _build_explain_prompt(self, code: str, language: str) -> str:
        lang_hint = "" if language == "auto" else f"Language: {language}."
        return f"""Explain the following code in clear, plain English suitable for a developer who didn't write it. {lang_hint}

Cover:
1. What it does overall (1-2 sentences)
2. How it works step by step
3. Any important edge cases or assumptions

Be concise and practical. Do NOT include a JSON response — just write the explanation directly.

CODE:
```
{code}
```"""

    # ── Claude call ────────────────────────────────────────────────────────────

    def _call_claude(self, prompt: str, max_tokens: int = 1500) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _parse_json_response(self, raw: str) -> dict:
        """Extract and parse JSON from Claude's response."""
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try to find the JSON object inside the string
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse JSON from Claude response:\n{raw[:500]}")

    def _normalise_review(self, data: dict, code: str) -> dict:
        """Ensure all required fields exist with safe defaults."""
        issues = []
        for issue in data.get("issues", []):
            issues.append({
                "severity": issue.get("severity", "minor"),
                "category": issue.get("category", "style"),
                "line": str(issue.get("line", "")) if issue.get("line") else None,
                "title": issue.get("title", "Issue"),
                "description": issue.get("description", ""),
                "suggestion": issue.get("suggestion", ""),
            })

        line_count = code.count("\n") + 1
        char_count = len(code)
        critical = sum(1 for i in issues if i["severity"] == "critical")
        major = sum(1 for i in issues if i["severity"] == "major")

        return {
            "language": data.get("language", "unknown"),
            "overall_score": max(0, min(100, int(data.get("overall_score", 50)))),
            "summary": data.get("summary", "Review completed."),
            "issues": issues,
            "positive_aspects": data.get("positive_aspects", []),
            "refactored_snippet": data.get("refactored_snippet"),
            "stats": {
                "total_issues": len(issues),
                "critical": critical,
                "major": major,
                "minor": sum(1 for i in issues if i["severity"] == "minor"),
                "suggestions": sum(1 for i in issues if i["severity"] == "suggestion"),
                "lines_of_code": line_count,
                "characters": char_count,
            },
        }

    def _detect_language_from_code(self, code: str) -> str:
        """Rough heuristic language detection as fallback."""
        if "def " in code and "import " in code:
            return "python"
        if "function " in code or "const " in code or "let " in code:
            return "javascript"
        if "public class " in code or "System.out" in code:
            return "java"
        if "#include" in code:
            return "c++"
        if "func " in code and ":=" in code:
            return "go"
        return "unknown"
