---
context: fork
agent: plot-generator
allowed-tools: Read, Write, Bash
argument-hint: "<chart description or data>"
---

# generate-plot

Generate a matplotlib chart/visualization from a natural-language description.

## Workflow

1. Parse the user's chart description from `$ARGUMENTS`
2. Determine the appropriate chart type (bar, line, pie, scatter, etc.)
3. Write a Python script using matplotlib to generate the chart
4. Execute the script to produce the output file (PNG by default)
5. Report the output file path to the user

## Chart Type Selection

- **Bar chart**: Comparing discrete categories or items
- **Horizontal bar**: Comparing categories with long labels
- **Stacked bar**: Showing composition across categories
- **Grouped bar**: Comparing multiple series across categories
- **Line chart**: Showing trends over time or continuous data
- **Pie/Donut chart**: Showing proportions of a whole (use sparingly, max 7 segments)
- **Scatter plot**: Showing correlation between two variables
- **Area chart**: Emphasizing volume/magnitude over time
- **Heatmap**: Showing patterns in matrix data

## Script Template

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Azure color palette
AZURE_COLORS = [
    "#0078D4",  # Azure Blue (primary)
    "#50E6FF",  # Light Blue
    "#F25022",  # Red
    "#7FBA00",  # Green
    "#FFB900",  # Yellow
    "#737373",  # Gray
    "#B4009E",  # Purple
    "#00B7C3",  # Teal
    "#D83B01",  # Dark Orange
    "#005B70",  # Dark Teal
]

# Professional styling
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 11,
    "figure.dpi": 150,
})

fig, ax = plt.subplots(figsize=(10, 6))

# ... chart-specific code ...

plt.tight_layout()
plt.savefig("output.png", bbox_inches="tight", dpi=150)
print("Chart saved to output.png")
```

## Style Guidelines

- Always use `matplotlib.use("Agg")` before importing pyplot (no display needed)
- Use the Azure color palette defined above
- Remove top and right spines for a cleaner look
- Add subtle grid lines (alpha=0.3) on the value axis
- Use `tight_layout()` and `bbox_inches="tight"` when saving
- Default figure size: 10x6 inches at 150 DPI
- Add clear title, axis labels, and legend where appropriate
- For pie charts, use a donut style (wedgeprops with width=0.6) and add percentage labels
- Rotate x-axis labels if they overlap
- Use commas in large numbers via `ticker.FuncFormatter`

## Output

- Default format: PNG at 150 DPI
- If the user requests SVG, use `plt.savefig("output.svg", format="svg")`
- Use a descriptive filename based on the chart content (e.g., `azure-cost-comparison.png`)
- Always print the output path after saving

## Data Handling

- If the user provides explicit data, use it directly
- If the user describes a concept without data, generate realistic sample/placeholder data and clearly label it as illustrative
- For Azure cost data, use realistic price ranges from public Azure pricing
- Parse inline data formats: CSV snippets, JSON, markdown tables, or plain lists
