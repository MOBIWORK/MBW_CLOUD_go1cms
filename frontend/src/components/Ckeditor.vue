<template>
  <div>
    <ckeditor
      :editor="editor"
      v-model="data"
      :config="editorConfig"
      @ready="onEditorReady"
    ></ckeditor>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { ClassicEditor } from '@ckeditor/ckeditor5-editor-classic'
import {
  Bold,
  Code,
  Italic,
  Strikethrough,
  Subscript,
  Superscript,
  Underline,
} from '@ckeditor/ckeditor5-basic-styles'
import { Paragraph } from '@ckeditor/ckeditor5-paragraph'
import { Essentials } from '@ckeditor/ckeditor5-essentials'
import { Heading } from '@ckeditor/ckeditor5-heading'
import {
  Table,
  TableCaption,
  TableCellProperties,
  TableColumnResize,
  TableProperties,
  TableToolbar,
} from '@ckeditor/ckeditor5-table'
import {
  AutoImage,
  Image,
  ImageCaption,
  ImageInsert,
  ImageResize,
  ImageStyle,
  ImageToolbar,
  ImageUpload,
  PictureEditing,
} from '@ckeditor/ckeditor5-image'
import { SourceEditing } from '@ckeditor/ckeditor5-source-editing'
import { BlockQuote } from '@ckeditor/ckeditor5-block-quote'
import { AutoLink, Link, LinkImage } from '@ckeditor/ckeditor5-link'
import { CodeBlock } from '@ckeditor/ckeditor5-code-block'
import { RemoveFormat } from '@ckeditor/ckeditor5-remove-format'
import { HorizontalLine } from '@ckeditor/ckeditor5-horizontal-line'
import {
  SpecialCharacters,
  SpecialCharactersEssentials,
} from '@ckeditor/ckeditor5-special-characters'
import { CKBox, CKBoxImageEdit } from '@ckeditor/ckeditor5-ckbox'
import { CloudServices } from '@ckeditor/ckeditor5-cloud-services'
import { Font } from '@ckeditor/ckeditor5-font'
import { Highlight } from '@ckeditor/ckeditor5-highlight'
import { Alignment } from '@ckeditor/ckeditor5-alignment'
import { HtmlEmbed } from '@ckeditor/ckeditor5-html-embed'
import { TextTransformation } from '@ckeditor/ckeditor5-typing'
import { List, ListProperties, TodoList } from '@ckeditor/ckeditor5-list'
import { Indent, IndentBlock } from '@ckeditor/ckeditor5-indent'
import { MediaEmbed } from '@ckeditor/ckeditor5-media-embed'
import { Base64UploadAdapter } from '@ckeditor/ckeditor5-upload'
import '@ckeditor/ckeditor5-build-classic/build/translations/vi'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Nhập nội dung ở đây...',
  },
  modeConfig: {
    type: String,
    default: 'full',
  },
})

const data = defineModel()

const editor = ClassicEditor

