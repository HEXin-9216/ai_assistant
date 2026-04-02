frappe.pages['ai-chat'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({ parent: wrapper, title: '企业智能业务助手', single_column: true });

    if (!window.marked) {
        frappe.require("https://cdn.jsdelivr.net/npm/marked/marked.min.js");
    }

    $(frappe.render_template("ai_chat", {})).appendTo(page.main);

    function addLog(message, type = 'sys') {
        let logContent = $(wrapper).find('#ai-log-content');
        let time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
        let logHtml = `<div class="log-${type}">[${time}] ${message}</div>`;
        logContent.append(logHtml);
        logContent.scrollTop(logContent[0].scrollHeight);
    }

    addLog('系统初始化完毕。Markdown 美颜引擎已挂载。', 'success');

    const $wrapper = $(wrapper);

    $wrapper.find('#ai-user-input').on('keypress', function(e) { if(e.which === 13) sendMessage(); });
    $wrapper.find('#send-btn').on('click', function() { sendMessage(); });
    $wrapper.find('.quick-btn').on('click', function() {
        let msg = $(this).attr('data-msg');
        $wrapper.find('#ai-user-input').val(msg);
        sendMessage();
    });

    $wrapper.find('#ai-platform').on('change', function() {
        let platform = $(this).val();
        let baseUrlInput = $wrapper.find('#ai-base-url');
        let modelIdInput = $wrapper.find('#ai-model-id');

        if (platform === 'deepseek') {
            baseUrlInput.val('https://api.deepseek.com/v1'); modelIdInput.val('deepseek-chat');
            addLog('老板，已安全切换至 DeepSeek 引擎，握手成功！', 'success');
        } else if (platform === 'qwen') {
            baseUrlInput.val('https://dashscope.aliyuncs.com/compatible-mode/v1'); modelIdInput.val('qwen-plus');
            addLog('老板，已安全切换至 阿里云通义千问(Qwen) 引擎！', 'success');
        } else if (platform === 'glm4') {
            baseUrlInput.val('https://open.bigmodel.cn/api/paas/v4'); modelIdInput.val('glm-4');
            addLog('老板，已安全切换至 智谱(GLM-4) 引擎！', 'success');
        }
    });

    $wrapper.find('#chat-history').on('click', '.ai-reply-content a', function(e) {
        e.preventDefault(); 
        let targetUrl = $(this).attr('href');
        window.open(targetUrl, '_blank'); 
    });

    $wrapper.find('#chat-history').on('click', '.action-export-btn', function() {
        let dataId = $(this).attr('data-id');
        // 🌟 极其智能地读取专属文件名前缀
        let filePrefix = $(this).attr('data-prefix') || "ERPNext数据导出"; 
        let data = window[dataId]; 
        
        if (!data || data.length === 0) {
            frappe.msgprint('⚠️ 当前没有可导出的数据');
            return;
        }

        addLog('收到老板指令，正在内存中拼装 Excel 数据格式...', 'sys');
        
        let csvContent = '\uFEFF'; 
        let headers = Object.keys(data[0]);
        csvContent += headers.join(",") + "\r\n";
        
        data.forEach(function(row) {
            let rowArray = headers.map(header => {
                let cell = row[header] === null || row[header] === undefined ? "" : row[header];
                cell = cell.toString().replace(/"/g, '""');
                if (cell.search(/("|,|\n)/g) >= 0) cell = `"${cell}"`;
                return cell;
            });
            csvContent += rowArray.join(",") + "\r\n";
        });
        
        let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        let link = document.createElement("a");
        let url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        // 🌟 极其优雅的文件命名
        let fileName = filePrefix + "_" + new Date().toISOString().slice(0, 10) + ".csv";
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        addLog(`✅ 极其顺滑！[${fileName}] 已成功触发下载！`, 'success');
    });

    function sendMessage() {
        let input = $wrapper.find('#ai-user-input')[0];
        let text = input.value.trim();
        if (!text) return;

        let history = $wrapper.find('#chat-history')[0];
        history.innerHTML += `<div style="text-align: right; margin-bottom: 15px;"><span style="background: #2490ef; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; display: inline-block;">${text}</span></div>`;
        input.value = '';

        addLog(`接收到指令：[${text}]，正在构建查询上下文...`, 'sys');
        let loadingId = 'loading-' + Date.now();
        history.innerHTML += `<div id="${loadingId}" style="text-align: left; margin-bottom: 15px; color: #64748b;">AI 正在生成精美排版中...</div>`;
        history.scrollTop = history.scrollHeight;

        let currentModel = $wrapper.find('#ai-model-id').val();
        addLog(`正在通过加密通道向 [${currentModel}] 发起请求...`, 'warn');

        frappe.call({
            method: "ai_assistant.ai_assistant.api.chat",
            args: { message: text, platform: $wrapper.find('#ai-platform').val(), model_id: currentModel },
            callback: function(r) {
                if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();
                
                if(r.message && r.message.status === 'success') {
                    let finalHtml = (window.marked && typeof marked.parse === 'function') ? marked.parse(r.message.reply) : r.message.reply;

                    let actionBtnHtml = '';
                    if (r.message.action_button && r.message.action_button.type === 'export_excel') {
                        let actionDataId = 'export-data-' + Date.now();
                        window[actionDataId] = r.message.action_button.data; 
                        let filePrefix = r.message.action_button.file_prefix || 'ERPNext数据导出'; // 🌟 读取后端传来的前缀
                        actionBtnHtml = `
                            <div style="margin-top: 15px; border-top: 1px dashed #cbd5e1; padding-top: 12px;">
                                <button class="action-export-btn" data-id="${actionDataId}" data-prefix="${filePrefix}">
                                    ${r.message.action_button.label}
                                </button>
                            </div>
                        `;
                    }

                    history.innerHTML += `
                        <div style="text-align: left; margin-bottom: 15px;">
                            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 15px 15px 15px 0; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 85%;">
                                <div class="ai-reply-content">${finalHtml}</div>
                                ${actionBtnHtml}
                            </div>
                        </div>`;
                    history.scrollTop = history.scrollHeight;
                    r.message.logs.forEach(log => addLog(log, 'success'));
                }
            },
            error: function() {
                if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();
                addLog('糟糕！后端 Python 接口连接失败。', 'error');
            }
        });
    }
};