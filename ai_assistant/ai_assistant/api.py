import frappe
import requests
import json

# =========================================================
# 🛠️ 极其强大的本地业务工具箱 (七大金刚 - 参数化升级版)
# =========================================================

# --- 销售模块 ---
def get_recent_sales_orders(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        orders = frappe.db.get_list("Sales Order", fields=["name", "customer", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not orders: return {"text": "报告：在指定范围内没有找到任何销售订单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售订单：\n"
        orders_data = [] 
        for o in orders:
            result_str += f"- 订单号: [{o.name}](/app/sales-order/{o.name}), 客户: {o.customer}, 日期: {o.transaction_date}, 金额: ￥{o.grand_total}, 状态: {o.status}\n"
            orders_data.append({"订单编号": o.name, "客户名称": o.customer, "交易日期": str(o.transaction_date), "总金额(元)": float(o.grand_total) if o.grand_total else 0.0, "当前状态": o.status})
        return {"text": result_str, "data": orders_data}
    except Exception as e: return {"text": f"查询销售订单失败：{str(e)}", "data": []}

def get_recent_sales_invoices(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        invoices = frappe.db.get_list("Sales Invoice", fields=["name", "customer", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not invoices: return {"text": "报告：在指定范围内没有找到任何销售发票。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售发票：\n"
        invoices_data = [] 
        for i in invoices:
            result_str += f"- 发票号: [{i.name}](/app/sales-invoice/{i.name}), 客户: {i.customer}, 日期: {i.posting_date}, 金额: ￥{i.grand_total}, 状态: {i.status}\n"
            invoices_data.append({"发票编号": i.name, "客户名称": i.customer, "开票日期": str(i.posting_date), "总金额(元)": float(i.grand_total) if i.grand_total else 0.0, "当前状态": i.status})
        return {"text": result_str, "data": invoices_data}
    except Exception as e: return {"text": f"查询销售发票失败：{str(e)}", "data": []}

# --- 库存模块 ---
def get_recent_purchase_receipts(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        receipts = frappe.db.get_list("Purchase Receipt", fields=["name", "supplier", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not receipts: return {"text": "报告：在指定范围内没有找到任何采购入库单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购入库单：\n"
        receipts_data = [] 
        for r in receipts:
            result_str += f"- 入库单号: [{r.name}](/app/purchase-receipt/{r.name}), 供应商: {r.supplier}, 日期: {r.posting_date}, 金额: ￥{r.grand_total}, 状态: {r.status}\n"
            receipts_data.append({"入库单编号": r.name, "供应商名称": r.supplier, "入库日期": str(r.posting_date), "总金额(元)": float(r.grand_total) if r.grand_total else 0.0, "当前状态": r.status})
        return {"text": result_str, "data": receipts_data}
    except Exception as e: return {"text": f"查询采购入库单失败：{str(e)}", "data": []}

def get_recent_delivery_notes(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        notes = frappe.db.get_list("Delivery Note", fields=["name", "customer", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not notes: return {"text": "报告：在指定范围内没有找到任何销售出库单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售出库单：\n"
        notes_data = [] 
        for n in notes:
            result_str += f"- 出库单号: [{n.name}](/app/delivery-note/{n.name}), 客户: {n.customer}, 日期: {n.posting_date}, 金额: ￥{n.grand_total}, 状态: {n.status}\n"
            notes_data.append({"出库单编号": n.name, "客户名称": n.customer, "出库日期": str(n.posting_date), "总金额(元)": float(n.grand_total) if n.grand_total else 0.0, "当前状态": n.status})
        return {"text": result_str, "data": notes_data}
    except Exception as e: return {"text": f"查询销售出库单失败：{str(e)}", "data": []}

# --- 采购模块 ---
def get_recent_supplier_quotations(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        quotations = frappe.db.get_list("Supplier Quotation", fields=["name", "supplier", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not quotations: return {"text": "报告：在指定范围内没有找到任何供应商报价。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的供应商报价：\n"
        quotations_data = [] 
        for q in quotations:
            result_str += f"- 报价单号: [{q.name}](/app/supplier-quotation/{q.name}), 供应商: {q.supplier}, 日期: {q.transaction_date}, 金额: ￥{q.grand_total}, 状态: {q.status}\n"
            quotations_data.append({"报价单编号": q.name, "供应商名称": q.supplier, "报价日期": str(q.transaction_date), "总金额(元)": float(q.grand_total) if q.grand_total else 0.0, "当前状态": q.status})
        return {"text": result_str, "data": quotations_data}
    except Exception as e: return {"text": f"查询供应商报价失败：{str(e)}", "data": []}

def get_recent_purchase_orders(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        orders = frappe.db.get_list("Purchase Order", fields=["name", "supplier", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not orders: return {"text": "报告：在指定范围内没有找到任何采购订单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购订单：\n"
        orders_data = [] 
        for o in orders:
            result_str += f"- 订单号: [{o.name}](/app/purchase-order/{o.name}), 供应商: {o.supplier}, 日期: {o.transaction_date}, 金额: ￥{o.grand_total}, 状态: {o.status}\n"
            orders_data.append({"采购订单编号": o.name, "供应商名称": o.supplier, "交易日期": str(o.transaction_date), "总金额(元)": float(o.grand_total) if o.grand_total else 0.0, "当前状态": o.status})
        return {"text": result_str, "data": orders_data}
    except Exception as e: return {"text": f"查询采购订单失败：{str(e)}", "data": []}

def get_recent_purchase_invoices(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        invoices = frappe.db.get_list("Purchase Invoice", fields=["name", "supplier", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not invoices: return {"text": "报告：在指定范围内没有找到任何采购发票。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购发票：\n"
        invoices_data = [] 
        for i in invoices:
            result_str += f"- 发票号: [{i.name}](/app/purchase-invoice/{i.name}), 供应商: {i.supplier}, 日期: {i.posting_date}, 金额: ￥{i.grand_total}, 状态: {i.status}\n"
            invoices_data.append({"采购发票编号": i.name, "供应商名称": i.supplier, "开票日期": str(i.posting_date), "总金额(元)": float(i.grand_total) if i.grand_total else 0.0, "当前状态": i.status})
        return {"text": result_str, "data": invoices_data}
    except Exception as e: return {"text": f"查询采购发票失败：{str(e)}", "data": []}


@frappe.whitelist()
def chat(message, platform, model_id):
    API_KEY = "sk-0bdcab13594f47d881b89ea415355401"
    frappe.logger().info(f"AI 小助手接收到指令：[{message}]，准备呼叫：[{model_id}]")

    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = { "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json" }
        
        # 🌟 定义极其聪明的通用参数配置
        common_parameters = {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "查询返回的记录数量，默认 5。如果用户明确要求特定数量（如50条），请传入该数字。"},
                "start_date": {"type": "string", "description": "起始日期，格式 YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "结束日期，格式 YYYY-MM-DD"}
            }
        }

        # 🌟 挂载全套 7 把带传参能力的扳手
        tools = [
            {"type": "function", "function": {"name": "get_recent_sales_orders", "description": "当用户询问销售订单时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_sales_invoices", "description": "当用户询问销售发票时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_receipts", "description": "当用户询问采购入库时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_delivery_notes", "description": "当用户询问销售出库时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_supplier_quotations", "description": "当用户询问供应商报价时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_orders", "description": "当用户询问采购订单时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_invoices", "description": "当用户询问采购发票时调用。可按需提取日期或数量。", "parameters": common_parameters}}
        ]

        # 🌟 极其心机的时间注入，让大模型知道今天是哪一天
        current_date = frappe.utils.nowdate()
        messages = [
            {"role": "system", "content": f"你是一个极其专业的企业级 ERPNext 智能业务助手。当前系统日期是 {current_date}。如果用户询问特定时间段（如本月、上个月、今年）的数据，请极其聪明地推算出具体的 start_date 和 end_date 并传给工具。输出结果务必用漂亮的 Markdown 排版，并保留超链接。"},
            {"role": "user", "content": message}
        ]
        
        payload = { "model": model_id, "messages": messages, "tools": tools, "tool_choice": "auto" }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        result_json = response.json()
        response_message = result_json["choices"][0]["message"]

        # =========================================================
        # 🧠 极其强悍的“七路拦截”且支持动态传参的路由中心
        # =========================================================
        if response_message.get("tool_calls"):
            tool_call = response_message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]
            
            # 💡 极其安全地解析 AI 传过来的参数
            try:
                args = json.loads(tool_call["function"].get("arguments", "{}"))
            except:
                args = {}
                
            req_limit = args.get("limit", 5)
            req_start = args.get("start_date")
            req_end = args.get("end_date")
            
            valid_functions = [
                "get_recent_sales_orders", "get_recent_sales_invoices", 
                "get_recent_purchase_receipts", "get_recent_delivery_notes",
                "get_recent_supplier_quotations", "get_recent_purchase_orders", "get_recent_purchase_invoices"
            ]
            
            if function_name in valid_functions:
                
                # 极其智能地把参数透传给底层函数
                if function_name == "get_recent_sales_orders":
                    tool_result, btn_label, file_prefix = get_recent_sales_orders(req_limit, req_start, req_end), "📊 导出完整订单明细 (Excel)", "ERPNext销售订单导出"
                elif function_name == "get_recent_sales_invoices":
                    tool_result, btn_label, file_prefix = get_recent_sales_invoices(req_limit, req_start, req_end), "📊 导出完整发票明细 (Excel)", "ERPNext销售发票导出"
                elif function_name == "get_recent_purchase_receipts":
                    tool_result, btn_label, file_prefix = get_recent_purchase_receipts(req_limit, req_start, req_end), "📥 导出采购入库明细 (Excel)", "ERPNext采购入库导出"
                elif function_name == "get_recent_delivery_notes":
                    tool_result, btn_label, file_prefix = get_recent_delivery_notes(req_limit, req_start, req_end), "🚚 导出销售出库明细 (Excel)", "ERPNext销售出库导出"
                elif function_name == "get_recent_supplier_quotations":
                    tool_result, btn_label, file_prefix = get_recent_supplier_quotations(req_limit, req_start, req_end), "📝 导出供应商报价明细 (Excel)", "ERPNext供应商报价导出"
                elif function_name == "get_recent_purchase_orders":
                    tool_result, btn_label, file_prefix = get_recent_purchase_orders(req_limit, req_start, req_end), "🛍️ 导出采购订单明细 (Excel)", "ERPNext采购订单导出"
                elif function_name == "get_recent_purchase_invoices":
                    tool_result, btn_label, file_prefix = get_recent_purchase_invoices(req_limit, req_start, req_end), "🧾 导出采购发票明细 (Excel)", "ERPNext采购发票导出"
                
                messages.append(response_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": function_name,
                    "content": tool_result["text"]
                })
                
                payload["messages"] = messages
                payload.pop("tools", None)
                payload.pop("tool_choice", None)
                
                second_response = requests.post(url, headers=headers, json=payload, timeout=30)
                second_response.raise_for_status()
                final_reply = second_response.json()["choices"][0]["message"]["content"]
                
                return {
                    "status": "success",
                    "reply": final_reply,
                    "action_button": {
                        "type": "export_excel",
                        "label": btn_label,
                        "data": tool_result["data"],
                        "file_prefix": file_prefix 
                    },
                    "logs": [
                        "后端 Python 接口触发成功！",
                        f"大模型极其聪明地调用了带有参数的工具：{function_name}。",
                        f"解析参数: limit={req_limit}, start_date={req_start}, end_date={req_end}",
                        "已成功抓取底层数据库真实账本！",
                        "已为您生成结构化 Excel 数据映射表与极其丝滑的跳转链接！"
                    ]
                }

        ai_reply = response_message.get("content")
        return {
            "status": "success",
            "reply": ai_reply,
            "logs": ["后端 Python 接口触发成功！", "大模型未触发数据库查询，已获取常规智能回复！"]
        }

    except Exception as e:
        error_msg = str(e)
        frappe.logger().error(f"AI API 请求失败: {error_msg}")
        return {
            "status": "success",
            "reply": f"⚠️ 报告老板，连接大脑时发生异常：<br><br><b>{error_msg}</b>",
            "logs": ["发生网络或认证异常！请排查。"]
        }