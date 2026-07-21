"""
Export module — CSV

Public interface:
    generate_csv(results: list) -> str
"""

import csv
import io


def generate_csv(results: list) -> str:
    """
    Generate a CSV string from all search results.
    Shortlisted results (final_rank set) come first, then unranked.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Rank", "Name / Title", "URL", "Relevance Score", "Reasoning"])

    shortlist = sorted([r for r in results if r.final_rank is not None], key=lambda r: r.final_rank)
    other = [r for r in results if r.final_rank is None]

    for result in shortlist:
        writer.writerow([result.final_rank, result.title or "", result.url, result.relevance_score, result.relevance_reasoning or ""])

    if other:
        writer.writerow(["--- Other Results (not in shortlist) ---", "", "", "", ""])
        for result in other:
            writer.writerow(["", result.title or "", result.url, result.relevance_score, result.relevance_reasoning or ""])

    return buffer.getvalue()
