! function e(t, n, r) {
    function s(o, u) {
        if (!n[o]) {
            if (!t[o]) {
                var a = "function" == typeof require && require;
                if (!u && a) return a(o, !0);
                if (i) return i(o, !0);
                var f = new Error("Cannot find module '" + o + "'");
                throw f.code = "MODULE_NOT_FOUND", f
            }
            var l = n[o] = {
                exports: {}
            };
            t[o][0].call(l.exports, function(e) {
                var n = t[o][1][e];
                return s(n || e)
            }, l, l.exports, e, t, n, r)
        }
        return n[o].exports
    }
    for (var i = "function" == typeof require && require, o = 0; o < r.length; o++) s(r[o]);
    return s
}({
    1: [function(require, module, exports) {
        (function(global) {
            ! function() {
                var highlightJS = require("./highlight.js-internals.js").HighlightJS,
                    diffJson = null,
                    currentSelectionColumnId = -1;

                function Diff2HtmlUI(config) {
                    var cfg = config || {};
                    cfg.diff ? diffJson = Diff2Html.getJsonFromDiff(cfg.diff) : cfg.json && (diffJson = cfg.json), this._initSelection()
                }
                Diff2HtmlUI.prototype.draw = function(targetId, config) {
                    var cfg = config || {};
                    cfg.inputFormat = "json";
                    var $target = this._getTarget(targetId);
                    $target.html(Diff2Html.getPrettyHtml(diffJson, cfg)), cfg.synchronisedScroll && this.synchronisedScroll($target, cfg)
                }, Diff2HtmlUI.prototype.synchronisedScroll = function(targetId) {
                    this._getTarget(targetId).find(".d2h-file-side-diff").scroll(function() {
                        var $this = $(this);
                        $this.closest(".d2h-file-wrapper").find(".d2h-file-side-diff").scrollLeft($this.scrollLeft())
                    })
                }, Diff2HtmlUI.prototype.fileListCloseable = function(targetId, startVisible) {
                    var $target = this._getTarget(targetId),
                        hashTag = this._getHashTag(),
                        $showBtn = $target.find(".d2h-show"),
                        $hideBtn = $target.find(".d2h-hide"),
                        $fileList = $target.find(".d2h-file-list");

                    function show() {
                        $showBtn.hide(), $hideBtn.show(), $fileList.show()
                    }

                    function hide() {
                        $hideBtn.hide(), $showBtn.show(), $fileList.hide()
                    }
                    "files-summary-show" === hashTag ? show() : "files-summary-hide" === hashTag ? hide() : startVisible ? show() : hide(), $showBtn.click(show), $hideBtn.click(hide)
                }, Diff2HtmlUI.prototype.highlightCode = function(targetId) {
                    this._getTarget(targetId).find(".d2h-file-wrapper").map(function(_i, file) {
                        var oldLinesState, newLinesState, $file = $(file),
                            language = $file.data("lang");
                        $file.find(".d2h-code-line-ctn").map(function(_j, line) {
                            var lineState, $line = $(line),
                                text = line.textContent,
                                lineParent = line.parentNode;
                            lineState = -1 !== lineParent.className.indexOf("d2h-del") ? oldLinesState : newLinesState;
                            var result = hljs.getLanguage(language) ? hljs.highlight(language, text, !0, lineState) : hljs.highlightAuto(text); - 1 !== lineParent.className.indexOf("d2h-del") ? oldLinesState = result.top : newLinesState = (-1 !== lineParent.className.indexOf("d2h-ins") || (oldLinesState = result.top), result.top);
                            var originalStream = highlightJS.nodeStream(line);
                            if (originalStream.length) {
                                var resultNode = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
                                resultNode.innerHTML = result.value, result.value = highlightJS.mergeStreams(originalStream, highlightJS.nodeStream(resultNode), text)
                            }
                            $line.addClass("hljs"), $line.addClass(result.language), $line.html(result.value)
                        })
                    })
                }, Diff2HtmlUI.prototype._getTarget = function(targetId) {
                    return "object" == typeof targetId && targetId instanceof jQuery ? targetId : "string" == typeof targetId ? $(targetId) : (console.error("Wrong target provided! Falling back to default value 'body'."), console.log("Please provide a jQuery object or a valid DOM query string."), $("body"))
                }, Diff2HtmlUI.prototype._getHashTag = function() {
                    var docUrl = document.URL,
                        hashTagIndex = docUrl.indexOf("#"),
                        hashTag = null;
                    return -1 !== hashTagIndex && (hashTag = docUrl.substr(hashTagIndex + 1)), hashTag
                }, Diff2HtmlUI.prototype._distinct = function(collection) {
                    return collection.filter(function(v, i) {
                        return collection.indexOf(v) === i
                    })
                }, Diff2HtmlUI.prototype._initSelection = function() {
                    var body = $("body"),
                        that = this;
                    body.on("mousedown", ".d2h-diff-table", function(event) {
                        var target = $(event.target),
                            table = target.closest(".d2h-diff-table");
                        target.closest(".d2h-code-line,.d2h-code-side-line").length ? (table.removeClass("selecting-left"), table.addClass("selecting-right"), currentSelectionColumnId = 1) : target.closest(".d2h-code-linenumber,.d2h-code-side-linenumber").length && (table.removeClass("selecting-right"), table.addClass("selecting-left"), currentSelectionColumnId = 0)
                    }), body.on("copy", ".d2h-diff-table", function(event) {
                        var clipboardData = event.originalEvent.clipboardData,
                            text = that._getSelectedText();
                        clipboardData.setData("text", text), event.preventDefault()
                    })
                }, Diff2HtmlUI.prototype._getSelectedText = function() {
                    var doc = window.getSelection().getRangeAt(0).cloneContents(),
                        nodes = doc.querySelectorAll("tr"),
                        text = "",
                        idx = currentSelectionColumnId;
                    return 0 === nodes.length ? text = doc.textContent : [].forEach.call(nodes, function(tr, i) {
                        var td = tr.cells[1 === tr.cells.length ? 0 : idx];
                        text += (i ? "\n" : "") + td.textContent.replace(/(?:\r\n|\r|\n)/g, "")
                    }), text
                }, module.exports.Diff2HtmlUI = Diff2HtmlUI, global.Diff2HtmlUI = Diff2HtmlUI
            }()
        }).call(this, "undefined" != typeof global ? global : "undefined" != typeof self ? self : "undefined" != typeof window ? window : {})
    }, {
        "./highlight.js-internals.js": 2
    }],
    2: [function(require, module, exports) {
        ! function() {
            function HighlightJS() {}
            var ArrayProto = [];

            function escape(value) {
                return value.replace(/&/gm, "&amp;").replace(/</gm, "&lt;").replace(/>/gm, "&gt;")
            }

            function tag(node) {
                return node.nodeName.toLowerCase()
            }
            HighlightJS.prototype.nodeStream = function(node) {
                var result = [];
                return function _nodeStream(node, offset) {
                    for (var child = node.firstChild; child; child = child.nextSibling) 3 === child.nodeType ? offset += child.nodeValue.length : 1 === child.nodeType && (result.push({
                        event: "start",
                        offset: offset,
                        node: child
                    }), offset = _nodeStream(child, offset), tag(child).match(/br|hr|img|input/) || result.push({
                        event: "stop",
                        offset: offset,
                        node: child
                    }));
                    return offset
                }(node, 0), result
            }, HighlightJS.prototype.mergeStreams = function(original, highlighted, value) {
                var processed = 0,
                    result = "",
                    nodeStack = [];

                function selectStream() {
                    return original.length && highlighted.length ? original[0].offset !== highlighted[0].offset ? original[0].offset < highlighted[0].offset ? original : highlighted : "start" === highlighted[0].event ? original : highlighted : original.length ? original : highlighted
                }

                function open(node) {
                    result += "<" + tag(node) + ArrayProto.map.call(node.attributes, function(a) {
                        return " " + a.nodeName + '="' + escape(a.value) + '"'
                    }).join("") + ">"
                }

                function close(node) {
                    result += "</" + tag(node) + ">"
                }

                function render(event) {
                    ("start" === event.event ? open : close)(event.node)
                }
                for (; original.length || highlighted.length;) {
                    var stream = selectStream();
                    if (result += escape(value.substring(processed, stream[0].offset)), processed = stream[0].offset, stream === original) {
                        for (nodeStack.reverse().forEach(close); render(stream.splice(0, 1)[0]), (stream = selectStream()) === original && stream.length && stream[0].offset === processed;);
                        nodeStack.reverse().forEach(open)
                    } else "start" === stream[0].event ? nodeStack.push(stream[0].node) : nodeStack.pop(), render(stream.splice(0, 1)[0])
                }
                return result + escape(value.substr(processed))
            }, module.exports.HighlightJS = new HighlightJS
        }()
    }, {}]
}, {}, [1]);