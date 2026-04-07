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

    // =========================================================
    // 🛡️ 极其极其极其霸气的前端 RBAC 权限拦截雷达！
    // =========================================================
    let is_boss = frappe.user.has_role('Administrator') || frappe.user.has_role('System Manager') || frappe.session.user === "Administrator";
    
    if (!is_boss) {
        // 发现普通员工/马甲！直接进行物理超度，物理移除机密菜单！
        $wrapper.find('#finance-menu').remove();
        $wrapper.find('#asset-menu').remove();
        $wrapper.find('#nav-asset-btn').remove(); // 顺手把左侧资产图标也藏了

        $wrapper.find('#ai-context-status').html(`
            <div class="context-tag">模块: 销售、采购、库存</div>
            <div class="context-tag">状态: 普通员工级查询授权</div>
        `);
        $wrapper.find('#ai-greeting-text').text("您好！我是进销存智能助手，已为您开启安全查询模式。");
        addLog('🔒 识别到员工权限，已自动触发系统级降级，物理移除机密业务模块！', 'warn');
    } else {
        // 老板登场！全功率开启！
        $wrapper.find('#ai-context-status').html(`
            <div class="context-tag">模块: 销售、采购、库存、财务、资产</div>
            <div class="context-tag">状态: 高管最高级全链路授权</div>
        `);
        $wrapper.find('#ai-greeting-text').text("老板您好！企业全链路总管已就位，请随时下达最高指令！");
        addLog('👑 识别到老板/管理员登场，系统全量金刚权限已完全解锁！', 'success');
    }

    $wrapper.find('#ai-user-input').on('keypress', function(e) { if(e.which === 13) sendMessage(); });
    $wrapper.find('#send-btn').on('click', function() { sendMessage(); });
    
    $wrapper.find('.dropdown > .quick-btn').on('click', function(e) {
        e.stopPropagation(); 
        $(this).parent('.dropdown').toggleClass('show-menu');
    });

    $(document).on('click', function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $wrapper.find('.dropdown').removeClass('show-menu');
        }
    });

    $wrapper.find('.quick-btn, .quick-btn-menu').on('click', function(e) {
        let msg = $(this).attr('data-msg');
        if (msg) {
            e.preventDefault(); 
            $wrapper.find('#ai-user-input').val(msg);
            sendMessage();
            $wrapper.find('.dropdown').removeClass('show-menu'); 
        }
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
        let filePrefix = $(this).attr('data-prefix') || "ERPNext数据导出"; 
        let data = window[dataId]; 
        
        if (!data || data.length === 0) {
            frappe.msgprint('⚠️ 当前没有可导出的数据');
            return;
        }

        addLog('正在内存中拼装 Excel 数据格式...', 'sys');
        
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

        addLog(`接收到指令：[${text}]，正在构建安全查询上下文...`, 'sys');
        let loadingId = 'loading-' + Date.now();
        history.innerHTML += `<div id="${loadingId}" style="text-align: left; margin-bottom: 15px; color: #64748b;">AI 正在生成精美排版中...</div>`;
        history.scrollTop = history.scrollHeight;

        let currentModel = $wrapper.find('#ai-model-id').val();

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
                        let filePrefix = r.message.action_button.file_prefix || 'ERPNext数据导出'; 
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