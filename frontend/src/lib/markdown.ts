import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import 'katex/dist/contrib/mhchem.mjs';

// Configure KaTeX extension
marked.use({
  extensions: [
    {
      name: 'blockMath',
      level: 'block',
      tokenizer(src) {
        // $$...$$
        const rule1 = /^\$\$([\s\S]*?)\$\$/;
        const match1 = rule1.exec(src);
        if (match1) {
          return {
            type: 'blockMath',
            raw: match1[0],
            text: match1[1].trim()
          };
        }
        // \[...\]
        const rule2 = /^\\\[([\s\S]*?)\\\]/;
        const match2 = rule2.exec(src);
        if (match2) {
          return {
            type: 'blockMath',
            raw: match2[0],
            text: match2[1].trim()
          };
        }
      },
      renderer(token) {
        try {
            return `<div class="katex-block my-4 overflow-x-auto">${katex.renderToString(token.text, { displayMode: true, throwOnError: false })}</div>`;
        } catch (e) {
            return token.raw;
        }
      }
    },
    {
      name: 'displayMath',
      level: 'inline',
      start(src) { return src.indexOf('$$'); },
      tokenizer(src) {
        const rule = /^\$\$([\s\S]*?)\$\$/;
        const match = rule.exec(src);
        if (match) {
          return {
            type: 'displayMath',
            raw: match[0],
            text: match[1].trim()
          };
        }
      },
      renderer(token) {
        try {
            return katex.renderToString(token.text, { displayMode: true, throwOnError: false });
        } catch (e) {
            return token.raw;
        }
      }
    },
    {
      name: 'inlineMath',
      level: 'inline',
      start(src) {
        const index1 = src.indexOf('$');
        const index2 = src.indexOf('\\(');
        if (index1 === -1 && index2 === -1) return -1;
        if (index1 === -1) return index2;
        if (index2 === -1) return index1;
        return Math.min(index1, index2);
      },
      tokenizer(src) {
        // $...$
        const rule1 = /^\$([^\$\n]+?)\$/;
        const match1 = rule1.exec(src);
        if (match1) {
          return {
            type: 'inlineMath',
            raw: match1[0],
            text: match1[1].trim()
          };
        }
        // \(...\)
        const rule2 = /^\\\(([\s\S]+?)\\\)/;
        const match2 = rule2.exec(src);
        if (match2) {
          return {
            type: 'inlineMath',
            raw: match2[0],
            text: match2[1].trim()
          };
        }
      },
      renderer(token) {
        try {
            return katex.renderToString(token.text, { displayMode: false, throwOnError: false });
        } catch (e) {
            return token.raw;
        }
      }
    }
  ]
});

export { marked };
