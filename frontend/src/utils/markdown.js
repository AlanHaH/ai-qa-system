import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import 'highlight.js/styles/github.css'

// markdown-it 配置（聊天场景：换行转 <br>、自动链接、不渲染原始 HTML 防 XSS）
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
          hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
          '</code></pre>'
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  }
})

// 规范化 AI 输出中不规范的 markdown（标记后无空格，如 ###🏆、-常规）
function normalizeMarkdown(text) {
  return text
    // 标题：# 后无空格（###🏆 → ### 🏆）
    .replace(/^(#{1,6})(?=[^\s#])/gm, '$1 ')
    // 无序列表：- * + 后无空格，且不是分隔线/加粗/斜体标记（-常规 → - 常规）
    .replace(/^([-*+])(?=[^-\*+\s])/gm, '$1 ')
    // 有序列表：1. 后无空格（1.第一 → 1. 第一）
    .replace(/^(\d+)\.(?=\S)/gm, '$1. ')
}

// markdown → 经过 DOMPurify 清洗的安全 HTML
export function renderMarkdown(text) {
  if (!text) return ''
  const html = md.render(normalizeMarkdown(text))
  return DOMPurify.sanitize(html)
}