var editorConfig = {
  plugins: [
    Base64UploadAdapter,
    MediaEmbed,
    Indent,
    IndentBlock,
    List,
    ListProperties,
    TodoList,
    TextTransformation,
    HtmlEmbed,
    Essentials,
    Bold,
    Code,
    Italic,
    Strikethrough,
    Subscript,
    Superscript,
    Underline,
    AutoLink,
    Link,
    LinkImage,
    Paragraph,
    Heading,
    Table,
    TableCaption,
    TableCellProperties,
    TableColumnResize,
    TableProperties,
    TableToolbar,
    SourceEditing,
    BlockQuote,
    AutoImage,
    Image,
    ImageCaption,
    ImageInsert,
    ImageResize,
    ImageStyle,
    ImageToolbar,
    ImageUpload,
    PictureEditing,
    CodeBlock,
    RemoveFormat,
    HorizontalLine,
    SpecialCharacters,
    SpecialCharactersEssentials,
    CKBox,
    CKBoxImageEdit,
    CloudServices,
    Font,
    Highlight,
    Alignment,
  ],
  toolbar: {
    items: [
      'undo',
      'redo',
      '|',
      'heading',
      '|',
      'fontSize',
      'fontFamily',
      'fontColor',
      'fontBackgroundColor',
      '|',
      'bold',
      'italic',
      'underline',
      {
        label: 'Formatting',
        icon: 'text',
        items: [
          'strikethrough',
          'subscript',
          'superscript',
          'code',
          'horizontalLine',
          '|',
          'removeFormat',
        ],
      },
      'specialCharacters',
      '|',
      'link',
      'insertImage',
      'insertTable',
      'highlight',
      'blockQuote',
      'mediaEmbed',
      'codeBlock',
      'htmlEmbed',
      '|',
      'alignment',
      '|',
      'bulletedList',
      'numberedList',
      'todoList',
      'outdent',
      'indent',
      '|',
      'sourceEditing',
    ],
    shouldNotGroupWhenFull: true,
  },
  fontFamily: {
    supportAllValues: true,
  },
  fontSize: {
    options: ['default', 10, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 32],
    supportAllValues: true,
  },
  image: {
    styles: ['alignCenter', 'alignLeft', 'alignRight'],
    resizeOptions: [
      {
        name: 'resizeImage:original',
        label: 'Original',
        value: null,
      },
      {
        name: 'resizeImage:50',
        label: '50%',
        value: '50',
      },
      {
        name: 'resizeImage:75',
        label: '75%',
        value: '75',
      },
    ],
    toolbar: [
      'imageTextAlternative',
      'toggleImageCaption',
      '|',
      'imageStyle:inline',
      'imageStyle:wrapText',
      'imageStyle:breakText',
      '|',
      'resizeImage',
      '|',
      'ckboxImageEdit',
    ],
  },
  list: {
    properties: {
      styles: true,
      startIndex: true,
      reversed: true,
    },
  },
  link: {
    decorators: {
      addTargetToExternalLinks: true,
      defaultProtocol: 'https://',
      toggleDownloadable: {
        mode: 'manual',
        label: 'Downloadable',
        attributes: {
          download: 'file',
        },
      },
    },
  },
  table: {
    contentToolbar: [
      'tableColumn',
      'tableRow',
      'mergeTableCells',
      'tableProperties',
      'tableCellProperties',
      'toggleTableCaption',
    ],
  },
  placeholder: props.placeholder,
  language: 'vi',
}

if (props.modeConfig == 'textarea') {
  editorConfig = {
    plugins: [
      Base64UploadAdapter,
      MediaEmbed,
      Indent,
      IndentBlock,
      List,
      ListProperties,
      TodoList,
      TextTransformation,
      HtmlEmbed,
      Essentials,
      Bold,
      Code,
      Italic,
      Strikethrough,
      Subscript,
      Superscript,
      Underline,
      AutoLink,
      Link,
      Paragraph,
      Heading,
      SourceEditing,
      BlockQuote,
      PictureEditing,
      CodeBlock,
      RemoveFormat,
      HorizontalLine,
      SpecialCharacters,
      SpecialCharactersEssentials,
      CloudServices,
      Font,
      Highlight,
      Alignment,
    ],
    toolbar: {
      items: [
        'undo',
        'redo',
        '|',
        'heading',
        '|',
        'fontSize',
        'fontFamily',
        'fontColor',
        'fontBackgroundColor',
        '|',
        'bold',
        'italic',
        'underline',
        {
          label: 'Formatting',
          icon: 'text',
          items: [
            'strikethrough',
            'subscript',
            'superscript',
            'code',
            'horizontalLine',
            '|',
            'removeFormat',
          ],
        },
        'specialCharacters',
        '|',
        'link',
        'highlight',
        'blockQuote',
        'codeBlock',
        'htmlEmbed',
        '|',
        'alignment',
        '|',
        'bulletedList',
        'numberedList',
        'todoList',
        'outdent',
        'indent',
        '|',
        'sourceEditing',
      ],
      shouldNotGroupWhenFull: true,
    },
    fontFamily: {
      supportAllValues: true,
    },
    fontSize: {
      options: ['default', 10, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 32],
      supportAllValues: true,
    },
    list: {
      properties: {
        styles: true,
        startIndex: true,
        reversed: true,
      },
    },
    link: {
      decorators: {
        addTargetToExternalLinks: true,
        defaultProtocol: 'https://',
        toggleDownloadable: {
          mode: 'manual',
          label: 'Downloadable',
          attributes: {
            download: 'file',
          },
        },
      },
    },
    placeholder: props.placeholder,
    language: 'vi',
  }
}

onMounted(() => {
  window.addEventListener('resize', onEditorReady)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onEditorReady)
})

