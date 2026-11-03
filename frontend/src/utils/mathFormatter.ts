/**
 * Normalizes mathematical formulas and LaTeX delimiters so that remark-math
 * and rehype-katex can consistently render them.
 *
 * Handles:
 * - Dollar notation: $inline$ and $$display$$
 * - Slash/bracket notation: \[display\] and \(inline\)
 * - Escaped slash/bracket notation: \\[display\\] and \\(inline\\)
 * - Forward slash/bracket notation: /[display/] and /(inline/)
 * - Ensures each display math equation is enclosed in clean $$...$$ blocks
 *   with proper surrounding paragraphs and no interior empty lines.
 */
export function formatMathContent(content: string): string {
  if (!content) return '';

  let formatted = content;

  // 1. Bracket display math: \[ ... \] or \\[ ... \\] or /[ ... /]
  formatted = formatted.replace(/(?:\\\\|\\|\/\/|\/)\[([\s\S]*?)(?:\\\\|\\|\/\/|\/)\]/g, (_, math) => {
    const clean = math.trim();
    return clean ? `\n\n$$\n${clean}\n$$\n\n` : '';
  });

  // 2. Inline brackets: \( ... \) or \\( ... \\) or /( ... /)
  formatted = formatted.replace(/(?:\\\\|\\|\/\/|\/)\(([\s\S]*?)(?:\\\\|\\|\/\/|\/)\)/g, (_, math) => {
    const clean = math.trim();
    return clean ? ` $${clean}$ ` : '';
  });

  // 3. Single-dollar block math on isolated lines: $\n ... \n$ -> $$ ... $$
  formatted = formatted.replace(/(^|\n)\s*\$\s*\n+([\s\S]*?)\n+\s*\$\s*($|\n)/g, (_, before, math, after) => {
    const clean = math.trim();
    return clean ? `${before}\n\n$$\n${clean}\n$$\n\n${after}` : '';
  });

  // 4. Normalize all display math $$...$$ to ensure clean block separation
  formatted = formatted.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    const clean = math.trim();
    return clean ? `\n\n$$\n${clean}\n$$\n\n` : '';
  });

  // 5. Collapse excessive empty newlines (3+ -> 2)
  formatted = formatted.replace(/\n{3,}/g, '\n\n');

  return formatted;
}
