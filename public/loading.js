/**
 * 星星对话 - 加载遮罩控制
 * 页面加载时立即显示遮罩，当欢迎消息出现时移除
 */
(function () {
    // 立即激活遮罩层
    document.body.classList.add('loading-overlay-active');

    function removeOverlay() {
        document.body.classList.remove('loading-overlay-active');
        document.body.classList.add('chainlit-loading-done');
    }

    var triggered = false;

    var observer = new MutationObserver(function () {
        if (triggered) return;
        // 检测 on_chat_start 发送的欢迎消息是否已渲染
        var allNodes = document.querySelectorAll('*');
        for (var i = 0; i < allNodes.length; i++) {
            var el = allNodes[i];
            var testid = el.getAttribute('data-testid') || '';
            if (testid === 'message' || testid.indexOf('message') === 0) {
                triggered = true;
                removeOverlay();
                observer.disconnect();
                return;
            }
        }
        // 备用：检测 markdown 渲染的欢迎消息内容
        var markdownBodies = document.querySelectorAll('.markdown-body');
        if (markdownBodies.length > 0) {
            triggered = true;
            removeOverlay();
            observer.disconnect();
        }
    });

    // 等待 DOM 就绪后开始监听
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    } else {
        document.addEventListener('DOMContentLoaded', function () {
            observer.observe(document.body, { childList: true, subtree: true });
        });
    }

    // 兜底：30秒后强制移除遮罩
    setTimeout(function () {
        if (!triggered) {
            triggered = true;
            removeOverlay();
            observer.disconnect();
        }
    }, 30000);
})();
