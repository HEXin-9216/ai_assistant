frappe.pages['ai-chat'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({ parent: wrapper, title: '企业智能业务助手', single_column: true });

    if (!window.marked) {
        frappe.require("https://cdn.jsdelivr.net/npm/marked/marked.min.js");
    }

    $(frappe.render_template("ai_chat", {})).appendTo(page.main);

    // =========================================================
    // 🌐 首席架构师极其优雅的 i18n 国际化引擎 (纯净版)
    // =========================================================
    let sysLangRaw = frappe.boot.user.language || 'zh';
    let currentLang = sysLangRaw.startsWith('en') ? 'en' : (sysLangRaw.startsWith('es') ? 'es' : 'zh');

    const i18nDict = {
        'zh': {
            ai_config_title: "🤖 AI 引擎配置", lbl_platform: "选择 AI 平台", lbl_url: "Base URL 接口地址", lbl_model: "调用模型 ID",
            context_title: "📍 当前业务上下文", nav_title: "🚀 ERPNext 模块直达",
            mod_selling: "销售", mod_buying: "采购", mod_stock: "库存", mod_projects: "项目", mod_assets: "资产", mod_mfg: "生产",
            menu_finance: "💰 财务会计 ▾", menu_assets: "🏢 固定资产 ▾", menu_stock: "📦 进销存查询 ▾",
            btn_fin_health: "🏥 财务体检", btn_fin_overdue: "🚨 智能催款", btn_fin_expense: "💸 成本追踪",
            btn_ast_list: "🏢 资产盘点", btn_ast_value: "📉 资产净值", btn_ast_leave: "🏃‍♂️ 离职交接",
            btn_stk_sales_report: "📊 销售月报", btn_stk_low: "📦 低库存预警", btn_stk_so: "🛒 销售订单", btn_stk_si: "🧾 销售发票",
            btn_stk_pr: "📥 采购入库", btn_stk_dn: "🚚 销售出库", btn_stk_sq: "📝 供应商报价", btn_stk_po: "🛍️ 采购订单", btn_stk_pi: "🧾 采购发票",
            placeholder_input: "输入指令，按下发送...", btn_send: "发送", log_title: "🖥️ 运行日志监控 (系统状态：正常)",
            greet_boss: "您好老板！我是您的专属企业智能助手。全系金刚已就位，请下达指令！",
            greet_emp: "您好！我是进销存智能助手，已为您开启安全查询模式。",
            ctx_emp: `<div class="context-tag">模块: 销售、采购、库存</div><div class="context-tag">状态: 普通员工级查询授权</div>`,
            ctx_boss: `<div class="context-tag">模块: 销售、采购、库存、财务、资产</div><div class="context-tag">状态: 高管最高级全链路授权</div>`,
            
            msg_fin_health: "生成一句话财务体检报告，看看公司总资产、负债和目前的利润", msg_fin_overdue: "帮我查一下目前有哪些客户的账款逾期了？列出催款清单",
            msg_fin_expense: "帮我查一下上个月各成本中心一共烧了多少钱？列出开销明细", msg_ast_list: "帮我盘点一下公司现在的固定资产家底，总共值多少钱？列出资产清单",
            msg_ast_value: "查一下咱们目前最值钱的5个资产是什么？看看净值和贬值情况", msg_ast_leave: "有员工要离职了，查一下名下挂着哪些公司资产需要交接？",
            msg_stk_sales_report: "帮我生成本月的销售月报及大客户贡献榜", msg_stk_low: "帮我查一下当前库存数量低于 10 的商品",
            msg_stk_so: "查看最近的销售订单", msg_stk_si: "查看最近的销售发票", msg_stk_pr: "查看最近的采购入库单", msg_stk_dn: "查看最近的销售出库单",
            msg_stk_sq: "查看最近的供应商报价", msg_stk_po: "查看最近的采购订单", msg_stk_pi: "查看最近的采购发票",

            log_init: "系统初始化完毕。Markdown 美颜引擎已挂载。",
            log_emp_warn: "🔒 识别到员工权限，已自动触发系统级降级，物理移除机密业务模块！",
            log_boss_success: "👑 识别到老板/管理员登场，系统全量金刚权限已完全解锁！",
            log_switch: "已安全切换至",
            log_export_start: "正在内存中拼装 Excel 数据格式...",
            log_export_success: "✅ 极其顺滑！[{fileName}] 已成功触发下载！",
            log_send: "接收到指令：[{text}]，正在构建安全查询上下文...",
            log_loading: "AI 正在生成精美排版中...",
            log_err: "糟糕！后端 Python 接口连接失败。",
            export_prefix: "ERPNext数据导出",
            empty_export: "⚠️ 当前没有可导出的数据"
        },
        'en': {
            ai_config_title: "🤖 AI Engine Config", lbl_platform: "Select AI Platform", lbl_url: "Base URL", lbl_model: "Model ID",
            context_title: "📍 Current Context", nav_title: "🚀 ERPNext Shortcuts",
            mod_selling: "Selling", mod_buying: "Buying", mod_stock: "Stock", mod_projects: "Projects", mod_assets: "Assets", mod_mfg: "Mfg",
            menu_finance: "💰 Finance ▾", menu_assets: "🏢 Assets ▾", menu_stock: "📦 Inventory ▾",
            btn_fin_health: "🏥 Financial Health", btn_fin_overdue: "🚨 Overdue Invoices", btn_fin_expense: "💸 Cost Tracking",
            btn_ast_list: "🏢 Asset Inventory", btn_ast_value: "📉 Asset Value", btn_ast_leave: "🏃‍♂️ Employee Handover",
            btn_stk_sales_report: "📊 Sales Report", btn_stk_low: "📦 Low Stock Alert", btn_stk_so: "🛒 Sales Orders", btn_stk_si: "🧾 Sales Invoices",
            btn_stk_pr: "📥 Purchase Receipts", btn_stk_dn: "🚚 Delivery Notes", btn_stk_sq: "📝 Supplier Quotes", btn_stk_po: "🛍️ Purchase Orders", btn_stk_pi: "🧾 Purchase Invoices",
            placeholder_input: "Enter command and press send...", btn_send: "Send", log_title: "🖥️ System Logs (Status: Normal)",
            greet_boss: "Hello Boss! Your Enterprise AI Assistant is ready. Please give your command!",
            greet_emp: "Hello! I am your Inventory Assistant. Safe query mode is enabled.",
            ctx_emp: `<div class="context-tag">Modules: Sales, Purchase, Stock</div><div class="context-tag">Status: Employee Access</div>`,
            ctx_boss: `<div class="context-tag">Modules: All Modules</div><div class="context-tag">Status: Executive Full Access</div>`,
            
            msg_fin_health: "Generate a financial health report showing total assets, liabilities, and current profit.", msg_fin_overdue: "Check which customers have overdue invoices and list them.",
            msg_fin_expense: "Check the total expenses for each cost center last month. List the details.", msg_ast_list: "Take inventory of our current fixed assets and their total value.",
            msg_ast_value: "What are our top 5 most valuable assets? Show their net value and depreciation.", msg_ast_leave: "An employee is leaving. Check what company assets are assigned to them.",
            msg_stk_sales_report: "Generate this month's sales report and top customers.", msg_stk_low: "Check items with stock quantity below 10.",
            msg_stk_so: "Show recent Sales Orders", msg_stk_si: "Show recent Sales Invoices", msg_stk_pr: "Show recent Purchase Receipts", msg_stk_dn: "Show recent Delivery Notes",
            msg_stk_sq: "Show recent Supplier Quotations", msg_stk_po: "Show recent Purchase Orders", msg_stk_pi: "Show recent Purchase Invoices",

            log_init: "System Initialized. Markdown Engine Ready.",
            log_emp_warn: "🔒 Employee Access Detected. Confidential modules removed.",
            log_boss_success: "👑 Admin Access Detected. Full system capabilities unlocked!",
            log_switch: "Switched to engine",
            log_export_start: "Building CSV...",
            log_export_success: "✅ Download triggered for [{fileName}]!",
            log_send: "Command received: [{text}], building secure context...",
            log_loading: "AI is generating formatted response...",
            log_err: "Error connecting to backend API.",
            export_prefix: "ERPNext_Data_Export",
            empty_export: "⚠️ No data available to export"
        },
        'es': {
            ai_config_title: "🤖 Configuración de IA", lbl_platform: "Plataforma de IA", lbl_url: "URL Base", lbl_model: "ID del Modelo",
            context_title: "📍 Contexto Actual", nav_title: "🚀 Módulos ERPNext",
            mod_selling: "Ventas", mod_buying: "Compras", mod_stock: "Inventario", mod_projects: "Proyectos", mod_assets: "Activos", mod_mfg: "Fabricación",
            menu_finance: "💰 Finanzas ▾", menu_assets: "🏢 Activos Fijos ▾", menu_stock: "📦 Consultas de Inv ▾",
            btn_fin_health: "🏥 Salud Financiera", btn_fin_overdue: "🚨 Facturas Vencidas", btn_fin_expense: "💸 Costos",
            btn_ast_list: "🏢 Inventario de Activos", btn_ast_value: "📉 Valor de Activos", btn_ast_leave: "🏃‍♂️ Entrega de Empleado",
            btn_stk_sales_report: "📊 Reporte de Ventas", btn_stk_low: "📦 Alerta de Stock", btn_stk_so: "🛒 Pedidos de Venta", btn_stk_si: "🧾 Facturas de Venta",
            btn_stk_pr: "📥 Recibos de Compra", btn_stk_dn: "🚚 Notas de Entrega", btn_stk_sq: "📝 Cotizaciones", btn_stk_po: "🛍️ Pedidos de Compra", btn_stk_pi: "🧾 Facturas de Compra",
            placeholder_input: "Ingrese el comando y presione enviar...", btn_send: "Enviar", log_title: "🖥️ Registros del Sistema (Estado: Normal)",
            greet_boss: "¡Hola Jefe! Su Asistente de IA está listo. ¡Por favor, dé su orden!",
            greet_emp: "¡Hola! Soy su asistente de inventario. Modo seguro activado.",
            ctx_emp: `<div class="context-tag">Módulos: Ventas, Compras, Inventario</div><div class="context-tag">Estado: Acceso de Empleado</div>`,
            ctx_boss: `<div class="context-tag">Módulos: Todos los Módulos</div><div class="context-tag">Estado: Acceso Ejecutivo Total</div>`,
            
            msg_fin_health: "Genere un informe de salud financiera que muestre los activos totales, los pasivos y las ganancias.", msg_fin_overdue: "Revise qué clientes tienen facturas vencidas y lístelos.",
            msg_fin_expense: "Revise los gastos totales de cada centro de costos el mes pasado.", msg_ast_list: "Haga un inventario de nuestros activos fijos actuales y su valor total.",
            msg_ast_value: "¿Cuáles son nuestros 5 activos más valiosos? Muestre su valor neto.", msg_ast_leave: "Un empleado se va. Compruebe qué activos tiene asignados.",
            msg_stk_sales_report: "Genere el informe de ventas de este mes y los mejores clientes.", msg_stk_low: "Verifique los artículos con cantidad de stock por debajo de 10.",
            msg_stk_so: "Mostrar pedidos de venta recientes", msg_stk_si: "Mostrar facturas de venta recientes", msg_stk_pr: "Mostrar recibos de compra recientes", msg_stk_dn: "Mostrar notas de entrega recientes",
            msg_stk_sq: "Mostrar cotizaciones de proveedores", msg_stk_po: "Mostrar pedidos de compra recientes", msg_stk_pi: "Mostrar facturas de compra recientes",

            log_init: "Sistema inicializado. Motor Markdown listo.",
            log_emp_warn: "🔒 Acceso de empleado detectado. Módulos confidenciales eliminados.",
            log_boss_success: "👑 ¡Acceso de administrador detectado. Capacidades completas desbloqueadas!",
            log_switch: "Cambiado al motor",
            log_export_start: "Construyendo CSV...",
            log_export_success: "✅ ¡Descarga iniciada para [{fileName}]!",
            log_send: "Comando recibido: [{text}], construyendo contexto...",
            log_loading: "La IA está generando el formato...",
            log_err: "Error al conectar con la API Python.",
            export_prefix: "ERPNext_Datos",
            empty_export: "⚠️ No hay datos para exportar"
        }
    };

    let dict = i18nDict[currentLang];

    function addLog(message, type = 'sys') {
        let logContent = $(wrapper).find('#ai-log-content');
        let time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
        let logHtml = `<div class="log-${type}">[${time}] ${message}</div>`;
        logContent.append(logHtml);
        logContent.scrollTop(logContent[0].scrollHeight);
    }

    addLog(dict['log_init'], 'success');

    const $wrapper = $(wrapper);

    // 💥 瞬间将所有文本极其聪明地替换为当前系统语言！
    $wrapper.find('[data-i18n]').each(function() {
        let key = $(this).attr('data-i18n');
        if (dict[key]) {
            if ($(this).is('input')) $(this).attr('placeholder', dict[key]);
            else $(this).html(dict[key]);
        }
    });

    $wrapper.find('[data-i18n-msg]').each(function() {
        let msgKey = $(this).attr('data-i18n-msg');
        if (dict[msgKey]) $(this).attr('data-msg', dict[msgKey]);
    });

    if(currentLang !== 'zh') page.set_title(currentLang === 'en' ? 'Enterprise AI Assistant' : 'Asistente de IA Empresarial');
    $wrapper.find('#log-panel-title').text(dict['log_title']);

    // =========================================================
    // 🛡️ 极其极其极其霸气的前端 RBAC 权限拦截雷达！
    // =========================================================
    let is_boss = frappe.user.has_role('Administrator') || frappe.user.has_role('System Manager') || frappe.session.user === "Administrator";
    
    if (!is_boss) {
        $wrapper.find('#finance-menu').remove();
        $wrapper.find('#asset-menu').remove();
        $wrapper.find('#nav-asset-btn').remove(); 

        $wrapper.find('#ai-context-status').html(dict['ctx_emp']);
        $wrapper.find('#ai-greeting-text').text(dict['greet_emp']);
        addLog(dict['log_emp_warn'], 'warn');
    } else {
        $wrapper.find('#ai-context-status').html(dict['ctx_boss']);
        $wrapper.find('#ai-greeting-text').text(dict['greet_boss']);
        addLog(dict['log_boss_success'], 'success');
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
        let platformName = "";

        if (platform === 'deepseek') {
            baseUrlInput.val('https://api.deepseek.com/v1'); modelIdInput.val('deepseek-chat');
            platformName = "DeepSeek";
        } else if (platform === 'qwen') {
            baseUrlInput.val('https://dashscope.aliyuncs.com/compatible-mode/v1'); modelIdInput.val('qwen-plus');
            platformName = "Qwen";
        } else if (platform === 'glm4') {
            baseUrlInput.val('https://open.bigmodel.cn/api/paas/v4'); modelIdInput.val('glm-4');
            platformName = "GLM-4";
        }
        addLog(`${dict['log_switch']} ${platformName}`, 'success');
    });

    $wrapper.find('#chat-history').on('click', '.ai-reply-content a', function(e) {
        e.preventDefault(); 
        let targetUrl = $(this).attr('href');
        window.open(targetUrl, '_blank'); 
    });

    $wrapper.find('#chat-history').on('click', '.action-export-btn', function() {
        let dataId = $(this).attr('data-id');
        let filePrefix = $(this).attr('data-prefix') || dict['export_prefix']; 
        let data = window[dataId]; 
        
        if (!data || data.length === 0) {
            frappe.msgprint(dict['empty_export']);
            return;
        }

        addLog(dict['log_export_start'], 'sys');
        
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
        
        let successMsg = dict['log_export_success'].replace('{fileName}', fileName);
        addLog(successMsg, 'success');
    });

    function sendMessage() {
        let input = $wrapper.find('#ai-user-input')[0];
        let text = input.value.trim();
        if (!text) return;

        let history = $wrapper.find('#chat-history')[0];
        history.innerHTML += `<div style="text-align: right; margin-bottom: 15px;"><span style="background: #2490ef; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; display: inline-block;">${text}</span></div>`;
        input.value = '';

        let sendMsg = dict['log_send'].replace('{text}', text);
        addLog(sendMsg, 'sys');
        let loadingId = 'loading-' + Date.now();
        history.innerHTML += `<div id="${loadingId}" style="text-align: left; margin-bottom: 15px; color: #64748b;">${dict['log_loading']}</div>`;
        history.scrollTop = history.scrollHeight;

        let currentModel = $wrapper.find('#ai-model-id').val();

        // 💥 极其关键的修改：把前端探测到的 currentLang 作为极其机密的参数传给后端大脑！
        frappe.call({
            method: "ai_assistant.ai_assistant.api.chat",
            args: { message: text, platform: $wrapper.find('#ai-platform').val(), model_id: currentModel, lang: currentLang },
            callback: function(r) {
                if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();
                
                if(r.message && r.message.status === 'success') {
                    let finalHtml = (window.marked && typeof marked.parse === 'function') ? marked.parse(r.message.reply) : r.message.reply;

                    let actionBtnHtml = '';
                    if (r.message.action_button && r.message.action_button.type === 'export_excel') {
                        let actionDataId = 'export-data-' + Date.now();
                        window[actionDataId] = r.message.action_button.data; 
                        let filePrefix = r.message.action_button.file_prefix || dict['export_prefix']; 
                        
                        let btnLabel = currentLang === 'zh' ? '⬇️ 导出数据 (Excel)' : (currentLang === 'en' ? '⬇️ Export Data' : '⬇️ Exportar Datos');
                        actionBtnHtml = `
                            <div style="margin-top: 15px; border-top: 1px dashed #cbd5e1; padding-top: 12px;">
                                <button class="action-export-btn" data-id="${actionDataId}" data-prefix="${filePrefix}">
                                    ${btnLabel}
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
                addLog(dict['log_err'], 'error');
            }
        });
    }
};