const onEditorReady = () => {
  let dropdownPanels = document.querySelectorAll('.ck-dropdown__panel')

  dropdownPanels.forEach((panel) => {
    let parentElement = panel.closest('.ck.ck-dropdown')
    let parentElement1 = panel.closest('.ck.ck-toolbar')
    if (parentElement1) {
      let newMaxWidth = parentElement1.offsetWidth * 0.75

      let parentRect = parentElement.getBoundingClientRect()
      let parentRect1 = parentElement1.getBoundingClientRect()
      let distanceToRight = parentRect1.right - parentRect.left
      let distanceToLeft = parentRect.right - parentRect1.left

      if (distanceToRight < newMaxWidth && distanceToRight < distanceToLeft) {
        panel.style.right = '0px'
        panel.style.left = 'auto'
        newMaxWidth =
          distanceToLeft > newMaxWidth ? newMaxWidth : distanceToLeft
      } else {
        panel.style.left = '0px'
        panel.style.right = 'auto'
        newMaxWidth =
          distanceToRight > newMaxWidth ? newMaxWidth : distanceToRight
      }
      panel.style.maxWidth = `${newMaxWidth}px`
    }
  })
}
</script>
<style>
.ck.ck-reset.ck-list {
  max-height: 200px;
  overflow: auto;
}
.ck.ck-editor__editable_inline {
  padding-bottom: 20px;
}
.ck.ck-content {
  max-height: 700px;
}
.ck-content * {
  line-height: 1.5;
}
.ck-content .image-inline.image-style-align-left {
  margin-right: var(--ck-image-style-spacing);
}
.ck-content .image-inline.image-style-align-right {
  margin-left: var(--ck-image-style-spacing);
}
.ck-content .image-inline.image-style-align-left,
.ck-content .image-inline.image-style-align-right {
  margin-top: inherit;
  margin-bottom: inherit;
}
.ck-content blockquote {
  display: block;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 40px;
  margin-inline-end: 40px;
}
.ck-content strong,
.ck-content b {
  font-weight: bold;
}
.ck-content i,
.ck-content address {
  font-style: italic;
}

/* heading elements */
.ck-content h1 {
  display: block;
  font-size: 2em;
  margin-block-start: 0.67em;
  margin-block-end: 0.67em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}
.ck-content h2 {
  display: block;
  font-size: 1.5em;
  margin-block-start: 0.83em;
  margin-block-end: 0.83em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}
.ck-content h3 {
  display: block;
  font-size: 1.17em;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}
.ck-content h4 {
  display: block;
  margin-block-start: 1.33em;
  margin-block-end: 1.33em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}
.ck-content h5 {
  display: block;
  font-size: 0.83em;
  margin-block-start: 1.67em;
  margin-block-end: 1.67em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}
.ck-content h6 {
  display: block;
  font-size: 0.67em;
  margin-block-start: 2.33em;
  margin-block-end: 2.33em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  font-weight: bold;
}

/* tables */
.ck-content table {
  display: table;
  border-collapse: separate;
  border-spacing: 2px;
  border-color: gray;
}
.ck-content .table table td {
  border: 1px solid #bfbfbf !important;
}
.ck-content thead {
  display: table-header-group;
  vertical-align: middle;
  border-color: inherit;
}
.ck-content tbody {
  display: table-row-group;
  vertical-align: middle;
  border-color: inherit;
}
.ck-content tfoot {
  display: table-footer-group;
  vertical-align: middle;
  border-color: inherit;
}
/* for tables without table section elements (can happen with XHTML or dynamically created tables) */
.ck-content table > tr {
  vertical-align: middle;
}
.ck-content col {
  display: table-column;
}
.ck-content colgroup {
  display: table-column-group;
}
.ck-content tr {
  display: table-row;
  vertical-align: inherit;
  border-color: inherit;
}
.ck-content td,
.ck-content th {
  display: table-cell;
  vertical-align: inherit;
}
.ck-content th {
  font-weight: bold;
}
.ck-content caption {
  display: table-caption;
  text-align: center;
}

/* lists */
.ck-content ul,
.ck-content menu,
.ck-content dir {
  display: block;
  list-style-type: disc;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  padding-inline-start: 40px;
}
.ck-content ol {
  display: block;
  list-style-type: decimal;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  padding-inline-start: 40px;
}
.ck-content li {
  display: list-item;
  text-align: match-parent;
}
.ck-content ::marker {
  unicode-bidi: isolate;
  font-variant-numeric: tabular-nums;
  white-space: pre;
  text-transform: none;
}
.ck-content ul ul,
.ck-content ol ul {
  list-style-type: circle;
}
.ck-content ol ol ul,
.ck-content ol ul ul,
.ck-content ul ol ul,
.ck-content ul ul ul {
  list-style-type: square;
}
.ck-content a:any-link {
  color: blue;
  text-decoration: underline;
  cursor: auto;
}
.ck-content a:any-link:active {
  color: red;
}
</style>
